"""Fixed-size stationary linear control for a selected nonlinear rank fluctuation."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy.stats import beta

from reference import community, score
from linear_reference import equilibrium, linear_system
from linear_calibration import stationary_sample
from interpolated_linear import interpolated_system, predictions


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def binomial_interval(successes, trials, alpha=.05):
    if type(successes) is not int or type(trials) is not int or not 0 <= successes <= trials or trials < 1:
        raise ValueError('need valid fixed-trial counts')
    return [0. if successes == 0 else float(beta.ppf(alpha/2, successes, trials-successes+1)),
            1. if successes == trials else float(beta.ppf(1-alpha/2, successes+1, trials-successes))]


def configuration():
    return dict(community=9, paths=512, observations=8192, short=4096, segment=30,
                spacing=1/32, first_input_seed=120000,
                severity_threshold='inclusive abs coherence rank delta >= 57/280, numerical tolerance 1e-12',
                length_threshold='strict abs coherence rank delta > .10, numerical tolerance 1e-12',
                numpy=np.__version__, scipy=scipy.__version__,
                source_sha256={n: digest(Path(__file__).with_name(n)) for n in (
                    'stationary_rank_control.py', 'reference.py', 'linear_reference.py',
                    'linear_calibration.py', 'interpolated_linear.py', 'linear_welch.py')},
                scope='Post-hoc question in one fixed local-linear community. Exact stationary Gaussian samples of the interpolated-input model, not nonlinear communities or a population validation.')


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    config = configuration()
    encoded = json.dumps(config, indent=2, sort_keys=True)+'\n'
    protocol = output/'protocol.json'
    if protocol.exists() and protocol.read_text() != encoded:
        raise ValueError('changed stationary-control protocol')
    protocol.write_text(encoded)
    u, g, labels = community(config['community'])
    x, r = equilibrium(u, g, np.r_[np.ones(24), np.full(6, 3.)])
    j, b = linear_system(u, g, x, r)
    step, covariance, residual = interpolated_system(j, b, config['spacing'])
    transition = np.linalg.matrix_power(step, 32)
    limiting_scores, _ = predictions(transition, covariance, g, labels)
    records = []
    for path in range(config['paths']):
        receipt = output/f'path-{path}.json'
        if receipt.exists():
            record = json.loads(receipt.read_text())
            if record['path'] != path or record['protocol_sha256'] != digest(protocol):
                raise ValueError('wrong stationary-control receipt')
        else:
            record = dict(path=path, input_seed=config['first_input_seed']+path,
                          protocol_sha256=digest(protocol), status='failure')
            try:
                samples, diagnostics = stationary_sample(transition, covariance, record['input_seed'], config['observations'])
                before, after = score(samples[:config['short']], g, labels), score(samples, g, labels)
                record.update(status='success', diagnostics=diagnostics,
                    scores=after, deltas={m: {k: after[m][k]-before[m][k] for k in before[m]} for m in before})
            except (ValueError, RuntimeError, FloatingPointError) as error:
                record['error'] = str(error)
            receipt.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
        records.append(record)
        if (path+1) % 64 == 0:
            print('stationary paths', path+1, flush=True)
    good = [r for r in records if r['status'] == 'success']
    failures = [r for r in records if r['status'] == 'failure']
    events = {}
    for name, threshold, inclusive in [('observed_severity', 57/280, True), ('original_rank_margin', .10, False)]:
        count = sum(abs(r['deltas']['coherence']['overlap_spearman']) >= threshold-1e-12
                    if inclusive else abs(r['deltas']['coherence']['overlap_spearman']) > threshold+1e-12 for r in good)
        lower = binomial_interval(count, config['paths'])[0]
        upper = binomial_interval(count+len(failures), config['paths'])[1]
        events[name] = dict(known_exceedances=count, unknown=len(failures), planned_paths=config['paths'],
                           fixed_n_marginal95_completion_interval=[lower, upper])
    rows = []
    for metric in limiting_scores:
        for target in limiting_scores[metric]:
            values = np.array([abs(r['deltas'][metric][target]) for r in good])
            rows.append(dict(metric=metric, target=target, successful_paths=len(good),
                mean_absolute_length_change=float(values.mean()) if len(values) else None,
                q95_absolute_length_change=float(np.quantile(values, .95)) if len(values) else None,
                maximum_absolute_length_change=float(values.max()) if len(values) else None,
                limiting_score=limiting_scores[metric][target]))
    summary = dict(scope=config['scope'], planned=config['paths'], attempted=len(records),
        successful=len(good), failures=failures, events=events, diagnostics=rows,
        mesh_lyapunov_relative_residual=residual, protocol_sha256=digest(protocol),
        ordered_receipt_hash_digest=hashlib.sha256(''.join(digest(output/f'path-{p}.json') for p in range(config['paths'])).encode()).hexdigest(),
        maximum_stationarity_covariance_residual=max((r['diagnostics']['transition_covariance_residual'] for r in good), default=None))
    (output/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    with (output/'scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.output)
    print(json.dumps(result['events'], sort_keys=True))
