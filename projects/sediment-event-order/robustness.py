#!/usr/bin/env python3
"""Development-only robustness extension; frozen paired sources stay untouched."""
from __future__ import annotations

import argparse
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import time

import paired_experiment as paired
import paired_protocol_check as frozen
from material_model import draw_sample

VERSION = 'robustness-development-v1'
CASES = ('baseline', 'simultaneous', 'mixing-x2', 'finite-layer-40',
         'differential-offset-75')
METHODS = ('paired-exponential', 'gaussian-material')


def development_protocol():
    """Descriptive development plan, explicitly not a held-out registration."""
    return {'version': VERSION, 'held_out_authorized': False,
            'allowed_namespaces': ['development', 'contract-test'],
            'allowed_indices': [0, 999], 'base_protocol_sha256': frozen.PROTOCOL_SHA256,
            'target': paired.protocol()['target'],
            'cases': {'baseline': {}, 'simultaneous': {'events': 'tau_B=tau_A'},
                      'mixing-x2': {'true_mixing_multiplier': 2},
                      'finite-layer-40': {'material_uniform_half_width_years': 40},
                      'differential-offset-75': {'additional_archive_date_offsets_years': [-75, 75]}},
            'methods': {'paired-exponential': 'unchanged paired-v1 inference',
                        'gaussian-material': 'A~Normal(path(z),h^2); exact shared-specimen conditional proxy law'},
            'comparator_priors': 'same as paired-v1, including ONE common calibration offset',
            'pairing': 'common index across cases, designs and methods; posterior event rows stay joint',
            'thresholds': {'minimum_batch_ess': 100, 'maximum_mean_disagreement_mcse': 3,
                           'maximum_endpoint_cdf_disagreement': .05,
                           'maximum_order_probability_disagreement': .05},
            'reporting': {'interval_mass': .90, 'directional_declaration_probability': .95,
                          'failed_and_missing_in_requested_denominator': True,
                          'retries': False},
            'limits': {'indices_per_call': 4, 'particles_per_fit': [1000, 50000],
                       'fit_seconds': 20, 'batch_seconds': 600}}


def development_only(namespace, index):
    # No prospective held-out extension has yet been registered.
    if namespace not in ('development', 'contract-test') or type(index) is not int or not 0 <= index < 1000:
        raise ValueError('only development/contract-test indices 0..999 permitted')


def generate(case, namespace='development', index=0, scenario='balanced'):
    """Same ancestry and random roles as paired.generate, with explicit departures.

    Baseline is byte-equivalent. All designs/cases at an index share chronology,
    baseline events, calibration and random streams; simultaneity replaces B's
    event by A's. Truth remains exclusively in the labelled oracle.
    """
    development_only(namespace, index)
    if case not in CASES or scenario not in paired.SCENARIOS:
        raise ValueError('unknown case or design')
    draw = paired.prior_draw(paired.stream(namespace, index, 'truth'))
    if case == 'simultaneous':
        draw = replace(draw, events=(draw.events[0], draw.events[0]))
    if case == 'mixing-x2':
        draw = replace(draw, mixing=tuple(2*h for h in draw.mixing))
    p, d, overlap = paired.SCENARIOS[scenario]
    archives, ages = [], []
    for a in range(2):
        layers = []
        for z, depth in enumerate(paired.DEPTHS):
            sample = draw_sample(depth_cm=depth, focal=draw.paths[a].age_at(depth),
                event=draw.events[a], mixing=draw.mixing[a],
                half_width=40. if case == 'finite-layer-40' else 0.,
                proxy_count=p, date_count=d, overlap=overlap, dating_sigma=paired.DATE_SD,
                age_rng=paired.stream(namespace, index, f'material/{a}/{z}'),
                proxy_rng=paired.stream(namespace, index, f'proxy/{a}/{z}'),
                date_rng=paired.stream(namespace, index, f'date/{a}/{z}'), prefix=f'a{a}:z{z}')
            layer = sample.observed()
            for row in layer['date_measurements']:
                row['measured_age'] += draw.calibration + (
                    (-75. if a == 0 else 75.) if case == 'differential-offset-75' else 0.)
            layers.append(layer)
            ages.extend((s.identifier, s.true_age) for s in sample.specimens)
        archives.append(layers)
    observation = paired.PublicObservation.from_dict(
        {'version': paired.VERSION, 'scenario': scenario, 'archives': archives})
    return observation, paired.OracleEvaluation('ORACLE ONLY: robustness generating truth', draw, tuple(ages))


def normal_logpdf(x, mean, variance):
    return -.5*(math.log(2*math.pi*variance)+(x-mean)**2/variance)


def positive_probability(event, mean, variance):
    fraction = (.5*math.erfc((mean-event)/math.sqrt(2*variance)) if variance > 0
                else float(mean <= event))
    return .1 + .8*fraction


