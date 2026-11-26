"""Deterministic segment-length sensitivity of the stationary linear estimand."""
import argparse
import csv
from pathlib import Path
import numpy as np
from convergence import METRICS,TARGETS
from linear_welch import predictions


def run(output):
    reference={seed:predictions(seed,30) for seed in range(4,16)}
    rows=[]
    for segment in (16,30,60):
        records={seed:predictions(seed,segment) for seed in range(4,16)}
        for metric in METRICS:
            row=dict(segment=segment,metric=metric)
            for target in TARGETS:
                row['mean_'+target]=float(np.mean([r['scores'][metric][target] for r in records.values()]))
                row['max_change_'+target]=float(max(abs(records[seed]['scores'][metric][target]
                                                 -reference[seed]['scores'][metric][target]) for seed in range(4,16)))
            rows.append(row)
    with output.open('w') as stream:
        writer=csv.DictWriter(stream,list(rows[0]));writer.writeheader()
        for row in rows:
            writer.writerow({k:format(v,'.8g') if isinstance(v,float) else v for k,v in row.items()})
    return rows


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();run(args.output)
