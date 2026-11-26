"""Full-tail tolerance diagnostic of one selected path; see TAIL_SOLVER.md."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy

from reference import community, ou, simulate, score
from ou_bridge import bridge

BASELINE_SHA = '5f7b8188229de7a3e1eaf0fabc1e406910b1bf75d7902964a4e12e5333e1fb95'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, value):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    temporary.replace(path)


def baseline(path):
    receipt = json.loads((path/'receipt.json').read_text())
    config = json.loads((path/'protocol.json').read_text())
    if receipt['status'] != 'success' or receipt['protocol_sha256'] != digest(path/'protocol.json'):
        raise ValueError('baseline receipt/protocol mismatch')
    if receipt['trajectory_sha256'] != BASELINE_SHA or digest(path/'trajectory.npz') != BASELINE_SHA:
        raise ValueError('changed or wrong selected baseline trajectory')
    expected = dict(community=9, drive=0, input_seed=80900, bridge_seed=90900,
                    duration=66048, burn=512, spacing=1/32, max_step=1/32, rtol=1e-9)
    if any(config.get(k) != v for k, v in expected.items()):
        raise ValueError('wrong baseline settings')
    with np.load(path/'trajectory.npz', allow_pickle=False) as saved:
        x = saved['log_abundance']
    if x.shape != (65536, 6) or not np.isfinite(x).all():
        raise ValueError('invalid baseline array')
    return x


def run(old, output):
    previous = baseline(old)
    output.mkdir(parents=True, exist_ok=True)
    config = dict(community=9, drive=0, input_seed=80900, bridge_seed=90900,
                  duration=66048, burn=512, coarse_spacing=1/16, spacing=1/32,
                  max_step=1/32, rtol=1e-11, solver_margin=.005,
                  lengths=[4096, 8192, 16384, 32768, 65536],
                  baseline_sha256=BASELINE_SHA,
                  baseline_receipt_sha256=digest(old/'receipt.json'),
                  baseline_protocol_sha256=digest(old/'protocol.json'),
                  numpy=np.__version__, scipy=scipy.__version__,
                  sources={n: digest(Path(__file__).with_name(n)) for n in
                           ('tail_solver.py', 'reference.py', 'ou_bridge.py')},
                  scope='One selected development path; tolerance sensitivity only; original gates unchanged')
    protocol = output/'protocol.json'
    if protocol.exists() and json.loads(protocol.read_text()) != config:
        raise ValueError('changed frozen protocol')
    if not protocol.exists():
        write(protocol, config)
    receipt = output/'receipt.json'
    if receipt.exists():
        result = json.loads(receipt.read_text())
        if result['protocol_sha256'] != digest(protocol):
            raise ValueError('changed receipt protocol')
        if result['status'] == 'success' and digest(output/'trajectory.npz') != result['trajectory_sha256']:
            raise ValueError('changed result trajectory')
        return result
    started = time.monotonic()
    result = dict(status='failure', protocol_sha256=digest(protocol))
    try:
        coarse = ou(80900, 66048, 1/16)
        fine = bridge(coarse, 1/16, 90900)
        if fine.min() <= 0 or not np.array_equal(fine[::2], coarse):
            raise ValueError('nonpositive supply or changed endpoints')
        del coarse
        uptake, gain, labels = community(9)
        x, minimum = simulate(uptake, gain, fine, 1/32, 66048, 512, 1/32, 1e-11)
        del fine
        np.savez_compressed(output/'trajectory.npz', log_abundance=x)
        result.update(status='success', trajectory_sha256=digest(output/'trajectory.npz'),
                      minimum_abundance=minimum, windows={})
        for n in config['lengths']:
            a, b = score(previous[:n], gain, labels), score(x[:n], gain, labels)
            delta = {m: {t: abs(b[m][t]-a[m][t]) for t in a[m]} for m in a}
            result['windows'][str(n)] = dict(baseline=a, refined=b, absolute_delta=delta,
                maximum_log_error=float(np.abs(x[:n]-previous[:n]).max()),
                rms_log_error=float(np.sqrt(np.mean((x[:n]-previous[:n])**2))),
                inside_original_solver_margin=all(d <= .005 for v in delta.values() for d in v.values()))
    except (ValueError, RuntimeError, FloatingPointError) as error:
        result.update(status='failure', error=str(error))
    result['elapsed_seconds'] = time.monotonic()-started
    write(receipt, result)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.baseline, args.output)
    print(json.dumps({k: v for k, v in result.items() if k != 'windows'}))
