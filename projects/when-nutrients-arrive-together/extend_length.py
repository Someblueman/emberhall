"""Extend all remaining development communities; never changes frozen gates."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy

from reference import community, ou, simulate, score


def run(output, seeds):
    output.mkdir(parents=True, exist_ok=True)
    config = dict(communities=list(seeds), supply_seed_offset=20000,
                  retained=20000, baseline_retained=4096, burn=512,
                  mesh=0.0625, tolerance=1e-8, segment=30,
                  numpy=np.__version__, scipy=scipy.__version__,
                  code_sha256={name: hashlib.sha256(
                      Path(__file__).with_name(name).read_bytes()).hexdigest()
                      for name in ('reference.py', 'extend_length.py')})
    encoded = json.dumps(config, indent=2, sort_keys=True) + '\n'
    protocol = output / 'protocol.json'
    if protocol.exists() and protocol.read_text() != encoded:
        raise ValueError('different protocol already exists')
    protocol.write_text(encoded)
    for seed in seeds:
        receipt = output / f'seed-{seed}.json'
        if receipt.exists():
            continue
        record = dict(seed=seed, status='failure')
        try:
            uptake, gain, labels = community(seed)
            supply = ou(20000 + seed, 20512, spacing=.0625)
            record['minimum_supply'] = float(supply.min())
            if supply.min() <= 0:
                raise ValueError('nonpositive supply; no repair')
            short, _ = simulate(uptake, gain, supply[:4608*16+1],
                                .0625, 4608, 512, .0625, 1e-8)
            long, minimum = simulate(uptake, gain, supply,
                                     .0625, 20512, 512, .0625, 1e-8)
            record['prefix_max_error'] = float(np.max(np.abs(short-long[:4096])))
            if record['prefix_max_error'] > 1e-6:
                raise ValueError('independent short solve disagrees with prefix')
            scores = {str(n): score(long[:n], gain, labels)
                      for n in (2048, 4096, 8192, 10000, 16384, 20000)}
            record.update(status='success', minimum_abundance=minimum,
                          scores=scores, second_half_scores=score(long[10000:], gain, labels))
            np.savez_compressed(output / f'seed-{seed}.npz', log_x=long,
                                uptake=uptake, gain=gain, labels=labels)
        except (ValueError, RuntimeError, FloatingPointError) as error:
            record['error'] = str(error)
        receipt.write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
        print(f'seed {seed}: {record["status"]}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--start', type=int, default=8)
    parser.add_argument('--count', type=int, default=8)
    args = parser.parse_args()
    if args.count < 1 or args.start < 8 or args.start + args.count > 16:
        parser.error('only the remaining development communities 8–15 are allowed')
    run(args.output, range(args.start, args.start + args.count))
