#!/usr/bin/env python3
"""Frozen milestone-one development report; Python standard library only.

No seed, trial-count or held-out switches: this is an acceptance recipe, not
the prospective scientific evaluation. Each calculation runs in a child with
a wall timeout. Failed stages remain in the report; none are silently omitted.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import platform
import subprocess
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parent
VERSION = 'latent-step-contract-v1'
TRIALS = 2000
STAGE_SECONDS = 240
TOTAL_SECONDS = 900
STAGES = ('analytic', 'published', 'finite', 'continuous', 'gaussian', 'audit', 'example')


def calculate(stage):
    import baseline as b
    import change_point as c
    if stage == 'analytic':
        # Existing independent derivations, including enumeration, observation-
        # space Student-t densities, material integration and chronology limits.
        suite = unittest.defaultTestLoader.discover(str(ROOT), pattern='test_*.py')
        output = io.StringIO()
        result = unittest.TextTestRunner(stream=output).run(suite)
        return {'tests_run': result.testsRun, 'successful': result.wasSuccessful(),
                'skipped': len(result.skipped),
                'failures': [{'test': str(test), 'trace': trace[-1600:]}
                             for test, trace in result.failures + result.errors],
                'certificate': c.certified_mismatch(),
                'published_response': {'h_years': 200,
                    'younger_fraction_at_event': b.mixed_fraction(0, 0, 200),
                    'half_height_offset_years': c.mixing_counterexample()['half_height']}}
    if stage == 'published':
        row = c.published_simulation(seed=20261124)
        row.pop('count_probabilities')
        return row
    if stage == 'finite':
        keys = ('law', 'trials', 'seed', 'pit_ks', 'pit_99_percent_dkw_bound',
                'pit_within_band', 'interval_coverage', 'interval_mean_posterior_mass',
                'event_information_mean_nats', 'data_conditional_pit', 'numerical_failures')
        cases = {'own_law': {}, 'ignore_mixing': {'ignore_mixing': True},
                 'prior_only': {'prior_only': True},
                 'continuous_truth_discrete_fit': {'continuous_truth': True}}
        return {name: {k: v for k, v in b.calibration(TRIALS, 20261124, **kw).items()
                       if k in keys} for name, kw in cases.items()}
    if stage == 'continuous':
        return c.matched_event_calibration(TRIALS, 20261124, .0625)
    if stage == 'gaussian':
        return {'one_event_own_law': c.gaussian_event_calibration(TRIALS, 672419),
                'count_own_law': c.calibration(TRIALS, 914073)}
    if stage == 'audit':
        from audit import audit
        return audit()
    if stage == 'example':
        row = c.foundation_comparison(20261124)
        for key in ('gaussian_boundary_inclusion', 'boundary_midpoint_labels'):
            row.pop(key)
        return row
    raise ValueError('unknown stage')


def assess(stages):
    """Distinct numerical/statistical gates; robustness failures are evidence."""
    gates = {'all_stages_completed': 'PASS' if all(
        row['status'] == 'OK' for row in stages.values()) else 'UNRESOLVED'}
    def gate(name, stage, check):
        row = stages[stage]
        if row['status'] != 'OK':
            gates[name] = 'UNRESOLVED'
            return
        try:
            gates[name] = 'PASS' if check(row['result']) else 'FAIL'
        except (KeyError, TypeError, ValueError, IndexError):
            gates[name] = 'FAIL'
    gate('independent_analytic_checks', 'analytic',
         lambda r: r['successful'] and r['tests_run'] >= 74 and not r['skipped'])
    gate('exact_target_mismatch', 'analytic', lambda r:
         r['certificate']['exact_rational_positive_gap_verified'] and
         r['certificate']['binomial_gaussian_profile_positive_gap_verified'])
    gate('published_law_input_identity', 'published', lambda r: r['input_sha256'] ==
         'dd37ce2621618b2eab9bd0c84d501e72a969d5c3c815ca91c0418a32835deb5d')
    gate('finite_own_law_calibration', 'finite', lambda r:
         r['own_law']['pit_within_band'] and r['own_law']['numerical_failures'] == 0)
    gate('prior_only_trap_exposed', 'finite', lambda r:
         r['prior_only']['pit_within_band'] and all(
             g['pit_within_band'] is False for g in r['prior_only']['data_conditional_pit'].values()))
    gate('continuous_own_law_calibration', 'continuous', lambda r:
         r['models']['observation_aware']['all']['pit_ks'] <=
         r['models']['observation_aware']['all']['individual_99_percent_dkw_band'])
    gate('gaussian_event_own_law_calibration', 'gaussian', lambda r:
         r['one_event_own_law']['pit_ks'] <= r['one_event_own_law']['individual_99_percent_dkw_band'])
    gate('gaussian_count_own_law_calibration', 'gaussian', lambda r: all(
         g['ks'] <= g['individual_99_percent_dkw_band']
         for g in r['count_own_law']['diagnostics']['posterior'].values()))
    gate('gaussian_conditional_location_calibration', 'gaussian', lambda r:
         r['count_own_law']['one_change_location_conditional_calibration']['ks'] <=
         r['count_own_law']['one_change_location_conditional_calibration']['individual_99_percent_dkw_band'])
    # These are frozen finite-probe accuracy criteria, not certified bounds.
    gate('finest_grid_finite_probe_accuracy', 'audit', lambda r:
         r['max_probe_cdf_errors'][-1] <= .001 and
         r['max_reference_tolerance_difference'] <= 1e-8)
    gate('unmixed_exact_endpoint_agreement', 'continuous', lambda r:
         r['max_unmixed_endpoint_discrepancy_vs_exact_rational'] <= 1e-8)
    return gates


def run():
    started = time.monotonic()
    def fingerprints():
        sources = sorted(ROOT.glob('*.py')) + sorted(ROOT.glob('*.md'))
        return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    source_hashes = fingerprints()
    stages = {}
    for stage in STAGES:
        remaining = TOTAL_SECONDS - (time.monotonic() - started)
        if remaining <= 0:
            stages[stage] = {'status': 'NOT_RUN', 'reason': 'total wall budget exhausted'}
            continue
        print(f'Checking {stage} (development only)...', file=sys.stderr, flush=True)
        try:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--stage', stage],
                                   capture_output=True, text=True,
                                   timeout=min(STAGE_SECONDS, remaining))
            if child.returncode:
                stages[stage] = {'status': 'ERROR', 'returncode': child.returncode,
                                 'reason': child.stderr[-2000:]}
            else:
                stages[stage] = {'status': 'OK', 'result': json.loads(child.stdout)}
        except subprocess.TimeoutExpired:
            stages[stage] = {'status': 'TIMEOUT', 'reason': 'stage or total wall budget exhausted'}
        except (ValueError, OSError) as error:
            stages[stage] = {'status': 'ERROR', 'reason': str(error)}
    gates = assess(stages)
    gates['unchanged_sources_during_run'] = 'PASS' if fingerprints() == source_hashes else 'FAIL'
    accepted = all(value == 'PASS' for value in gates.values())
    return {'contract': VERSION, 'python': platform.python_version(),
            'development_only': True, 'held_out_evaluated': False,
            'budget': {'trials_per_calibration': TRIALS, 'stage_wall_seconds': STAGE_SECONDS,
                       'total_wall_seconds': TOTAL_SECONDS, 'maximum_event_cells': 3200},
            'source_sha256': source_hashes,
            'gates': gates, 'stages': stages,
            'assessment': 'READY_FOR_INDEPENDENT_MILESTONE_REVIEW' if accepted else 'REQUIREMENTS_UNMET',
            'milestone_closed': False,
            'remaining': ['Independent milestone review and integration of this release.',
                          'Paired experiment freeze and prospective held-out evaluation are later milestones.',
                          'No historical reconstruction, literal Khider reproduction or novelty claim.'],
            'interpretation': 'Numerical agreement and own-law calibration are different checks. '
                              'DKW bands are individual 99% diagnostics, not simultaneous certification. '
                              'A development diagnostic pass does not establish scientific validity.'}


def render(report):
    print(f"{report['contract']}: {report['assessment']}")
    print('Development seeds only; milestone remains OPEN pending independent review.')
    print('Budget: 2000 trials/check; 240 s/stage; 900 s total; no held-out evaluation.')
    for name, status in report['gates'].items():
        print(f'{status:10} {name}')
    for name, row in report['stages'].items():
        if row['status'] != 'OK':
            print(f"{row['status']:10} {name}: {row.get('reason', '')}")
    def result(stage):
        return report['stages'][stage].get('result')
    if r := result('analytic'):
        print(f"Analytic checks: {r['tests_run']} tests; {len(r['failures'])} failures/errors.")
        print('Exact positive gaps (display only):',
              r['certificate']['gap_display_only'],
              r['certificate']['binomial_gaussian_profile_gap_display_only'])
    if r := result('published'):
        print(f"Published simulation law: P(K=0)={r['p_zero_changes']:.9f}; E[K]={r['expected_changes']:.9f}")
    if r := result('finite'):
        for name, row in r.items():
            print(f"Finite {name}: PIT KS={row['pit_ks']:.7f}; coverage={row['interval_coverage']:.4f}; "
                  f"mean posterior interval mass={row['interval_mean_posterior_mass']:.7f}")
    if r := result('continuous'):
        for name, groups in r['models'].items():
            row = groups['all']
            print(f"Continuous {name}: PIT KS={row['pit_ks']:.7f}; coverage={row['coverage_90']:.4f}; "
                  f"mean width={row['mean_width']:.6f} years")
        print(f"Individual 99% PIT band: {row['individual_99_percent_dkw_band']:.7f}")
    if r := result('gaussian'):
        e, c = r['one_event_own_law'], r['count_own_law']
        print(f"Gaussian own-law event: PIT KS={e['pit_ks']:.7f}; coverage={e['coverage_90']:.4f}")
        print(f"Gaussian own-law count: PIT KS={c['diagnostics']['posterior']['all']['ks']:.7f}; "
              f"coverage={c['count_interval_coverage']:.4f}")
    if r := result('audit'):
        print('Grid widths:', r['steps'])
        print('Finite-probe CDF errors (coarse failures retained):', r['max_probe_cdf_errors'])
    print(report['interpretation'])
    for item in report['remaining']:
        print('Remaining:', item)
    print('Use --json for complete diagnostics, controls, source hashes and same-data example.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true', help='complete machine-readable report')
    parser.add_argument('--stage', choices=STAGES, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.stage:
        print(json.dumps(calculate(args.stage), allow_nan=False))
        return 0
    report = run()
    if args.json:
        print(json.dumps(report, indent=2, allow_nan=False))
    else:
        render(report)
    return 0 if report['assessment'] == 'READY_FOR_INDEPENDENT_MILESTONE_REVIEW' else 1


if __name__ == '__main__':
    sys.exit(main())
