"""Fixed first-four-community duration extension, retaining the same OU prefixes."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np

from reference import community, ou, simulate, score
from convergence import difference, stationarity


def extend(study, output):
    config = json.loads((study/'protocol.json').read_text())
    seeds = config['seeds'][:4]  # fixed ordering; never choose by convergence or score
    config = dict(seeds=seeds, input_seed_offset=20000, duration=20512, burn=512,
                  mesh=.0625, rtol=1e-8, windows=[2048,4096,8192,16384,20000],
                  code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  purpose='exploratory record-length extension; four communities do not establish population uncertainty')
    output.mkdir(parents=True,exist_ok=True)
    encoded=json.dumps(config,indent=2,sort_keys=True)+'\n'
    path=output/'protocol.json'
    if path.exists() and path.read_text()!=encoded:
        raise ValueError('different extension protocol')
    path.write_text(encoded)
    for seed in seeds:
        receipt=output/f'seed-{seed}.json'
        if receipt.exists():
            continue
        record=dict(seed=seed,status='failure')
        try:
            uptake,gain,labels=community(seed)
            supply=ou(20000+seed,20512,spacing=.0625)
            if supply.min()<=0:
                raise ValueError('nonpositive supply; no repair')
            x,minimum=simulate(uptake,gain,supply,.0625,20512,512,.0625,1e-8)
            prefix=np.load(study/f'seed-{seed}.npz')['log_x_0.0625']
            prefix_error=float(np.max(np.abs(x[:len(prefix)]-prefix)))
            if prefix_error>1e-6:
                raise ValueError(f'extended trajectory prefix changed by {prefix_error}')
            scores={str(n):score(x[:n],gain,labels) for n in config['windows']}
            np.savez_compressed(output/f'seed-{seed}.npz',log_abundance=x)
            record.update(status='success',scores=scores,minimum_abundance=minimum,
                          prefix_max_error=prefix_error,stationarity=stationarity(x),
                          length_delta=difference(score(x[:10000],gain,labels),scores['20000']),
                          last_half_scores=score(x[10000:],gain,labels))
        except (ValueError,RuntimeError,FloatingPointError) as error:
            record['error']=str(error)
        receipt.write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
        print('long record',seed,record['status'],flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('study',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    extend(args.study,args.output)
