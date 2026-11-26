"""Outcome-selected seed-14 failure investigation; not a population convergence test."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy

from reference import community, ou, simulate, score


def run(study, output):
    with np.load(study / 'seed-14.npz') as data:
        prefix = data['log_x']
    if prefix.shape != (20000, 6):
        raise ValueError('the recorded 20000-observation witness is required')
    config = dict(seed=14, supply_seed=20014, retained=65536, burn=512,
                  mesh=.0625, tolerance=1e-8, segment=30,
                  windows=[20000, 32768, 40000, 65536],
                  selection='largest observed correlation half-to-full rank change among communities 8–15',
                  purpose='exploratory single-witness diagnosis; not population acceptance',
                  prefix_sha256=hashlib.sha256(prefix.tobytes()).hexdigest(),
                  numpy=np.__version__, scipy=scipy.__version__,
                  code_sha256={name: hashlib.sha256(
                      Path(__file__).with_name(name).read_bytes()).hexdigest()
                      for name in ('reference.py', 'extend_witness.py')})
    output.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(config, indent=2, sort_keys=True) + '\n'
    protocol = output / 'protocol.json'
    if protocol.exists() and protocol.read_text() != encoded:
        raise ValueError('different witness protocol already exists')
    protocol.write_text(encoded)
    receipt = output / 'seed-14.json'
    if receipt.exists():
        return
    record = dict(seed=14, status='failure')
    try:
        uptake, gain, labels = community(14)
        supply = ou(20014, 66048, spacing=.0625)
        record['minimum_supply'] = float(supply.min())
        if supply.min() <= 0:
            raise ValueError('nonpositive supply; no repair')
        x, minimum = simulate(uptake, gain, supply, .0625, 66048, 512, .0625, 1e-8)
        record['prefix_max_error'] = float(np.max(np.abs(x[:20000]-prefix)))
        if record['prefix_max_error'] > 1e-6:
            raise ValueError('witness prefix changed')
        record.update(status='success', minimum_abundance=minimum,
                      scores={str(n): score(x[:n], gain, labels) for n in config['windows']},
                      second_half_scores=score(x[32768:], gain, labels))
        np.savez_compressed(output / 'seed-14.npz', log_x=x, gain=gain, labels=labels)
    except (ValueError, RuntimeError, FloatingPointError) as error:
        record['error'] = str(error)
    receipt.write_text(json.dumps(record, indent=2, allow_nan=False) + '\n')
    print(f'seed 14 witness: {record["status"]}', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run(args.study, args.output)
