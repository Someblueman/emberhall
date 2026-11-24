#!/usr/bin/env python3
"""Synthetic paired latent-event experiment; see PAIRED_EXPERIMENT.md."""
from __future__ import annotations

import argparse
import copy
from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import platform
import random
import time

from chronology_model import (ArchivePriorSpec, AgeDepthPath, simulate_gamma_increment_path,
                              _cholesky, _solve_spd_chol, _solve_upper_t)
from material_model import draw_sample, sample_log_likelihood
from change_point import Prior, segment_posterior
from baseline import Design, Observation, mixed_fraction, ks_uniform
from continuous import ContinuousInference, cdf_distance

VERSION = 'paired-v1'
SCENARIOS = {'balanced': (4, 4, 2), 'proxy-rich': (12, 2, 1),
             'date-rich': (2, 12, 1)}
DEPTHS = (0., 1., 2., 3.)
MIXING_PRIORS = ((25., 45., 65.), (45., 65., 85.))
DATE_SD = 100.
CAL_SD = 50.
MAX_PARTICLES = 50000
MAX_SECONDS = 20.
REGISTERED_PARTICLES = 50000
REGISTERED_TOTAL_SECONDS = 5400
EVENT_CELLS = 12
PRIOR_PROPOSAL_FRACTION = .2
# These namespaces are frozen before any fresh held-out evaluation.
NAMESPACES = ('development', 'contract-test', 'held-out')


def protocol():
    """Prospective contract, exported without generating or exposing truth."""
    return {'version': VERSION, 'target': 'tau_A, tau_B; delta=tau_B-tau_A in synthetic years',
            'event_prior': 'independent Uniform(850,1150)', 'mixing_priors': MIXING_PRIORS,
            'shared_calibration_sd': CAL_SD, 'independent_date_sd': DATE_SD,
            'depths': DEPTHS, 'scenarios_proxy_date_overlap': SCENARIOS,
            'held_out_indices': [1000, 1127], 'held_out_particles': REGISTERED_PARTICLES,
            'held_out_proposal': 'guided', 'max_particles': MAX_PARTICLES,
            'max_seconds_per_fit': MAX_SECONDS, 'max_seconds_per_batch': 60,
            'max_replicates_per_batch': 16, 'particle_storage_budget_mib': 32,
            'minimum_ess_each_batch': 100, 'maximum_mean_disagreement_in_combined_mcse': 3,
            'maximum_endpoint_cdf_disagreement': .05,
            'maximum_order_probability_disagreement': .05,
            'coverage_interval_mass': .90, 'order_declaration_probability': .95,
            'conditional_pit_groups': ['A_more_positive', 'A_not_more_positive'],
            'archive_priors': [archive_prior(a).to_dict() for a in range(2)],
            'event_proposal_cells': EVENT_CELLS, 'event_proposal_prior_fraction': PRIOR_PROPOSAL_FRACTION,
            'held_out_total_wall_budget_seconds': REGISTERED_TOTAL_SECONDS,
            'no_post_outcome_particle_increase': True}


def stream(namespace, index, role):
    if namespace not in NAMESPACES or type(index) is not int or not 0 <= index < 1000000:
        raise ValueError('valid namespace and replicate index required')
    if namespace == 'held-out' and not 1000 <= index <= 1127:
        raise ValueError('held-out v1 range is 1000..1127; lower indices retired')
    seed = hashlib.sha256(f'{VERSION}/{namespace}/{index}/{role}'.encode()).digest()
    return random.Random(int.from_bytes(seed, 'big'))


def archive_prior(index):
    return ArchivePriorSpec(str(index), DEPTHS, (), 1.5, 800., 35., 130., 40.)


@dataclass(frozen=True)
class JointDraw:
    paths: tuple
    events: tuple[float, float]
    calibration: float
    mixing: tuple[float, float]


def prior_draw(rng):
    # Independent event times on physical time, not depth or apparent boundaries.
    return JointDraw(tuple(simulate_gamma_increment_path(archive_prior(a), rng)
                           for a in range(2)),
                     (rng.uniform(850., 1150.), rng.uniform(850., 1150.)),
                     rng.gauss(0., CAL_SD),
                     tuple(rng.choice(values) for values in MIXING_PRIORS))


