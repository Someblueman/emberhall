"""Audit planned extension receipts and export dependent-window diagnostics."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

from reference import interval

METRICS = ('correlation', 'absolute_correlation', 'cpsd', 'coherence')
TARGETS = ('overlap_spearman', 'same_diet_pair_auc', 'single_linkage_guild_auc')
WINDOWS = (2048, 4096, 8192, 10000, 16384, 20000)


def load(partitions):
    records, hashes = {}, {}
    for directory in partitions:
        config = json.loads((directory / 'protocol.json').read_text())
        if (config['retained'], config['baseline_retained'], config['burn'],
            config['mesh'], config['tolerance'], config['segment'],
            config['supply_seed_offset']) != (20000, 4096, 512, .0625, 1e-8, 30, 20000):
            raise ValueError('unexpected experiment settings')
        if set(config['code_sha256']) != {'reference.py', 'extend_length.py'}:
            raise ValueError('both experiment source hashes are required')
        for name, expected in config['code_sha256'].items():
            if hashlib.sha256(Path(__file__).with_name(name).read_bytes()).hexdigest() != expected:
                raise ValueError('recorded source differs from current source')
        for seed in config['communities']:
            if seed not in range(8, 16) or seed in records:
                raise ValueError('unexpected or duplicate community')
            path = directory / f'seed-{seed}.json'
            record = json.loads(path.read_text())
            if record['seed'] != seed or record['status'] not in ('success', 'failure'):
                raise ValueError('invalid receipt identity or status')
            if record['status'] == 'success':
                if not 0 <= record['prefix_max_error'] <= 1e-6:
                    raise ValueError('prefix check failed')
                for n in WINDOWS:
                    for metric in METRICS:
                        for target in TARGETS:
                            value = record['scores'][str(n)][metric][target]
                            low = -1 if target == 'overlap_spearman' else 0
                            if not np.isfinite(value) or not low <= value <= 1:
                                raise ValueError('invalid bounded score')
            records[seed] = record
            hashes[str(seed)] = hashlib.sha256(path.read_bytes()).hexdigest()
    if set(records) != set(range(8, 16)):
        raise ValueError('all eight planned communities must have receipts, including failures')
    return records, hashes


def summarize(partitions, output):
    records, hashes = load(partitions)
    good = [r for r in records.values() if r['status'] == 'success']
    summary = dict(planned=8, successful=len(good),
                   failures={str(s): r.get('error', '') for s, r in records.items()
                             if r['status'] == 'failure'}, receipt_sha256=hashes,
                   conditional_on_success=len(good) != 8,
                   max_prefix_error=max((r['prefix_max_error'] for r in good), default=None))
    summary['paired_4096_to_20000'] = {
        m: {t: interval([r['scores']['20000'][m][t] - r['scores']['4096'][m][t]
                         for r in good]) for t in TARGETS}
        for m in METRICS} if good else {}
    summary['maximum_10000_to_20000'] = {
        m: {t: max(abs(r['scores']['20000'][m][t] - r['scores']['10000'][m][t])
                    for r in good) for t in TARGETS} for m in METRICS} if good else {}
    summary['maximum_first_to_second_half'] = {
        m: {t: max(abs(r['second_half_scores'][m][t] - r['scores']['10000'][m][t])
                    for r in good) for t in TARGETS} for m in METRICS} if good else {}
    summary['half_to_full_passes_original_tolerances'] = {
        str(r['seed']): all(abs(r['scores']['20000'][m][t] - r['scores']['10000'][m][t])
                           <= (.10 if t == 'overlap_spearman' else .05)
                           for m in METRICS for t in TARGETS) for r in good}
    # The earlier four trajectories were deliberately not committed. Their
    # published table is rounded to eight significant digits; retain that limit.
    prior = Path(__file__).with_name('long-record-scores.csv')
    old = {}
    for row in csv.DictReader(prior.open()):
        key = (int(row['seed']), int(row['observations']), row['metric'])
        if key in old:
            raise ValueError('duplicate prior score')
        old[key] = float(row['overlap_spearman'])
    common = (2048, 4096, 8192, 16384, 20000)
    expected = {(s, n, m) for s in range(4, 8) for n in common for m in METRICS}
    if set(old) != expected or not all(np.isfinite(v) and -1 <= v <= 1 for v in old.values()):
        raise ValueError('invalid prior four-community table')
    if len(good) == 8:
        joined = dict(old)
        joined.update({(r['seed'], n, m): r['scores'][str(n)][m]['overlap_spearman']
                       for r in good for n in common for m in METRICS})
        summary['all_twelve_overlap'] = {
            str(n): {m: interval([joined[s, n, m] for s in range(4, 16)])
                     for m in METRICS} for n in common}
        summary['paired_all_twelve_overlap'] = {
            m: interval([joined[s, 20000, m]-joined[s, 4096, m] for s in range(4, 16)])
            for m in METRICS}
    summary['prior_csv_sha256'] = hashlib.sha256(prior.read_bytes()).hexdigest()
    output.mkdir(parents=True, exist_ok=True)
    (output / 'summary.json').write_text(json.dumps(summary, indent=2, allow_nan=False) + '\n')
    with (output / 'scores.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=['seed', 'observations', 'metric', *TARGETS])
        writer.writeheader()
        for r in sorted(good, key=lambda r: r['seed']):
            for n in WINDOWS:
                for m in METRICS:
                    writer.writerow(dict(seed=r['seed'], observations=n, metric=m,
                                         **r['scores'][str(n)][m]))
    print(json.dumps({k: summary[k] for k in ('planned', 'successful', 'failures',
                     'max_prefix_error', 'half_to_full_passes_original_tolerances')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('partitions', nargs='+', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    summarize(args.partitions, args.output)
