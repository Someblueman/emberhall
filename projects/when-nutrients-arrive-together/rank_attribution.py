"""Exact edge-order attribution of a change in overlap Spearman correlation."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.stats import rankdata, spearmanr

from reference import PAIRS, community, measures, score


def attribution(target, before, after):
    """Attribute even tied-rank normalization changes, without assuming no ties.

    r_i - (n+1)/2 = .5 sum_j sign(x_i-x_j). Substitute this identity into
    Pearson correlation of ranks and group terms by unordered comparisons.
    """
    vectors = [np.asarray(v, dtype=float) for v in (target, before, after)]
    if any(v.ndim != 1 or v.shape != vectors[0].shape or not np.isfinite(v).all()
           for v in vectors):
        raise ValueError('need equal finite vectors')
    ranks = [rankdata(v)-(len(v)+1)/2 for v in vectors]
    norms = [np.linalg.norm(v) for v in ranks]
    if min(norms) == 0:
        raise ValueError('constant rank vector')
    records = []
    for i, j in zip(*np.triu_indices(len(target), 1)):
        old_sign = float(np.sign(before[i]-before[j]))
        new_sign = float(np.sign(after[i]-after[j]))
        contribution = ((ranks[0][i]-ranks[0][j])/(2*norms[0])
                        * (new_sign/norms[2]-old_sign/norms[1]))
        records.append(dict(first=int(i), second=int(j), before_sign=old_sign,
                            after_sign=new_sign, before_gap=float(before[i]-before[j]),
                            after_gap=float(after[i]-after[j]),
                            contribution=float(contribution)))
    actual = float(spearmanr(target, after).statistic-spearmanr(target, before).statistic)
    total = float(sum(r['contribution'] for r in records))
    if not np.isclose(total, actual, rtol=0, atol=1e-12):
        raise ValueError('rank attribution does not conserve score change')
    return dict(score_change=actual, attribution_sum=total,
                changed_comparisons=sum(r['before_sign'] != r['after_sign'] for r in records),
                total_comparisons=len(records),
                normalization_changed=not np.isclose(norms[1], norms[2], rtol=0, atol=1e-14),
                comparisons=records)


def analyze(study, output, reference_csv):
    """Post-hoc diagnostic of the pre-existing worst coherence length case."""
    seed, drive = 9, 0
    receipt_path = study/f'community-{seed}-drive-{drive}.json'
    receipt = json.loads(receipt_path.read_text())
    arrays_path = receipt_path.with_suffix('.npz')
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if receipt['status'] != 'success' or digest(arrays_path) != receipt['trajectory_sha256']:
        raise ValueError('unsuccessful or changed replay trajectory')
    if (receipt['community'], receipt['drive']) != (seed, drive):
        raise ValueError('wrong replay identity')
    with np.load(arrays_path, allow_pickle=False) as arrays:
        fine, coarse = arrays['fine'], arrays['coarse']
    if fine.shape != (8192, 6) or coarse.shape != fine.shape:
        raise ValueError('expected frozen 8192-observation replay')
    _, gain, labels = community(seed)
    target = (gain@gain.T)[PAIRS]
    old_measures, new_measures = measures(fine[:4096]), measures(fine)
    old_scores, new_scores, coarse_scores = (score(x, gain, labels)
                                             for x in (fine[:4096], fine, coarse))
    with reference_csv.open() as stream:
        expected = {r['metric']: r for r in csv.DictReader(stream)
                    if int(r['community']) == seed and int(r['drive']) == drive}
    if set(expected) != set(new_scores):
        raise ValueError('missing reference scores')
    errors = []
    for m in new_scores:
        for k in new_scores[m]:
            for prefix, actual in [('scores', new_scores[m][k]),
                                   ('length_delta', new_scores[m][k]-old_scores[m][k]),
                                   ('forcing_delta', new_scores[m][k]-coarse_scores[m][k])]:
                errors.append(abs(float(expected[m][prefix+'_'+k])-actual))
    report = dict(community=seed, drive=drive,
                  selection='post-hoc replay of the largest previously reported coherence length change; not a new population sample',
                  maximum_reference_score_discrepancy=max(errors),
                  reference_agreement_within_1e_8=max(errors) <= 1e-8,
                  reference_csv_sha256=digest(reference_csv), receipt_sha256=digest(receipt_path),
                  protocol_sha256=digest(study/'protocol.json'), exporter_sha256=digest(Path(__file__)),
                  scope='exact score-change attribution on one selected finite path; no stationarity, continuum or population inference',
                  methods={})
    rows = []
    for metric in old_measures:
        result = attribution(target, old_measures[metric], new_measures[metric])
        comparisons = result.pop('comparisons')
        report['methods'][metric] = dict(**result, before_scores=old_scores[metric],
            after_scores=new_scores[metric],
            maximum_raw_measure_change=float(np.abs(new_measures[metric]-old_measures[metric]).max()))
        for row in sorted(comparisons, key=lambda r: -abs(r['contribution']))[:10]:
            row = dict(metric=metric, **row)
            for key in ('first', 'second'):
                edge = row[key]
                row[key+'_species_pair'] = f'{PAIRS[0][edge]}-{PAIRS[1][edge]}'
            rows.append(row)
    output.mkdir(parents=True, exist_ok=True)
    (output/'summary.json').write_text(json.dumps(report, indent=2, allow_nan=False)+'\n')
    with (output/'largest-contributions.csv').open('w') as stream:
        writer = csv.DictWriter(stream, list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--reference-csv', required=True, type=Path)
    args = parser.parse_args()
    report = analyze(args.study, args.output, args.reference_csv)
    print('maximum reference discrepancy', report['maximum_reference_score_discrepancy'])
    for metric, result in report['methods'].items():
        print(metric, 'rank change', result['score_change'], 'changed orders', result['changed_comparisons'])