def specimen_ids(archive, layer, scenario):
    p, d, overlap = SCENARIOS[scenario]
    prefix = f'a{archive}:z{layer}'
    shared = [f'{prefix}:shared:{i}' for i in range(overlap)]
    return (shared + [f'{prefix}:proxy:{i}' for i in range(p-overlap)],
            shared + [f'{prefix}:date:{i}' for i in range(d-overlap)])


@dataclass(frozen=True)
class PublicObservation:
    """Only design and measurements cross the inference boundary."""
    scenario: str
    archives: tuple

    def __post_init__(self):
        validate_public({'version': VERSION, 'scenario': self.scenario, 'archives': self.archives})

    def to_dict(self):
        value = copy.deepcopy({'version': VERSION, 'scenario': self.scenario, 'archives': self.archives})
        validate_public(value)
        return value

    @classmethod
    def from_dict(cls, value):
        validate_public(value)
        return cls(value['scenario'], tuple(copy.deepcopy(value['archives'])))


@dataclass(frozen=True)
class OracleEvaluation:
    label: str
    latent_draw: JointDraw
    specimen_ages: tuple


def validate_public(value):
    if type(value) is not dict or set(value) != {'version', 'scenario', 'archives'}:
        raise ValueError('public allowlist forbids truth or unknown fields')
    if value['version'] != VERSION or type(value['scenario']) is not str or value['scenario'] not in SCENARIOS:
        raise ValueError('unknown frozen design')
    if type(value['archives']) not in (list, tuple) or len(value['archives']) != 2:
        raise ValueError('exactly two archives required')
    for a, layers in enumerate(value['archives']):
        if type(layers) not in (list, tuple) or len(layers) != len(DEPTHS):
            raise ValueError('wrong layer count')
        for z, layer in enumerate(layers):
            if type(layer) is not dict or set(layer) != {'depth_cm', 'dating_sigma_years', 'proxy_measurements', 'date_measurements'}:
                raise ValueError('layer allowlist forbids truth')
            if (type(layer['depth_cm']) not in (int, float) or layer['depth_cm'] != DEPTHS[z]
                    or layer['dating_sigma_years'] != DATE_SD):
                raise ValueError('changed design')
            for kind, ids in zip(('proxy', 'date'), specimen_ids(a, z, value['scenario'])):
                rows = layer[kind+'_measurements']
                field = 'positive' if kind == 'proxy' else 'measured_age'
                if (type(rows) not in (list, tuple) or len(rows) != len(ids)
                        or any(type(r) is not dict or set(r) != {'specimen_id', field} for r in rows)):
                    raise ValueError('measurement schema/count changed')
                if any(type(r['specimen_id']) is not str for r in rows):
                    raise ValueError('string specimen IDs required')
                if sorted(r['specimen_id'] for r in rows) != sorted(ids):
                    raise ValueError('specimen ancestry differs from frozen allocation')
                for r in rows:
                    x = r[field]
                    if (type(x) is not bool if kind == 'proxy' else
                            type(x) not in (int, float) or not math.isfinite(x)):
                        raise ValueError('invalid measurement')


def generate(namespace='development', index=0, scenario='balanced'):
    if scenario not in SCENARIOS:
        raise ValueError('unknown scenario')
    draw = prior_draw(stream(namespace, index, 'truth'))
    p, d, overlap = SCENARIOS[scenario]
    archives, ages = [], []
    for a in range(2):
        layers = []
        for z, depth in enumerate(DEPTHS):
            sample = draw_sample(depth_cm=depth, focal=draw.paths[a].age_at(depth),
                event=draw.events[a], mixing=draw.mixing[a], half_width=0., proxy_count=p,
                date_count=d, overlap=overlap, dating_sigma=DATE_SD,
                age_rng=stream(namespace, index, f'material/{a}/{z}'),
                proxy_rng=stream(namespace, index, f'proxy/{a}/{z}'),
                date_rng=stream(namespace, index, f'date/{a}/{z}'), prefix=f'a{a}:z{z}')
            layer = sample.observed()
            for row in layer['date_measurements']:
                row['measured_age'] += draw.calibration
            layers.append(layer)
            ages.extend((s.identifier, s.true_age) for s in sample.specimens)
        archives.append(layers)
    public = PublicObservation.from_dict({'version': VERSION, 'scenario': scenario,
                                          'archives': archives})
    return public, OracleEvaluation('ORACLE ONLY: never an inference input', draw, tuple(ages))


