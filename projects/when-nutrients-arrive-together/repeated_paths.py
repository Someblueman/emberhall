"""Second independent OU path per fixed community; no correlated inputs."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from convergence import METRICS, TARGETS, stationarity
from reference import community, ou, simulate, score, interval


def repeat(study, output):
    config = json.loads((study/'protocol.json').read_text())
    protocol = dict(parent_sha256=hashlib.sha256((study/'protocol.json').read_bytes()).hexdigest(),
                    seeds=config['seeds'], input_seed_offset=40000, mesh=.0625,
                    duration=config['duration'], burn=config['burn'], rtol=1e-8,
                    code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                    purpose='separate input-path variation from community variation; no new clean acceptance')
    output.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(protocol, indent=2, sort_keys=True)+'\n'
    path = output/'protocol.json'
    if path.exists() and path.read_text() != encoded:
        raise ValueError('different repeat protocol')
    path.write_text(encoded)
    records = []
    for seed in config['seeds']:
        receipt = output/f'seed-{seed}.json'
        if receipt.exists():
            records.append(json.loads(receipt.read_text()))
            continue
        r = dict(seed=seed, status='failure')
        try:
            uptake, gain, labels = community(seed)
            supply = ou(40000+seed, config['duration'], spacing=.0625)
            if supply.min() <= 0:
                raise ValueError('nonpositive supply; not repaired')
            x, minimum = simulate(uptake, gain, supply, .0625, config['duration'],
                                  config['burn'], .0625, 1e-8)
            r.update(status='success', scores=score(x, gain, labels),
                     minimum_abundance=minimum, minimum_supply=float(supply.min()),
                     stationarity=stationarity(x))
            np.savez_compressed(output/f'seed-{seed}.npz', log_abundance=x)
        except (ValueError, RuntimeError, FloatingPointError) as error:
            r['error'] = str(error)
        receipt.write_text(json.dumps(r, indent=2, allow_nan=False)+'\n')
        records.append(r)
        print('second path', seed, r['status'], flush=True)
    return records


def analyze_repeats(study, output):
    config = json.loads((study/'protocol.json').read_text())
    pairs, failures = [], []
    for seed in config['seeds']:
        a = json.loads((study/f'seed-{seed}.json').read_text())
        b = json.loads((output/f'seed-{seed}.json').read_text())
        if a['status'] != 'success' or b['status'] != 'success':
            failures.append(dict(seed=seed, first_status=a['status'], second_status=b['status']))
        else:
            pairs.append((a['scores']['0.0625']['30'], b['scores']))
    summary = {}
    for m in METRICS:
        summary[m] = {}
        for k in TARGETS:
            data = np.array([[a[m][k], b[m][k]] for a,b in pairs])
            if len(data) < 2:
                continue
            means = data.mean(1)
            within = float(np.mean((data[:, 0]-data[:, 1])**2)/2)
            # Random-effects method of moments; raw negative estimate is retained.
            between = float(means.var(ddof=1)-within/2)
            summary[m][k] = dict(community_mean_interval=interval(means),
                                within_path_variance=within, between_community_variance_raw=between,
                                maximum_path_score_change=float(np.max(np.abs(data[:, 0]-data[:, 1]))))
    result = dict(complete_communities=len(pairs), failures=failures, summaries=summary,
                  caveat='Two paths per community; approximate random-effects diagnostics, not a precise variance decomposition. Communities remain the replicates.')
    (output/'repeated-summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--analyze', action='store_true')
    args = parser.parse_args()
    if args.analyze:
        analyze_repeats(args.study, args.output)
    else:
        repeat(args.study, args.output)
