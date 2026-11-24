#!/usr/bin/env python3
"""Prospectively registered synthetic held-out comparison; standard library only."""
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
import robustness as robust
from material_model import draw_sample

DIRECTORY = Path(__file__).resolve().parent
VERSION = 'heldout-robustness-v1'
# Keep the comparator's original random role, including its development version.
GAUSSIAN_VERSION = robust.VERSION
CASES, METHODS = robust.CASES, robust.METHODS
FIRST, LAST = 1000, 1127
PARTICLES, FIT_SECONDS, INDEX_SECONDS = 50000, 20., 600.
PIN_FILES = tuple(frozen.PINS) + ('paired_protocol_check.py', 'robustness.py',
    'test_robustness.py', 'ROBUSTNESS.md', 'heldout_protocol.py', 'test_heldout_protocol.py')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def registration():
    """No draws. Commit this manifest in HELDOUT_PROTOCOL.md before execution."""
    return {'version': VERSION, 'base_protocol_sha256': frozen.PROTOCOL_SHA256,
        'source_sha256': {n: hashlib.sha256((DIRECTORY/n).read_bytes()).hexdigest() for n in PIN_FILES},
        'namespace': 'held-out', 'indices': [FIRST, LAST],
        'cases': robust.development_protocol()['cases'], 'methods': list(METHODS),
        'designs': {k: list(v) for k, v in paired.SCENARIOS.items()},
        'particles': PARTICLES, 'fit_seconds': FIT_SECONDS, 'index_seconds': INDEX_SECONDS,
        'maximum_total_seconds': (LAST-FIRST+1)*INDEX_SECONDS,
        'thresholds': robust.development_protocol()['thresholds'],
        'interval_mass': .90, 'directional_threshold': .95,
        'initial_indices': [1000], 'execution_order': 'index/case/design/method insertion order',
        'independent_units': '128 latent indices; cases/designs/methods paired, never independent',
        'comparison': 'complete-pair differences: squared error, interval width, coverage, wrong declarations',
        'uncertainty': 'marginal Wilson 95% binomial; paired mean difference Hoeffding 95% bounded intervals; no multiplicity correction',
        'scientific_decision': 'descriptive comparison only; no winner or calibration certification; baseline nominal coverage .90, PIT uniformity only under generating prior',
        'missing': 'all cells retained; selected pass statistics and requested-denominator bounds',
        'simultaneous': 'either directional declaration is wrong; unresolved is not equality detection',
        'retries': False, 'outcome_driven_changes': 'new version and untouched stream required'}


def validate_registration(expected_sha, document=None):
    text = (document or DIRECTORY/'HELDOUT_PROTOCOL.md').read_text()
    try:
        saved = json.loads(text.split('```json\n', 1)[1].split('\n```', 1)[0])
    except (IndexError, ValueError) as error:
        raise ValueError('missing registered manifest') from error
    if digest(saved) != expected_sha or saved != registration():
        raise ValueError('registration or source pin drift')
    frozen.validate_freeze()
    return saved


def registered_index(namespace, index):
    if namespace != 'held-out' or type(index) is not int or not FIRST <= index <= LAST:
        raise ValueError('unregistered draw: held-out indices 1000..1127 only')


def generate(registration_sha, case, namespace='held-out', index=1000, scenario='balanced'):
    """Same ancestry and random roles as paired.generate, with explicit departures.

    Baseline is byte-equivalent. All designs/cases at an index share chronology,
    baseline events, calibration and random streams; simultaneity replaces B's
    event by A's. Truth remains exclusively in the labelled oracle.
    """
    validate_registration(registration_sha)
    registered_index(namespace, index)
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