def joint_log_likelihood(observation, candidate, *, independent_offsets=None):
    """Conditional joint law; ONE offset is used by both archive likelihoods.

    independent_offsets is an explicitly wrong calibration control, never default.
    Material ages are integrated analytically by the foundation likelihood.
    """
    if type(observation) is not PublicObservation or type(candidate) is not JointDraw:
        raise ValueError('public observations and explicit candidate draws required')
    total = 0.
    for a, layers in enumerate(observation.archives):
        offset = candidate.calibration if independent_offsets is None else independent_offsets[a]
        for layer in layers:
            shifted = dict(layer, date_measurements=[dict(r, measured_age=r['measured_age']-offset)
                                                     for r in layer['date_measurements']])
            total += sample_log_likelihood(shifted, focal=candidate.paths[a].age_at(layer['depth_cm']),
                event=candidate.events[a], mixing=candidate.mixing[a], half_width=0.)
    return total


def event_proposal(layers, path, mixing):
    """Piecewise-uniform proxy-only proposal, NOT an approximate target law.

    A 20% prior mixture gives full physical-time support. The exact joint
    date/proxy likelihood and proposal density correct every sampled event.
    """
    logs = []
    for i in range(EVENT_CELLS):
        tau = 850.+(i+.5)*300./EVENT_CELLS
        total = 0.
        for layer in layers:
            p = .1+.8*mixed_fraction(path.age_at(layer['depth_cm']), tau, mixing)
            positives = sum(r['positive'] for r in layer['proxy_measurements'])
            n = len(layer['proxy_measurements'])
            total += positives*math.log(p)+(n-positives)*math.log1p(-p)
        logs.append(total)
    peak = max(logs)
    values = [math.exp(x-peak) for x in logs]
    total = math.fsum(values)
    return tuple((1-PRIOR_PROPOSAL_FRACTION)*v/total + PRIOR_PROPOSAL_FRACTION/EVENT_CELLS
                 for v in values)


def propose_events(observation, candidate, rng):
    events, log_correction = [], 0.
    for a, layers in enumerate(observation.archives):
        masses = event_proposal(layers, candidate.paths[a], candidate.mixing[a])
        u = rng.random()
        cell, cumulative = len(masses)-1, 0.
        for i, mass in enumerate(masses):
            cumulative += mass
            if u < cumulative:
                cell = i
                break
        events.append(850.+(cell+rng.random())*300./EVENT_CELLS)
        # p(tau)/q(tau) = (1/300)/(mass/(300/EVENT_CELLS)).
        log_correction -= math.log(masses[cell]*EVENT_CELLS)
    return replace(candidate, events=tuple(events)), log_correction


def propose_chronology(observation, candidate, rng):
    """Joint Gaussian working proposal for (surface A, surface B, shared c).

    Gamma increments and mixing stay drawn from their exact priors. Date means
    guide this proposal only; the exponentially modified individual-date law
    remains the target. The normal prior/proposal density ratio is exact.
    """
    prior_means = (800., 800., 0.)
    prior_precisions = (1/35.**2, 1/35.**2, 1/CAL_SD**2)
    precision = [[prior_precisions[i] if i == j else 0. for j in range(3)] for i in range(3)]
    canonical = [p*m for p, m in zip(prior_precisions, prior_means)]
    for a, layers in enumerate(observation.archives):
        path = candidate.paths[a]
        for layer in layers:
            dates = layer['date_measurements']
            increment = path.age_at(layer['depth_cm'])-path.node_ages[0]
            residual = math.fsum(r['measured_age'] for r in dates)/len(dates)-increment
            weight = len(dates)/(DATE_SD**2+candidate.mixing[a]**2)
            for i in (a, 2):
                canonical[i] += weight*residual
                for j in (a, 2):
                    precision[i][j] += weight
    chol = _cholesky(precision)
    mean = _solve_spd_chol(chol, canonical)
    noise = _solve_upper_t(chol, [rng.gauss(0., 1.) for _ in range(3)])
    values = [m+z for m, z in zip(mean, noise)]
    prior_quadratic = math.fsum(p*(x-m)**2 for p, x, m in zip(prior_precisions, values, prior_means))
    centered = [x-m for x, m in zip(values, mean)]
    proposal_quadratic = math.fsum(centered[i]*precision[i][j]*centered[j]
                                  for i in range(3) for j in range(3))
    log_correction = (.5*math.fsum(math.log(p) for p in prior_precisions)
                      -math.fsum(math.log(chol[i][i]) for i in range(3))
                      +.5*(proposal_quadratic-prior_quadratic))
    paths = tuple(AgeDepthPath(path.node_depths,
        tuple(age-path.node_ages[0]+values[a] for age in path.node_ages))
        for a, path in enumerate(candidate.paths))
    return replace(candidate, paths=paths, calibration=values[2]), log_correction


