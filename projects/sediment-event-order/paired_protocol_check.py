#!/usr/bin/env python3
"""Bounded development-only preflight. Never authorizes or runs held-out data."""
from __future__ import annotations

import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import math
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

import paired_experiment as model

DIRECTORY = Path(__file__).resolve().parent
VERSION = 'paired-freeze-v1'
PROTOCOL_SHA256 = 'ce44adc83c905e751ec43f703720c8c223410d4ef4358a2f5cb9b4b12d6268c1'
PINS = {
    "paired_experiment.py": "78bb5b647db08429155ec357186891202d7c51cfdf4f231e733c6b4446901d33",
    "material_model.py": "c6bee7b0af91c69912d62315f7bd69d6b75b37c0e6c818cd293b9904a9520974",
    "chronology_model.py": "30d70d5801a65f0e194bf95eabb68a0cfbcb1719c5ccaf7ad41a603f9c0d8eab",
    "baseline.py": "b7e7039fca18aa0ea618210a865d00ad7904e05077efe0843af66ba65fa62b8a",
    "continuous.py": "89c9b7389c31666ecc08af13837e58b0e7659a57b0e462f9e2128ca5de0cb861",
    "change_point.py": "fb40bb3265a7117a0f2f9b1440e31754aad9b093bb5d10e81435fc5fcd502787",
    "test_paired_experiment.py": "220d6ae5916ad1f080c98bcb41081ea5342a6752b18928c066f8282f33b6d935",
    "PAIRED_EXPERIMENT.md": "a0c8bfad915d4aa86d4022e19f294b4115523a2600aad7f781a229a48da1623f",
    "MODEL_CONTRACT.md": "0c873c766bd13c5bdbb1f97d5744e500405f443a10d95e2991cb91c7ba5f1556"
}
GAPS = [
    'No held-out result or independent milestone-two verdict.',
    'Misspecified and simultaneous-event robustness cases are not implemented.',
    'No matched latent-climate-time Gaussian comparator; depth segmentation is not timing.',
    'No age-varying calibration curve, finite-width layers or continuous mixing prior.',
]


def source_hashes():
    return {name: hashlib.sha256((DIRECTORY / name).read_bytes()).hexdigest() for name in PINS}


def manifest():
    """Machine-readable plan; reading it draws no random stream."""
    protocol = model.protocol()
    return {
        'freeze_version': VERSION, 'model_protocol': protocol,
        'observation_law': {
            'material_age': 'path(z)-h+Exp(mean=h); zero layer half-width',
            'proxy': 'Bernoulli(0.9 if material_age<=tau else 0.1)',
            'date': 'material_age+c+epsilon',
            'common_error': 'one c~Normal(0,50^2) across both archives and all dates',
            'independent_errors': 'epsilon~Normal(0,100^2); separate specimens, paths and mixing',
            'chronology': 'surface Normal(800,35^2); independent Gamma(shape=40,scale=130/40) increments per cm',
            'specimen_link': 'date and proxy share latent age exactly when specimen IDs match',
            'truth_fence': 'only PublicObservation enters infer; oracle used after fitting',
        },
        'design': {
            'development_index': 0, 'development_replicates_per_scenario': 1,
            'particles': 50000, 'proposal': 'guided',
            'paired_latents': 'same namespace/index shares events, paths, mixing and calibration across scenarios',
            'count_contrast': 'proxy-rich versus date-rich: 13 unique specimens per layer; counts interchanged',
            'balanced_caveat': 'balanced also changes overlap and unique specimen count; no isolated count or cost contrast',
        },
        'precision_and_denominators': {
            'independent_latent_replicates': 128, 'scenario_runs': 384,
            'coverage_se_at_0_90': math.sqrt(.9*.1/128),
            'zero_errors_upper_one_sided_95_if_128_declarations': 1-.05**(1/128),
            'coverage': 'covered/passes is selected; report failures and missing/128 separately for each scenario',
            'order_error': 'wrong/declarations, with declaration denominator; no rare-error claim from zero errors',
            'pit': 'approximate weighted posterior PIT; report observed groups separately and their sizes',
            'comparison': 'paired per-index differences; never treat 384 scenario runs as independent',
            'no_decision': 'no scientific winner or calibration certification from this preflight',
        },
        'held_out': {
            'namespace': 'held-out', 'indices': [1000, 1127], 'retired_indices': [0, 999],
            'executed_by_this_command': False,
            'gate': 'independent milestone-two review and explicit later task before any held-out use',
            'revision_rule': 'new version and untouched seed range after any outcome-driven change',
            'accounting': 'no retries; missing and numerical failures retained; unchanged source/Python/protocol fingerprints',
        },
        'limits': {'preflight_subprocess_seconds': 180, 'fit_seconds': 20,
                   'batch_seconds': 60, 'registered_total_seconds': 5400,
                   'particle_storage_mib': 32, 'os_memory_limit': False},
        'source_sha256': source_hashes(), 'remaining_gaps': GAPS,
    }