def gaussian_layer_log_likelihood(layer, *, focal, event, mixing, calibration):
    """A~N(focal,h²); D|A,c~N(A+c,s²); shared P and D integrate ONE A."""
    dates = {r['specimen_id']: r['measured_age']-calibration
             for r in layer['date_measurements']}
    h2, s2 = mixing**2, layer['dating_sigma_years']**2
    total = math.fsum(normal_logpdf(d, focal, h2+s2) for d in dates.values())
    for proxy in layer['proxy_measurements']:
        date = dates.get(proxy['specimen_id'])
        mean, variance = focal, h2
        if date is not None:
            mean = focal + h2/(h2+s2)*(date-focal)
            variance = h2*s2/(h2+s2)
        probability = positive_probability(event, mean, variance)
        total += math.log(probability if proxy['positive'] else 1-probability)
    return total


def gaussian_log_likelihood(observation, candidate):
    if type(observation) is not paired.PublicObservation or type(candidate) is not paired.JointDraw:
        raise ValueError('public observations and candidate draws required')
    return math.fsum(gaussian_layer_log_likelihood(layer,
        focal=candidate.paths[a].age_at(layer['depth_cm']), event=candidate.events[a],
        mixing=candidate.mixing[a], calibration=candidate.calibration)
        for a, layers in enumerate(observation.archives) for layer in layers)


def summarize_batches(batches):
    summaries = [paired.weighted_summary(rows) for rows in batches]
    ensemble = tuple(batches[0]+batches[1])
    pooled = paired.weighted_summary(ensemble)
    disagreement = abs(summaries[0]['delta_mean']-summaries[1]['delta_mean'])
    three_mcse = 3*math.hypot(*(s['delta_mcse'] for s in summaries))
    cdf = max(abs(paired.weighted_cdf(batches[0], x)-paired.weighted_cdf(batches[1], x))
              for x in pooled['delta_interval_90'])
    order = abs(summaries[0]['probability_tau_b_older_than_a']-
                summaries[1]['probability_tau_b_older_than_a'])
    passed = min(s['ess'] for s in summaries) >= 100 and disagreement <= three_mcse and cdf <= .05 and order <= .05
    return {'status': 'PASS_DIAGNOSTICS' if passed else 'FAILED_IMPORTANCE_DIAGNOSTICS',
            'posterior': pooled if passed else None, 'diagnostics': summaries,
            'mean_disagreement': disagreement, 'three_mcse': three_mcse,
            'endpoint_cdf_disagreement': cdf, 'order_probability_disagreement': order,
            **({'ensemble': ensemble} if passed else {})}