def infer_gaussian(registration_sha, observation, namespace='held-out', index=1000, particles=50000, seconds=20.):
    validate_registration(registration_sha)
    registered_index(namespace, index)
    if type(observation) is not paired.PublicObservation:
        raise ValueError('public observations required; oracle forbidden')
    paired.validate_public(observation.to_dict())
    if type(particles) is not int or particles != PARTICLES:
        raise ValueError('registered particle count 50000 required')
    if not math.isfinite(seconds) or not 0 < seconds <= paired.MAX_SECONDS:
        raise ValueError('finite time budget in (0,20] required')
    start, batches = time.monotonic(), []
    for batch in range(2):
        rng = paired.stream(namespace, index, f'{GAUSSIAN_VERSION}/gaussian-material/{batch}')
        rows = []
        for i in range(particles//2):
            if i % 32 == 0 and time.monotonic()-start > seconds:
                return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
            candidate = paired.prior_draw(rng)
            candidate, correction = paired.propose_chronology(observation, candidate, rng)
            candidate, event_correction = paired.propose_events(observation, candidate, rng)
            logw = robust.gaussian_log_likelihood(observation, candidate)+correction+event_correction
            if not math.isfinite(logw):
                return {'status': 'FAILED_NONFINITE', 'posterior': None}
            rows.append((*candidate.events, logw))
        batches.append(rows)
    result = robust.summarize_batches(batches)
    if time.monotonic()-start > seconds:
        return {'status': 'FAILED_TIME_BUDGET', 'posterior': None}
    return dict(result, particles=particles, elapsed_seconds=time.monotonic()-start)



def wilson(successes, total):
    """Two-sided 95% Wilson score interval; null when no denominator."""
    if not 0 <= successes <= total:
        raise ValueError('invalid binomial counts')
    if not total:
        return None
    z = 1.959963984540054
    p, d = successes/total, 1+z*z/total
    center = (p+z*z/(2*total))/d
    radius = z*math.sqrt(p*(1-p)/total+z*z/(4*total*total))/d
    return [max(0., center-radius), min(1., center+radius)]


def bounded_mean(values, lower, upper):
    """Distribution-free Hoeffding interval for independent, bounded differences."""
    if any(not lower <= v <= upper for v in values):
        raise ValueError('paired statistic outside registered bounds')
    if not values:
        return {'n': 0, 'mean': None, 'interval_95': None}
    mean = math.fsum(values)/len(values)
    radius = (upper-lower)*math.sqrt(math.log(40)/(2*len(values)))
    return {'n': len(values), 'mean': mean,
            'interval_95': [max(lower, mean-radius), min(upper, mean+radius)]}


def summarize(records, indices):
    counts = robust.accounting([r for r in records if not r['status'].startswith('MISSING_')], indices, CASES)
    keys = [(r['index'], r['case'], r['scenario'], r['method']) for r in records]
    expected = {(i, c, d, m) for i in indices for c in CASES for d in paired.SCENARIOS for m in METHODS}
    if len(set(keys)) != len(keys) or any(k not in expected for k in keys):
        raise ValueError('duplicate or unrequested record')
    for label, s in counts['strata'].items():
        n, passed, covered = s['requested'], s['passed'], s['covered_among_passes']
        s['selected_coverage_wilson_95'] = wilson(covered, passed)
        s['selected_wrong_declaration_wilson_95'] = wilson(s['wrong_among_declarations'], s['declarations'])
        s['failure_or_missing_wilson_95'] = wilson(s['failed']+s['missing'], n)
        s['requested_coverage_identification_bounds'] = [covered/n, (covered+n-passed)/n]
        # False declarations among successful fits / ALL requested, with missing unknown.
        wrong = s['wrong_among_declarations']
        s['requested_wrong_declaration_bounds'] = [wrong/n, (wrong+n-passed)/n]
        case, scenario, method = label.split('/')
        passing = [r for r in records if (r['case'], r['scenario'], r['method']) ==
                   (case, scenario, method) and r['status'] == 'PASS_DIAGNOSTICS']
        for metric, maximum in (('squared_error', 360000.), ('interval_width', 600.)):
            s['selected_'+metric] = bounded_mean([r[metric] for r in passing], 0., maximum)
        pits = [r['approximate_pit'] for r in passing if r.get('approximate_pit') is not None]
        bins = [sum(min(9, int(p*10)) == b for p in pits) for b in range(10)]
        s['approximate_pit'] = {'available': len(pits), 'missing_among_passes': passed-len(pits),
            'decile_counts': bins, 'decile_wilson_95': [wilson(k, len(pits)) for k in bins]}

    lookup = {(r['index'], r['case'], r['scenario'], r['method']): r for r in records}
    comparisons = {}
    metrics = {'squared_error': (-360000., 360000.), 'interval_width': (-600., 600.),
               'covered': (-1., 1.), 'wrong_order': (-1., 1.)}
    def contrast(label, left_key, right_key):
        pairs = [(lookup.get(left_key(i)), lookup.get(right_key(i))) for i in indices]
        complete = [(a, b) for a, b in pairs if a and b and
                    a['status'] == b['status'] == 'PASS_DIAGNOSTICS']
        result = {'requested_pairs': len(indices), 'complete_pairs': len(complete),
                  'incomplete_pairs': len(indices)-len(complete)}
        for metric, bounds in metrics.items():
            # For this unconditional false-declaration contrast an unresolved pass is zero.
            differences = [(int(a[metric] is True)-int(b[metric] is True)
                            if metric in ('covered', 'wrong_order') else a[metric]-b[metric])
                           for a, b in complete]
            result[metric] = bounded_mean(differences, *bounds)
        comparisons[label] = result
    for case in CASES:
        for method in METHODS:
            contrast(f'{case}/{method}/proxy-minus-date',
                lambda i: (i, case, 'proxy-rich', method),
                lambda i: (i, case, 'date-rich', method))
        for design in paired.SCENARIOS:
            contrast(f'{case}/{design}/exponential-minus-gaussian',
                lambda i: (i, case, design, METHODS[0]),
                lambda i: (i, case, design, METHODS[1]))
    counts['comparisons'] = comparisons
    return counts


def execute_index(index, registration_sha, progress=None):
    validate_registration(registration_sha)
    registered_index('held-out', index)
    start, records = time.monotonic(), []
    for case in CASES:
        for scenario in paired.SCENARIOS:
            public = oracle = None
            generation_error = None
            if time.monotonic()-start < INDEX_SECONDS:
                try:
                    public, oracle = generate(registration_sha, case, index=index, scenario=scenario)
                except (ArithmeticError, ValueError) as error:
                    generation_error = str(error)
            for method in METHODS:
                remaining = INDEX_SECONDS-(time.monotonic()-start)
                row = {'index': index, 'case': case, 'scenario': scenario, 'method': method,
                       'status': 'MISSING_TIME_BUDGET'}
                if generation_error is not None:
                    row.update(status='FAILED_GENERATION', error=generation_error)
                elif public is not None and remaining > 0:
                    try:
                        if method == METHODS[0]:
                            result = paired.infer(public, namespace='held-out', index=index,
                                particles=PARTICLES, seconds=min(FIT_SECONDS, remaining), retain_ensemble=True)
                        else:
                            result = infer_gaussian(registration_sha, public, index=index,
                                particles=PARTICLES, seconds=min(FIT_SECONDS, remaining))
                        row.update(status=result['status'], **paired.evaluate(result, oracle))
                        if result.get('diagnostics'):
                            row['minimum_batch_ess'] = min(d['ess'] for d in result['diagnostics'])
                    except (ArithmeticError, ValueError) as error:
                        row.update(status='FAILED_EXCEPTION', error=str(error))
                records.append(row)
                if progress is not None:
                    progress(records)
    return {'version': VERSION, 'registration_sha256': registration_sha, 'indices': [index],
            'runtime': paired.provenance(), 'elapsed_seconds': time.monotonic()-start,
            'scope': 'one latent index; not a completed calibration study', 'records': records,
            'accounting': summarize(records, (index,))}


def run_once(index, registration_sha, directory):
    """Exclusive reservation survives interruption. Never silently overwrite/retry."""
    validate_registration(registration_sha)
    registered_index('held-out', index)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    output = directory/f'{VERSION}-{index}.json'
    # Every requested cell is explicitly missing in the interruption receipt.
    missing = [{'index': index, 'case': c, 'scenario': s, 'method': m,
                'status': 'MISSING_INTERRUPTED_OR_NOT_STARTED'}
               for c in CASES for s in paired.SCENARIOS for m in METHODS]
    def snapshot(records, status):
        seen = {(r['case'], r['scenario'], r['method']) for r in records}
        remaining = [r for r in missing if (r['case'], r['scenario'], r['method']) not in seen]
        all_records = list(records)+remaining
        return {'version': VERSION, 'registration_sha256': registration_sha,
                'indices': [index], 'status': status, 'records': all_records,
                'accounting': summarize(all_records, (index,))}
    with output.open('x') as handle:
        json.dump(snapshot([], 'RESERVED_NOT_COMPLETED'), handle)
    pending = output.with_suffix('.pending')
    def save(report):
        with pending.open('w') as handle:
            json.dump(report, handle, sort_keys=True, allow_nan=False)
        pending.replace(output)
    report = execute_index(index, registration_sha,
                           progress=lambda records: save(snapshot(records, 'INCOMPLETE')))
    save(report)
    return output


def aggregate(directory, registration_sha):
    validate_registration(registration_sha)
    records, observed = [], []
    for path in sorted(Path(directory).glob(f'{VERSION}-*.json')):
        report = json.loads(path.read_text())
        if report.get('registration_sha256') != registration_sha or len(report.get('indices', [])) != 1:
            raise ValueError('foreign or malformed run receipt')
        index = report['indices'][0]
        registered_index('held-out', index)
        if index in observed:
            raise ValueError('repeated index; no retry selection permitted')
        observed.append(index)
        records.extend(report['records'])
    return {'version': VERSION, 'registration_sha256': registration_sha,
            'observed_indices': observed, 'registered_indices': [FIRST, LAST],
            'records': records, 'accounting': summarize(records, tuple(range(FIRST, LAST+1)))}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='store_true', help='print candidate manifest without drawing')
    parser.add_argument('--validate', action='store_true')
    parser.add_argument('--aggregate', type=Path, help='summarize receipts against all 128 registered indices')
    parser.add_argument('--registration-sha')
    parser.add_argument('--index', type=int)
    parser.add_argument('--output-dir', type=Path)
    args = parser.parse_args()
    if args.manifest:
        if args.index is not None:
            parser.error('manifest cannot execute an index')
        print(json.dumps(registration(), indent=2, sort_keys=True))
        return
    if not args.registration_sha:
        parser.error('explicit frozen --registration-sha required')
    validate_registration(args.registration_sha)
    if args.aggregate is not None:
        if args.index is not None:
            parser.error('aggregate cannot execute an index')
        print(json.dumps(aggregate(args.aggregate, args.registration_sha), sort_keys=True, allow_nan=False))
        return
    if args.validate:
        print('PASS registration and scientific pins')
        return
    if args.index is None or args.output_dir is None:
        parser.error('--index and --output-dir required')
    print(run_once(args.index, args.registration_sha, args.output_dir))


if __name__ == '__main__':
    main()
