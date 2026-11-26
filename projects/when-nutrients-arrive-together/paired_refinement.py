"""Replicated conditional-OU refinement; see PAIRED_REFINEMENT.md."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
import scipy

from reference import community, ou, simulate, score, interval
from convergence import METRICS, TARGETS, difference, stationarity
from ou_bridge import bridge


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')
    temporary.replace(path)


def configuration():
    return dict(version=1, communities=list(range(4, 16)), drives=[0, 1],
                input_seed='80000 + 100 * community + drive',
                bridge_seed='90000 + 100 * community + drive',
                duration=8704, burn=512, meshes=[1/16, 1/32],
                max_step=1/32, rtol=1e-9, segments=[16, 30, 60], primary_segment=30,
                lengths=[4096, 8192], initial='all consumer and resource amounts one',
                solver_check=dict(community=4, drive=0, max_step=1/64, rtol=1e-11),
                scope='adaptive development diagnostic; original gates unchanged; held-out unused',
                versions=dict(numpy=np.__version__, scipy=scipy.__version__),
                code_sha256={name: digest(Path(__file__).with_name(name)) for name in
                    ('paired_refinement.py', 'reference.py', 'convergence.py',
                     'ou_bridge.py', 'paired_crosscheck.py')})


def freeze(output):
    output.mkdir(parents=True, exist_ok=True)
    config = configuration()
    path = output/'protocol.json'
    if path.exists():
        if json.loads(path.read_text()) != config:
            raise ValueError('configuration differs from frozen protocol')
    else:
        write_json(path, config)
    return config, digest(path)


def validate(row, seed, drive, protocol_hash):
    if (row.get('community'), row.get('drive'), row.get('protocol_sha256')) != (seed, drive, protocol_hash):
        raise ValueError('receipt identity/protocol mismatch')
    if row.get('input_seed') != 80000+100*seed+drive or row.get('bridge_seed') != 90000+100*seed+drive:
        raise ValueError('receipt seed mismatch')
    if row.get('status') not in ('success', 'failure'):
        raise ValueError('invalid receipt status')
    if row['status'] == 'success':
        for field in ('scores', 'forcing_delta', 'length_delta', 'segment_delta'):
            tables = row[field].values() if field == 'segment_delta' else [row[field]]
            for table in tables:
                for metric in METRICS:
                    for target in TARGETS:
                        if not np.isfinite(table[metric][target]):
                            raise ValueError('nonfinite score')
        if not row['endpoints_exact']:
            raise ValueError('bridge changed an endpoint')
    return row


def evaluate(seed, drive, config, protocol_hash, output):
    row = dict(community=seed, drive=drive, protocol_sha256=protocol_hash,
               input_seed=80000+100*seed+drive, bridge_seed=90000+100*seed+drive,
               status='failure')
    started = time.monotonic()
    try:
        uptake, gain, labels = community(seed)
        coarse = ou(row['input_seed'], config['duration'], config['meshes'][0])
        fine = bridge(coarse, config['meshes'][0], row['bridge_seed'])
        row['endpoints_exact'] = bool(np.array_equal(fine[::2], coarse))
        row['minimum_supply'] = float(min(coarse.min(), fine.min()))
        if row['minimum_supply'] <= 0 or not row['endpoints_exact']:
            raise ValueError('nonpositive supply or modified endpoints; no repair')
        paths = []
        row['minimum_abundance'] = []
        for mesh, supply in zip(config['meshes'], (coarse, fine)):
            x, minimum = simulate(uptake, gain, supply, mesh, config['duration'],
                                  config['burn'], config['max_step'], config['rtol'])
            paths.append(x)
            row['minimum_abundance'].append(minimum)
            print('mesh complete', seed, drive, mesh, round(time.monotonic()-started, 1), flush=True)
        a, b = paths
        full = score(b, gain, labels)
        row.update(scores=full, coarse_scores=score(a, gain, labels),
                   short_scores=score(b[:config['lengths'][0]], gain, labels),
                   second_half_scores=score(b[config['lengths'][0]:], gain, labels),
                   stationarity=stationarity(b), log_rms=float(np.sqrt(np.mean((b-a)**2))),
                   segment_delta={str(n): difference(full, score(b, gain, labels, n))
                                  for n in (16, 60)})
        row['forcing_delta'] = difference(row['coarse_scores'], full)
        row['length_delta'] = difference(row['short_scores'], full)
        check = config['solver_check']
        if (seed, drive) == (check['community'], check['drive']):
            row['solver_checks'] = []
            for mesh, supply, old in zip(config['meshes'], (coarse, fine), paths):
                tight, _ = simulate(uptake, gain, supply, mesh, config['duration'],
                                    config['burn'], check['max_step'], check['rtol'])
                row['solver_checks'].append(dict(mesh=mesh,
                    log_rms=float(np.sqrt(np.mean((tight-old)**2))),
                    score_delta=difference(score(old, gain, labels), score(tight, gain, labels))))
        array_path = output/f'community-{seed}-drive-{drive}.npz'
        np.savez_compressed(array_path, coarse=a, fine=b)
        row.update(status='success', trajectory_sha256=digest(array_path))
    except (ValueError, RuntimeError, FloatingPointError) as error:
        row['error'] = str(error)
    row['elapsed_seconds'] = time.monotonic()-started
    return row


def summarize(rows, config):
    identities = [(r['community'], r['drive']) for r in rows]
    planned = {(s, d) for s in config['communities'] for d in config['drives']}
    if len(set(identities)) != len(identities) or not set(identities) <= planned:
        raise ValueError('duplicate or unplanned realization')
    groups = {s: [r for r in rows if r['community'] == s] for s in config['communities']}
    complete = {s: rr for s, rr in groups.items()
                if len(rr) == len(config['drives']) and all(r['status'] == 'success' for r in rr)}
    summaries = {}
    for field in ('scores', 'forcing_delta', 'length_delta'):
        summaries[field] = {}
        for metric in METRICS:
            summaries[field][metric] = {}
            for target in TARGETS:
                values = [float(np.mean([r[field][metric][target] for r in rr]))
                          for rr in complete.values()]
                if not values:
                    continue
                stat = interval(values)
                width = (2 if target == 'overlap_spearman' else 1) * (1 if field == 'scores' else 2)
                stat['hoeffding_marginal_radius95'] = float(width*np.sqrt(np.log(40)/(2*len(values))))
                stat['maximum_individual_absolute_value'] = max(abs(r[field][metric][target])
                    for rr in complete.values() for r in rr)
                if field != 'scores':
                    stat['communities_with_any_margin_exceedance'] = sum(any(
                        abs(r[field][metric][target]) > ((.05 if target == 'overlap_spearman' else .03)
                        if field == 'forcing_delta' else (.1 if target == 'overlap_spearman' else .05))
                        for r in rr) for rr in complete.values())
                summaries[field][metric][target] = stat
    return dict(planned=len(planned), attempted=len(rows), complete=len(rows)==len(planned),
                complete_communities=len(complete), failures=[r for r in rows if r['status']=='failure'],
                summaries=summaries,
                caveat='Development diagnostic, not clean-baseline acceptance. Communities are independent units; paths and windows are not. Marginal t intervals are approximate; Hoeffding bounds are conservative and not simultaneous. Failure excludes its entire community from conditional means.')


def run(output, start=4, stop=16, report_only=False):
    config, protocol_hash = freeze(output)
    if not 4 <= start < stop <= 16:
        raise ValueError('partition must stay within development communities 4..15')
    for seed in range(start, stop):
        for drive in config['drives']:
            receipt = output/f'community-{seed}-drive-{drive}.json'
            if receipt.exists():
                row = validate(json.loads(receipt.read_text()), seed, drive, protocol_hash)
                if row['status'] == 'success' and digest(output/f'community-{seed}-drive-{drive}.npz') != row['trajectory_sha256']:
                    raise ValueError('trajectory hash mismatch')
            elif not report_only:
                row = evaluate(seed, drive, config, protocol_hash, output)
                validate(row, seed, drive, protocol_hash)
                write_json(receipt, row)
                print('receipt', seed, drive, row['status'], flush=True)
    rows = []
    for seed in config['communities']:
        for drive in config['drives']:
            path = output/f'community-{seed}-drive-{drive}.json'
            if path.exists():
                rows.append(validate(json.loads(path.read_text()), seed, drive, protocol_hash))
    report = summarize(rows, config)
    # Partitions have private summaries; final report-only gathers all receipts.
    name = 'summary.json' if report_only else f'summary-{start}-{stop}.json'
    write_json(output/name, report)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--start', type=int, default=4)
    parser.add_argument('--stop', type=int, default=16)
    parser.add_argument('--report-only', action='store_true')
    args = parser.parse_args()
    run(args.output, args.start, args.stop, args.report_only)