def infer_gaussian(observation, namespace='development', index=0, particles=12000, seconds=20.):
    development_only(namespace, index)
    if type(observation) is not paired.PublicObservation:
        raise ValueError('public observations required; oracle forbidden')
    paired.validate_public(observation.to_dict())
    if type(particles) is not int or not 1000 <= particles <= paired.MAX_PARTICLES or particles % 2:
        raise ValueError('even particle count 1000..50000 required')
    if not math.isfinite(seconds) or not 0 < seconds <= paired.MAX_SECONDS:
        raise ValueError('finite time budget in (0,20] required')
    start, batches = time.monotonic(), []
    for batch in range(2):
        rng = paired.stream(namespace, index, f'{VERSION}/gaussian-material/{batch}')
        rows = []
        for i in range(particles//2):
            if i % 32 == 0 and time.monotonic()-start > seconds:
                return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
            candidate = paired.prior_draw(rng)
            candidate, correction = paired.propose_chronology(observation, candidate, rng)
            candidate, event_correction = paired.propose_events(observation, candidate, rng)
            logw = gaussian_log_likelihood(observation, candidate)+correction+event_correction
            if not math.isfinite(logw):
                return {'status': 'FAILED_NONFINITE', 'posterior': None}
            rows.append((*candidate.events, logw))
        batches.append(rows)
    result = summarize_batches(batches)
    if time.monotonic()-start > seconds:
        return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
    return dict(result, particles=particles, elapsed_seconds=time.monotonic()-start)


def accounting(records, indices, cases):
    """Rectangular requested grid; reject duplicates/foreign keys, retain failures."""
    indices, cases = tuple(indices), tuple(cases)
    if len(set(indices)) != len(indices) or len(set(cases)) != len(cases):
        raise ValueError('duplicate requested index or case')
    expected = {(i, c, s, m) for i in indices for c in cases
                for s in paired.SCENARIOS for m in METHODS}
    seen = {}
    for row in records:
        key = tuple(row[k] for k in ('index', 'case', 'scenario', 'method'))
        if key not in expected or key in seen:
            raise ValueError('duplicate or unrequested record')
        seen[key] = row
    passed = sum(r['status'] == 'PASS_DIAGNOSTICS' for r in seen.values())
    strata = {}
    for case in cases:
        for scenario in paired.SCENARIOS:
            for method in METHODS:
                rows = [seen[i, case, scenario, method] for i in indices
                        if (i, case, scenario, method) in seen]
                passes = [r for r in rows if r['status'] == 'PASS_DIAGNOSTICS']
                declarations = [r for r in passes if r.get('wrong_order') is not None]
                strata[f'{case}/{scenario}/{method}'] = {
                    'requested': len(indices), 'attempted': len(rows),
                    'passed': len(passes), 'failed': len(rows)-len(passes),
                    'missing': len(indices)-len(rows),
                    'covered_among_passes': sum(r.get('covered') is True for r in passes),
                    'declarations': len(declarations),
                    'wrong_among_declarations': sum(r['wrong_order'] is True for r in declarations),
                    'unresolved_among_passes': len(passes)-len(declarations)}
    pairs = {}
    for case in cases:
        for method in METHODS:
            complete = [i for i in indices if all(
                (i, case, s, method) in seen and seen[i, case, s, method]['status'] == 'PASS_DIAGNOSTICS'
                for s in ('proxy-rich', 'date-rich'))]
            pairs[f'{case}/{method}'] = {'requested': len(indices), 'complete_indices': complete,
                                         'incomplete': len(indices)-len(complete)}
    method_pairs = {}
    for case in cases:
        for scenario in paired.SCENARIOS:
            complete = [i for i in indices if all(
                (i, case, scenario, method) in seen and seen[i, case, scenario, method]['status'] == 'PASS_DIAGNOSTICS'
                for method in METHODS)]
            method_pairs[f'{case}/{scenario}'] = {'requested': len(indices),
                'complete_indices': complete, 'incomplete': len(indices)-len(complete)}
    return {'requested': len(expected), 'attempted': len(seen), 'passed': passed,
            'failed': len(seen)-passed, 'missing': len(expected)-len(seen),
            'strata': strata, 'paired_budget_designs': pairs, 'paired_methods': method_pairs}


def benchmark(indices=(0,), cases=CASES, particles=12000, seconds=180.):
    indices, cases = tuple(indices), tuple(cases)
    if (not indices or len(indices) > 4 or len(set(indices)) != len(indices)
            or not cases or len(set(cases)) != len(cases) or any(c not in CASES for c in cases)):
        raise ValueError('one to four unique indices and unique known cases required')
    for i in indices:
        development_only('development', i)
    if type(particles) is not int or particles % 2 or not 1000 <= particles <= paired.MAX_PARTICLES:
        raise ValueError('even particles 1000..50000 required')
    if not math.isfinite(seconds) or not 0 < seconds <= 600:
        raise ValueError('batch budget in (0,600] required')
    frozen.validate_freeze()
    started, records = time.monotonic(), []
    for index in indices:
        for case in cases:
            for scenario in paired.SCENARIOS:
                if time.monotonic()-started >= seconds:
                    continue  # Explicit missing cell, never retried.
                observation, oracle = generate(case, index=index, scenario=scenario)
                for method in METHODS:
                    remaining = seconds-(time.monotonic()-started)
                    if remaining <= 0:
                        continue
                    try:
                        if method == 'paired-exponential':
                            result = paired.infer(observation, index=index, particles=particles,
                                seconds=min(20., remaining), retain_ensemble=True)
                        else:
                            result = infer_gaussian(observation, index=index, particles=particles,
                                                    seconds=min(20., remaining))
                        evaluation = paired.evaluate(result, oracle)
                        row = {'status': result['status'], **evaluation}
                        if result.get('diagnostics'):
                            row['minimum_batch_ess'] = min(r['ess'] for r in result['diagnostics'])
                    except (ArithmeticError, ValueError) as error:
                        row = {'status': 'FAILED_EXCEPTION', 'error': str(error)}
                    records.append(dict(row, index=index, case=case, scenario=scenario, method=method))
    source_files = ('robustness.py', 'test_robustness.py', 'paired_protocol_check.py')
    hashes = {name: hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() for name in source_files}
    return {'version': VERSION, 'namespace': 'development', 'held_out_executed': False,
            'development_protocol': development_protocol(),
            'indices': indices, 'cases': cases, 'particles_per_fit': particles,
            'wall_budget_seconds': seconds, 'elapsed_seconds': time.monotonic()-started,
            'source_sha256': dict(frozen.source_hashes(), **hashes),
            'base_protocol_sha256': frozen.PROTOCOL_SHA256,
            'runtime': paired.provenance(),
            'records': records, 'accounting': accounting(records, indices, cases)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', type=int, default=0)
    parser.add_argument('--particles', type=int, default=12000)
    parser.add_argument('--seconds', type=float, default=180.)
    parser.add_argument('--case', choices=CASES, action='append')
    args = parser.parse_args()
    print(json.dumps(benchmark((args.index,), args.case or CASES, args.particles, args.seconds), indent=2))


if __name__ == '__main__':
    main()
