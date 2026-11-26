"""Post-hoc 65536-observation extension of the reported coherence length failure."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy

from reference import community, ou, simulate, score, measures, PAIRS
from ou_bridge import bridge
from convergence import stationarity
from rank_attribution import attribution


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def configuration():
    return dict(community=9, drive=0, input_seed=80900, bridge_seed=90900,
                duration=66048, burn=512, retained=65536,
                lengths=[4096, 8192, 16384, 32768, 65536],
                coarse_spacing=1/16, spacing=1/32, max_step=1/32, rtol=1e-9,
                prefix_tolerance=1e-6, numpy=np.__version__, scipy=scipy.__version__,
                sources={n: digest(Path(__file__).with_name(n)) for n in (
                    'coherence_extension.py', 'rank_attribution.py', 'reference.py',
                    'ou_bridge.py', 'convergence.py')},
                scope='Selected after observing the largest coherence length change. One dependent path; original gates unchanged; no new community, held-out or correlated-input experiment.')


def run(output, replay):
    output.mkdir(parents=True, exist_ok=True)
    config = configuration()
    encoded = json.dumps(config, indent=2, sort_keys=True)+'\n'
    protocol = output/'protocol.json'
    if protocol.exists() and protocol.read_text() != encoded:
        raise ValueError('source or protocol changed')
    protocol.write_text(encoded)
    receipt = output/'receipt.json'
    if receipt.exists():
        return json.loads(receipt.read_text())
    record = dict(status='failure', protocol_sha256=digest(protocol))
    started = time.monotonic()
    try:
        old_receipt_path = replay/'community-9-drive-0.json'
        old_receipt = json.loads(old_receipt_path.read_text())
        old_arrays = old_receipt_path.with_suffix('.npz')
        if old_receipt['status'] != 'success' or digest(old_arrays) != old_receipt['trajectory_sha256']:
            raise ValueError('independent replay failed or changed')
        with np.load(old_arrays, allow_pickle=False) as arrays:
            previous = arrays['fine']
        record['previous_receipt_sha256'] = digest(old_receipt_path)
        coarse = ou(config['input_seed'], config['duration'], config['coarse_spacing'])
        fine = bridge(coarse, config['coarse_spacing'], config['bridge_seed'])
        record['minimum_supply'] = float(fine.min())
        if record['minimum_supply'] <= 0 or not np.array_equal(fine[::2], coarse):
            raise ValueError('nonpositive supply or changed coarse endpoints')
        del coarse
        uptake, gain, labels = community(config['community'])
        trajectory, minimum = simulate(uptake, gain, fine, config['spacing'],
            config['duration'], config['burn'], config['max_step'], config['rtol'])
        del fine
        record['minimum_abundance'] = minimum
        error = float(np.abs(trajectory[:len(previous)]-previous).max())
        record['maximum_prefix_error'] = error
        if previous.shape != (8192, 6) or error > config['prefix_tolerance']:
            raise ValueError('extension does not preserve the replayed prefix')
        path = output/'trajectory.npz'
        np.savez_compressed(path, log_abundance=trajectory)
        record.update(status='success', trajectory_sha256=digest(path))
    except (ValueError, RuntimeError, FloatingPointError) as error:
        record['error'] = str(error)
    record['elapsed_seconds'] = time.monotonic()-started
    receipt.write_text(json.dumps(record, indent=2, allow_nan=False)+'\n')
    return record


def report(output):
    config = json.loads((output/'protocol.json').read_text())
    if config != configuration():
        raise ValueError('configuration or source changed')
    receipt = json.loads((output/'receipt.json').read_text())
    if receipt['protocol_sha256'] != digest(output/'protocol.json'):
        raise ValueError('receipt protocol mismatch')
    if receipt['status'] != 'success':
        return receipt
    arrays_path = output/'trajectory.npz'
    if digest(arrays_path) != receipt['trajectory_sha256']:
        raise ValueError('changed trajectory')
    with np.load(arrays_path, allow_pickle=False) as saved:
        trajectory = saved['log_abundance']
    if trajectory.shape != (65536, 6) or not np.isfinite(trajectory).all():
        raise ValueError('invalid trajectory')
    _, gain, labels = community(config['community'])
    target = (gain@gain.T)[PAIRS]
    rows, windows, changes = [], {}, {}
    previous = None
    for n in config['lengths']:
        x = trajectory[:n]
        scores, pair_values = score(x, gain, labels), measures(x)
        windows[str(n)] = dict(scores=scores, second_half_scores=score(x[n//2:], gain, labels),
                               stationarity_descriptive=stationarity(x))
        for metric, values in scores.items():
            rows.append(dict(observations=n, metric=metric, **values))
        if previous is not None:
            changes[str(n)] = {}
            for metric in scores:
                result = attribution(target, previous[metric], pair_values[metric])
                comparisons = result.pop('comparisons')
                result['largest_contributions'] = sorted(comparisons, key=lambda r: -abs(r['contribution']))[:3]
                changes[str(n)][metric] = result
        previous = pair_values
    summary = dict(scope=config['scope'], receipt=receipt, windows=windows, rank_changes=changes)
    (output/'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False)+'\n')
    with (output/'scores.csv').open('w') as stream:
        writer = csv.DictWriter(stream, list(rows[0])); writer.writeheader(); writer.writerows(rows)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--replay', type=Path, required=True)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    if not args.report_only:
        result = run(args.output, args.replay)
        print('extension', result['status'], flush=True)
    result = report(args.output)
    if 'windows' in result:
        for n, row in result['windows'].items():
            print(n, {m: round(v['overlap_spearman'], 6) for m, v in row['scores'].items()})