def weighted_summary(rows):
    peak = max(row[2] for row in rows)
    if not math.isfinite(peak):
        raise ArithmeticError('no finite importance weights')
    weights = [math.exp(row[2]-peak) for row in rows]
    norm = math.fsum(weights)
    weights = [w/norm for w in weights]
    delta = [b-a for a, b, _ in rows]
    mean = math.fsum(w*x for w, x in zip(weights, delta))
    variance = math.fsum(w*(x-mean)**2 for w, x in zip(weights, delta))
    ess = 1/math.fsum(w*w for w in weights)
    # Self-normalized importance sampling CLT standard error, not posterior SD.
    mcse = math.sqrt(math.fsum(w*w*(x-mean)**2 for w, x in zip(weights, delta)))
    ordered = sorted(zip(delta, weights))
    def quantile(q):
        cumulative = 0.
        for x, w in ordered:
            cumulative += w
            if cumulative >= q:
                return x
        return ordered[-1][0]
    tau_means = [math.fsum(w*row[a] for w, row in zip(weights, rows)) for a in range(2)]
    covariance = math.fsum(w*(row[0]-tau_means[0])*(row[1]-tau_means[1])
                           for w, row in zip(weights, rows))
    order_probability = math.fsum(w for w, x in zip(weights, delta) if x > 0)
    order_mcse = math.sqrt(math.fsum(w*w*((x > 0)-order_probability)**2
                                     for w, x in zip(weights, delta)))
    return {'ess': ess, 'tau_means': tau_means, 'tau_covariance': covariance,
            'probability_tau_b_after_a': order_probability, 'order_probability_mcse': order_mcse,
            'delta_mean': mean, 'delta_sd': math.sqrt(variance),
            'delta_mcse': mcse, 'delta_interval_90': [quantile(.05), quantile(.95)]}


def weighted_cdf(rows, target):
    peak = max(row[2] for row in rows)
    weights = [math.exp(row[2]-peak) for row in rows]
    total = math.fsum(weights)
    return math.fsum(w for (a, b, _), w in zip(rows, weights) if b-a <= target)/total