def validate_freeze():
    """Refuse silent model changes, rather than blessing a new hash automatically."""
    actual = source_hashes()
    if actual != PINS:
        changed = [name for name in PINS if actual.get(name) != PINS[name]]
        raise ValueError('frozen input changed: ' + ', '.join(changed))
    p = model.protocol()
    expected = {'version': 'paired-v1', 'held_out_indices': [1000, 1127],
                'held_out_particles': 50000, 'held_out_proposal': 'guided',
                'max_seconds_per_fit': 20., 'max_seconds_per_batch': 60,
                'max_replicates_per_batch': 16, 'minimum_ess_each_batch': 100,
                'maximum_mean_disagreement_in_combined_mcse': 3,
                'maximum_endpoint_cdf_disagreement': .05,
                'maximum_order_probability_disagreement': .05,
                'coverage_interval_mass': .90, 'order_declaration_probability': .95,
                'held_out_total_wall_budget_seconds': 5400}
    for key, value in expected.items():
        if p.get(key) != value:
            raise ValueError('frozen protocol changed: ' + key)
    if hashlib.sha256(json.dumps(p, sort_keys=True).encode()).hexdigest() != PROTOCOL_SHA256:
        raise ValueError('frozen protocol fingerprint changed')
    return manifest()


@contextmanager
def development_only():
    original = model.stream
    def guarded(namespace, index, role):
        if namespace == 'held-out':
            raise ValueError('preflight forbids held-out random streams')
        return original(namespace, index, role)
    with patch.object(model, 'stream', guarded):
        yield


def analytic_checks():
    # Existing independent quadratures, density corrections and negative controls.
    import test_paired_experiment
    names = [
        'test_joint_likelihood_against_analytic_integrated_shared_offset',
        'test_nonzero_mixing_shared_specimen_likelihood_independent_quadrature',
        'test_importance_correction_against_independent_event_integration',
        'test_joint_chronology_proposal_density_by_collapsing_surface_ages',
        'test_truth_allowlist_at_every_level',
        'test_ancestry_cannot_be_changed_or_moved_between_archives',
        'test_ordering_uses_joint_weights_not_product_of_marginals',
        'test_registered_accounting_preserves_missing_and_failed_cases',
        'test_registered_accounting_rejects_duplicates_and_changed_contracts',
        'test_registered_total_budget_cannot_be_hidden_by_partial_results',
        'test_complete_accounting_never_means_failed_inference_is_calibrated',
        'test_budget_and_diagnostic_failures_withhold_posterior',
    ]
    suite = unittest.TestSuite(test_paired_experiment.PairedTests(name) for name in names)
    output = io.StringIO()
    result = unittest.TextTestRunner(stream=output).run(suite)
    return {'passed': result.wasSuccessful(), 'run': result.testsRun, 'names': names,
            'failures': output.getvalue() if not result.wasSuccessful() else None,
            'accounting_fixtures': 'fabricated accounting rows, not held-out observations'}


def development_cases():
    reports = {}
    for scenario in model.SCENARIOS:
        batch = model.benchmark('development', 0, 1, scenario, particles=50000, proposal='guided')
        reports[scenario] = {'requested': 1, 'attempted': batch['attempted'],
            'diagnostic_passes': batch['diagnostic_passes'], 'records': batch['records'],
            'source_changed_during_batch': batch['source_changed_during_batch'],
            'elapsed_seconds': batch['elapsed_seconds']}
    return reports


def preflight():
    frozen = validate_freeze()
    with development_only():
        checks = analytic_checks()
        cases = development_cases() if checks['passed'] else {}
    unchanged = source_hashes() == PINS
    passed = checks['passed'] and unchanged and len(cases) == 3 and all(
        c['diagnostic_passes'] == 1 and not c['source_changed_during_batch'] for c in cases.values())
    return {'status': 'READY_FOR_INDEPENDENT_REVIEW' if passed else 'PREFLIGHT_FAILED',
            'held_out_executed': False, 'manifest': frozen,
            'manifest_sha256': hashlib.sha256(json.dumps(frozen, sort_keys=True).encode()).hexdigest(),
            'runtime': model.provenance(),
            'preflight_source_sha256': {name: hashlib.sha256((DIRECTORY/name).read_bytes()).hexdigest()
                for name in ('paired_protocol_check.py', 'test_paired_protocol_check.py', 'PAIRED_PROTOCOL_FREEZE.md')},
            'analytic_checks': checks, 'development': cases,
            'source_unchanged': unchanged, 'milestone_complete': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', action='store_true', help='validate and print the plan without fitting')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    try:
        if args.manifest:
            result = validate_freeze()
        elif args.worker:
            result = preflight()
        else:
            child = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--worker'],
                                   capture_output=True, text=True, timeout=180)
            try:
                result = json.loads(child.stdout)
            except ValueError as error:
                raise RuntimeError('worker produced no report: ' + child.stderr[-2000:]) from error
            if child.returncode and result.get('status') != 'PREFLIGHT_FAILED':
                raise RuntimeError('worker exited unsuccessfully')
        print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
        return 0 if args.manifest or result['status'] == 'READY_FOR_INDEPENDENT_REVIEW' else 1
    except (ValueError, RuntimeError, subprocess.TimeoutExpired, OSError) as error:
        print(json.dumps({'status': 'PREFLIGHT_FAILED', 'held_out_executed': False,
                          'milestone_complete': False, 'error': str(error)}))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
