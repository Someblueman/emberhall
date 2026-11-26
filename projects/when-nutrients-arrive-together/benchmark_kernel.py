"""Compare an allocation-light RHS against the frozen simulator in both orders."""
import argparse
import hashlib
import json
import time
from pathlib import Path
from unittest.mock import patch

import numpy as np
import scipy

import reference
from rhs_kernel import rhs as candidate


def run(output):
    config = dict(seeds=[4, 7, 12], duration=1024, burn=128, mesh=.0625,
                  tolerance=1e-8, orders=[['reference', 'candidate'],
                                       ['candidate', 'reference']],
                  numpy=np.__version__, scipy=scipy.__version__,
                  code_sha256={name: hashlib.sha256(
                      Path(__file__).with_name(name).read_bytes()).hexdigest()
                      for name in ('reference.py', 'rhs_kernel.py', 'benchmark_kernel.py')})
    original = reference.rhs
    rows = []
    for seed in config['seeds']:
        uptake, gain, _ = reference.community(seed)
        supply = reference.ou(20000 + seed, 1024, spacing=.0625)
        for order in config['orders']:
            arrays, minimum, times = {}, {}, {}
            for name in order:
                kernel = original if name == 'reference' else candidate
                start_wall, start_cpu = time.perf_counter(), time.process_time()
                with patch.object(reference, 'rhs', kernel):
                    arrays[name], minimum[name] = reference.simulate(
                        uptake, gain, supply, .0625, 1024, 128, .0625, 1e-8)
                times[name] = dict(wall=time.perf_counter() - start_wall,
                                   cpu=time.process_time() - start_cpu)
            error = float(np.max(np.abs(arrays['reference'] - arrays['candidate'])))
            minimum_error = abs(minimum['reference'] - minimum['candidate'])
            row = dict(seed=seed, order=order, seconds=times,
                       maximum_log_error=error, minimum_abundance_error=minimum_error)
            rows.append(row)
            if error > 1e-12 or minimum_error > 1e-12:
                raise ValueError(f'candidate changed the controlled trajectory: {row}')
            print(f'seed {seed}, {order[0]} first: max error {error:g}', flush=True)
    result = dict(protocol=config, comparisons=rows,
                  maximum_log_error=max(r['maximum_log_error'] for r in rows),
                  median_cpu_speedup=float(np.median([
                      r['seconds']['reference']['cpu']/r['seconds']['candidate']['cpu']
                      for r in rows])))
    output.write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps({k: result[k] for k in ('maximum_log_error', 'median_cpu_speedup')}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    run(parser.parse_args().output)
