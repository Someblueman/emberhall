"""Independent tighter solve on one saved fine-forcing realization."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from paired_crosscheck import compare
from reference import ou, simulate, score


def check(experiment, seed=0, drive=0, stride=1):
    config = json.loads((experiment / 'config.json').read_text())
    model_hash = hashlib.sha256(Path(__file__).with_name('reference.py').read_bytes()).hexdigest()
    if config['model_sha256'] != model_hash:
        raise ValueError('saved experiment used a different model/estimator')
    with np.load(experiment / f'community-{seed}-drive-{drive}.npz') as saved:
        uptake, gain, labels = saved['uptake'], saved['gain'], saved['labels']
        original = saved['log_abundance']
    if stride not in (1, 2):
        raise ValueError('mesh stride must be one or two')
    original_scores = score(original, gain, labels)
    if stride == 2:
        rows = [json.loads(line) for line in (experiment/'records.jsonl').read_text().splitlines()]
        row = next(r for r in rows if r['community'] == seed and r['drive'] == drive)
        original_scores = {m: {k: row['scores'][m][k] - row['middle_to_fine'][m][k]
                               for k in row['scores'][m]} for m in row['scores']}
    spacing = config['finest'] * stride
    supply = ou(200000 + 1000*seed + drive, config['duration'], config['finest'])
    refined, _ = simulate(uptake, gain, supply[::stride], spacing, config['duration'],
                          config['burn'], spacing/4, 1e-10)
    difference = compare(original_scores, score(refined, gain, labels))
    result = dict(community=seed, drive=drive, mesh_stride=stride, duration=config['duration'], burn=config['burn'],
                  finest=config['finest'], model_sha256=model_hash,
                  original=dict(max_step=spacing/2, rtol=1e-8),
                  refined=dict(max_step=spacing/4, rtol=1e-10),
                  log_rms=float(np.sqrt(np.mean((refined-original)**2))) if stride == 1 else None,
                  maximum_absolute_log_change=float(np.max(np.abs(refined-original))) if stride == 1 else None,
                  score_differences=difference,
                  limitation='one realization only; not a bound for all communities')
    suffix = '' if stride == 1 else f'-stride-{stride}'
    (experiment / f'solver-check-{seed}-{drive}{suffix}.json').write_text(
        json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('experiment', type=Path)
    parser.add_argument('--seed', type=int, default=0)
    parser.add_argument('--drive', type=int, default=0)
    parser.add_argument('--stride', type=int, default=1)
    args = parser.parse_args()
    check(args.experiment, args.seed, args.drive, args.stride)