def infer(observation, namespace='development', index=0, particles=12000, seconds=MAX_SECONDS,
          proposal='guided', *, retain_ensemble=False):
    if type(observation) is not PublicObservation:
        raise ValueError('oracle/dict inference input forbidden')
    validate_public(observation.to_dict())
    if type(particles) is not int or not 1000 <= particles <= MAX_PARTICLES:
        raise ValueError('1000..50000 particles required')
    if not 0 < seconds <= MAX_SECONDS:
        raise ValueError('time budget must be at most 20 seconds')
    if proposal not in ('prior', 'proxy-grid', 'guided'):
        raise ValueError('unknown importance proposal')
    if namespace == 'held-out' and (particles != REGISTERED_PARTICLES or proposal != 'guided'):
        raise ValueError('held-out v1 freezes 50000 particles and guided proposal')
    started = time.monotonic()
    batches = []
    for batch in range(2):
        rng = stream(namespace, index, f'inference/{batch}')
        rows = []
        for i in range(particles//2):
            if i % 32 == 0 and time.monotonic()-started > seconds:
                return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
            candidate = prior_draw(rng)
            correction = 0.
            if proposal == 'guided':
                candidate, correction = propose_chronology(observation, candidate, rng)
            if proposal in ('proxy-grid', 'guided'):
                candidate, event_correction = propose_events(observation, candidate, rng)
                correction += event_correction
            logw = joint_log_likelihood(observation, candidate)+correction
            if not math.isfinite(logw):
                return {'status': 'FAILED_NONFINITE', 'posterior': None}
            rows.append((*candidate.events, logw))
        batches.append(rows)
    summaries = [weighted_summary(rows) for rows in batches]
    pooled = weighted_summary(batches[0]+batches[1])
    error = math.hypot(*(s['delta_mcse'] for s in summaries))
    disagreement = abs(summaries[0]['delta_mean']-summaries[1]['delta_mean'])
    # A mean can agree while the tails disagree. Check CDFs at pooled endpoints.
    cdf_disagreement = max(abs(weighted_cdf(batches[0], x)-weighted_cdf(batches[1], x))
                           for x in pooled['delta_interval_90'])
    order_disagreement = abs(summaries[0]['probability_tau_b_after_a']-
                             summaries[1]['probability_tau_b_after_a'])
    passed = (min(s['ess'] for s in summaries) >= 100 and disagreement <= 3*error
              and cdf_disagreement <= .05 and order_disagreement <= .05)
    if time.monotonic()-started > seconds:
        return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
    result = {'status': 'PASS_DIAGNOSTICS' if passed else 'FAILED_IMPORTANCE_DIAGNOSTICS',
            'posterior': pooled if passed else None, 'diagnostics': summaries,
            'mean_disagreement': disagreement, 'three_mcse': 3*error,
            'endpoint_cdf_disagreement': cdf_disagreement,
            'order_probability_disagreement': order_disagreement,
            'proposal': proposal,
            'particles': 2*(particles//2), 'elapsed_seconds': time.monotonic()-started}
    if retain_ensemble and passed:
        result['ensemble'] = tuple(batches[0]+batches[1])
    return result


def gaussian_control(observation):
    """Working-model boundaries in DEPTH; never renamed latent event times."""
    validate_public(observation.to_dict())
    results = []
    for layers in observation.archives:
        y = [sum(r['positive'] for r in layer['proxy_measurements']) /
             len(layer['proxy_measurements']) for layer in layers]
        fit = segment_posterior(DEPTHS, y, Prior(min_length=1, max_changes=1))
        results.append({'count_probabilities': fit.count_probabilities,
                        'depth_gap_probabilities_given_one_break': fit.one_change_probabilities})
    return {'label': 'Gaussian working model in depth; not historical Khider reproduction; not tau',
            'archives': results}


def fixed_chronology_control(observation):
    """Proxy-only sensitivity control, with fixed PRIOR MEAN ages, never truth."""
    validate_public(observation.to_dict())
    results = []
    for a, layers in enumerate(observation.archives):
        ages = tuple(800.+130.*z for z in DEPTHS)
        count = len(layers[0]['proxy_measurements'])
        design = Design(events=(1000.,), mixing_times=MIXING_PRIORS[a],
                        focal_ages=ages, specimens=count)
        obs = Observation(ages, count, tuple(sum(r['positive'] for r in layer['proxy_measurements'])
                                            for layer in layers))
        coarse = ContinuousInference(design, .5, 850., 1150.).fit(obs)
        fine = ContinuousInference(design, .25, 850., 1150.).fit(obs)
        distance = cdf_distance(coarse, fine)
        results.append({'tau_interval_90': [fine.quantile(.05), fine.quantile(.95)],
                        'cdf_refinement_distance': distance,
                        'numerical_status': 'PASS' if distance <= .002 else 'FAILED_REFINEMENT'})
    return {'label': 'Proxy-only; fixed prior-mean chronology; ignores dates; not joint inference',
            'archives': results}


def evaluate(result, oracle):
    """Truth enters here only AFTER fitting; failures remain in the denominator."""
    if type(oracle) is not OracleEvaluation:
        raise ValueError('explicitly labelled oracle required for evaluation')
    posterior = result['posterior']
    if posterior is None:
        return {'covered': None, 'squared_error': None, 'order': 'numerical failure',
                'wrong_order': None, 'predicted_order_error': None, 'approximate_pit': None,
                'interval_width': None, 'order_probability': None}
    delta = oracle.latent_draw.events[1]-oracle.latent_draw.events[0]
    lo, hi = posterior['delta_interval_90']
    probability = posterior['probability_tau_b_after_a']
    order = 'A before B' if probability >= .95 else 'B before A' if probability <= .05 else 'unresolved'
    wrong = (delta <= 0 if order == 'A before B' else delta >= 0) if order != 'unresolved' else None
    return {'covered': lo <= delta <= hi, 'squared_error': (posterior['delta_mean']-delta)**2,
            'order': order, 'wrong_order': wrong,
            'predicted_order_error': min(probability, 1-probability) if wrong is not None else None,
            'interval_width': hi-lo, 'order_probability': probability,
            'approximate_pit': weighted_cdf(result['ensemble'], delta) if 'ensemble' in result else None}


def prior_only_control(observation, namespace, index, particles):
    """Deliberately defective inference: useful marginal calibration trap."""
    validate_public(observation.to_dict())
    if type(particles) is not int or not 1000 <= particles <= MAX_PARTICLES:
        raise ValueError('1000..50000 particles required')
    if namespace == 'held-out' and particles != REGISTERED_PARTICLES:
        raise ValueError('held-out control must use the registered particle budget')
    rng = stream(namespace, index, 'prior-only-control')
    rows = tuple((rng.uniform(850., 1150.), rng.uniform(850., 1150.), 0.)
                 for _ in range(particles))
    return {'status': 'CONTROL_PRIOR_ONLY', 'posterior': weighted_summary(rows), 'ensemble': rows}


def observed_group(observation):
    # Conditioning uses observations only. The threshold is frozen before holdout.
    counts = [sum(r['positive'] for layer in layers for r in layer['proxy_measurements'])
              for layers in observation.archives]
    return 'A_more_positive' if counts[0] > counts[1] else 'A_not_more_positive'


def provenance():
    directory = Path(__file__).resolve().parent
    files = ('paired_experiment.py', 'material_model.py', 'chronology_model.py',
             'baseline.py', 'continuous.py', 'change_point.py')
    return {'protocol_sha256': hashlib.sha256(json.dumps(protocol(), sort_keys=True).encode()).hexdigest(),
            'source_sha256': {name: hashlib.sha256((directory/name).read_bytes()).hexdigest()
                              for name in files}, 'python': platform.python_version()}


def benchmark(namespace, first_index, replicates, scenario, particles=12000, proposal='guided',
              control='none'):
    """Bounded own-law calibration harness; a development run is not held-out proof."""
    if type(replicates) is not int or not 1 <= replicates <= 16:
        raise ValueError('1..16 replicates per bounded invocation')
    if type(first_index) is not int or first_index+replicates > 1000000:
        raise ValueError('replicate index range exceeded')
    if control not in ('none', 'prior-only'):
        raise ValueError('unknown benchmark control')
    if namespace == 'held-out' and (particles != REGISTERED_PARTICLES or proposal != 'guided'):
        raise ValueError('held-out v1 requires the registered particle budget and proposal')
    # Validate the full requested range before drawing even the first case.
    stream(namespace, first_index, 'validate')
    stream(namespace, first_index+replicates-1, 'validate')
    signature = provenance()
    started = time.monotonic()
    records = []
    for index in range(first_index, first_index+replicates):
        remaining = 60.-(time.monotonic()-started)
        if remaining <= 0:
            break
        public, oracle = generate(namespace, index, scenario)
        result = (infer(public, namespace, index, particles, seconds=min(remaining, MAX_SECONDS),
                        proposal=proposal, retain_ensemble=True) if control == 'none' else
                  prior_only_control(public, namespace, index, particles))
        diagnostics = result.get('diagnostics', [])
        records.append({'index': index, 'status': result['status'], 'observed_group': observed_group(public),
                        **evaluate(result, oracle),
                        'minimum_batch_ess': min((d['ess'] for d in diagnostics), default=None),
                        'endpoint_cdf_disagreement': result.get('endpoint_cdf_disagreement')})
    passed = [r for r in records if r['covered'] is not None]
    covered = sum(r['covered'] for r in passed)
    declared = [r for r in records if r['wrong_order'] is not None]
    pits = [r['approximate_pit'] for r in passed if r['approximate_pit'] is not None]
    conditional = {}
    for group in ('A_more_positive', 'A_not_more_positive'):
        values = [r['approximate_pit'] for r in passed if r['observed_group'] == group
                  and r['approximate_pit'] is not None]
        conditional[group] = {'count': len(values), 'ks': ks_uniform(values) if values else None}
    return {'namespace': namespace, 'scenario': scenario, 'proposal': proposal, 'control': control,
            'first_index': first_index, 'particles': particles, 'provenance': signature,
            'source_changed_during_batch': signature != provenance(),
            'requested': replicates,
            'attempted': len(records), 'evaluated_posteriors': len(passed),
            'diagnostic_passes': sum(r['status'] == 'PASS_DIAGNOSTICS' for r in records), 'covered': covered,
            'coverage_among_passes': covered/len(passed) if passed else None,
            'covered_fraction_all_requested': covered/replicates,
            'declared_orders': len(declared), 'wrong_orders': sum(r['wrong_order'] for r in declared),
            'unresolved_posteriors': sum(r['order'] == 'unresolved' for r in passed),
            'predicted_order_errors': math.fsum(r['predicted_order_error'] for r in declared),
            'approximate_pit_ks': ks_uniform(pits) if pits else None, 'conditional_pit': conditional,
            'warning': 'Pass-only coverage is selected; failures and unattempted cases are unresolved.',
            'records': records, 'elapsed_seconds': time.monotonic()-started}


def aggregate_registered(reports):
    """Reconcile partial registered chunks without retries, duplicates or silent loss.

    This is result accounting, not an authenticity or adversarial security claim.
    Missing cases remain explicit; a changed source/contract cannot be pooled.
    """
    if not reports:
        raise ValueError('at least one registered report required')
    expected_signature = provenance()
    rows, charged_seconds = {}, 0.
    for report in reports:
        if (report['namespace'] != 'held-out' or report['control'] != 'none'
                or report['proposal'] != 'guided' or report['particles'] != REGISTERED_PARTICLES
                or report['provenance'] != expected_signature or report['source_changed_during_batch']):
            raise ValueError('cannot pool development, controls, changed source or unregistered settings')
        scenario = report['scenario']
        if scenario not in SCENARIOS:
            raise ValueError('unknown registered scenario')
        records = report['records']
        if (report['attempted'] != len(records) or not 1 <= report['requested'] <= 16
                or len(records) > report['requested']):
            raise ValueError('batch counts are inconsistent')
        requested = range(report['first_index'], report['first_index']+report['requested'])
        if not all(1000 <= i <= 1127 for i in requested):
            raise ValueError('unregistered indices')
        if [r['index'] for r in records] != list(requested)[:len(records)]:
            raise ValueError('batch records must be the contiguous attempted prefix')
        if any(type(r['index']) is not int for r in records):
            raise ValueError('integer replicate indices required')
        elapsed = report['elapsed_seconds']
        if not math.isfinite(elapsed) or elapsed < 0:
            raise ValueError('finite nonnegative charged time required')
        charged_seconds += elapsed
        for row in records:
            key = (scenario, row['index'])
            if key in rows:
                raise ValueError('duplicate attempted case: cannot retry or double-count')
            passed = row['status'] == 'PASS_DIAGNOSTICS'
            if (not passed and not row['status'].startswith('FAILED_')):
                raise ValueError('unexpected algorithm status')
            if passed:
                if (type(row['covered']) is not bool or row['approximate_pit'] is None
                        or not 0 <= row['approximate_pit'] <= 1):
                    raise ValueError('successful case requires coverage and a finite PIT')
            elif row['covered'] is not None or row['approximate_pit'] is not None:
                raise ValueError('failed cases cannot carry successful posterior evaluations')
            rows[key] = row
    summaries = {}
    for scenario in SCENARIOS:
        records = [rows[(scenario, i)] for i in range(1000, 1128) if (scenario, i) in rows]
        passed = [r for r in records if r['status'] == 'PASS_DIAGNOSTICS']
        pits = [r['approximate_pit'] for r in passed]
        declared = [r for r in passed if r['wrong_order'] is not None]
        conditional = {}
        for group in ('A_more_positive', 'A_not_more_positive'):
            values = [r['approximate_pit'] for r in passed if r['observed_group'] == group]
            conditional[group] = {'count': len(values), 'ks': ks_uniform(values) if values else None}
        summaries[scenario] = {
            'requested': 128, 'attempted': len(records), 'diagnostic_passes': len(passed),
            'numerical_failures': len(records)-len(passed),
            'missing_indices': [i for i in range(1000, 1128) if (scenario, i) not in rows],
            'covered': sum(r['covered'] for r in passed),
            'coverage_among_passes': sum(r['covered'] for r in passed)/len(passed) if passed else None,
            'approximate_pit_ks': ks_uniform(pits) if pits else None,
            'conditional_pit': conditional,
            'mean_interval_width': math.fsum(r['interval_width'] for r in passed)/len(passed) if passed else None,
            'unresolved_posteriors': sum(r['order'] == 'unresolved' for r in passed),
            'predicted_order_errors': math.fsum(r['predicted_order_error'] for r in declared),
            'declared_orders': len(declared), 'wrong_orders': sum(r['wrong_order'] for r in declared)}
    complete = len(rows) == 3*128
    within_budget = charged_seconds <= REGISTERED_TOTAL_SECONDS
    return {'status': 'COMPLETE_ACCOUNTING' if complete and within_budget else
            'FAILED_TOTAL_BUDGET' if not within_budget else 'INCOMPLETE',
            'charged_seconds': charged_seconds, 'provenance': expected_signature,
            'numerically_complete': complete and within_budget and
                                    all(r['status'] == 'PASS_DIAGNOSTICS' for r in rows.values()),
            'scenarios': summaries,
            'warning': 'Accounting is not a scientific conclusion. Failure-selected calibration remains descriptive.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--scenario', choices=SCENARIOS, default='balanced')
    parser.add_argument('--namespace', choices=NAMESPACES, default='development')
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--particles', type=int, default=12000)
    parser.add_argument('--proposal', choices=('prior', 'proxy-grid', 'guided'), default='guided')
    parser.add_argument('--replicates', type=int, default=1,
                        help='2..16 runs invoke the bounded calibration harness')
    parser.add_argument('--protocol', action='store_true', help='print the prospective contract without draws')
    parser.add_argument('--control', choices=('none', 'prior-only'), default='none',
                        help='deliberately defective prior-only control for the benchmark')
    parser.add_argument('--summarize', nargs='+', metavar='JSON',
                        help='reconcile registered batch files without running inference')
    args = parser.parse_args()
    if args.summarize:
        reports = [json.loads(Path(name).read_text()) for name in args.summarize]
        print(json.dumps(aggregate_registered(reports), indent=2))
        return
    if args.protocol:
        print(json.dumps(protocol(), indent=2))
        return
    if args.namespace == 'held-out' and (args.particles != REGISTERED_PARTICLES or args.proposal != 'guided'):
        parser.error('held-out v1 requires --particles 50000 and --proposal guided')
    if args.replicates != 1:
        print(json.dumps(benchmark(args.namespace, args.index, args.replicates,
                                   args.scenario, args.particles, args.proposal, args.control), indent=2))
        return
    observation, oracle = generate(args.namespace, args.index, args.scenario)
    result = (infer(observation, args.namespace, args.index, args.particles, proposal=args.proposal)
              if args.control == 'none' else
              prior_only_control(observation, args.namespace, args.index, args.particles))
    result.pop('ensemble', None)
    print(json.dumps({'version': VERSION, 'provenance': provenance(),
        'namespace': args.namespace, 'index': args.index,
        'scenario': args.scenario, 'scope': 'synthetic model only; no held-out aggregate claim',
        'inference': result, 'gaussian_control': gaussian_control(observation),
        'fixed_chronology_control': fixed_chronology_control(observation),
        'oracle_evaluation': {'label': oracle.label, 'tau': oracle.latent_draw.events,
                             'delta': oracle.latent_draw.events[1]-oracle.latent_draw.events[0]}}, indent=2))


if __name__ == '__main__':
    main()
