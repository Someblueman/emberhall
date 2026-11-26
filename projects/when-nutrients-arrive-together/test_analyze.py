import json
from pathlib import Path
import tempfile
import unittest

from analyze import analyze
from convergence import METRICS, TARGETS, protocol


class ReceiptChecks(unittest.TestCase):
    def prepare(self, directory):
        directory.mkdir()
        (directory/'protocol.json').write_text(json.dumps(protocol(range(2),4608,512)))
        values={m:{k:.8 for k in TARGETS} for m in METRICS}
        zero={m:{k:0.0 for k in TARGETS} for m in METRICS}
        for seed in range(2):
            r=dict(seed=seed,status='success',
                   scores={str(mesh):{str(segment):values for segment in (16,30,60)}
                           for mesh in (.25,.125,.0625)},
                   coarse_forcing_delta=zero,finest_forcing_delta=zero,
                   solver_delta=zero,length_delta=zero)
            (directory/f'seed-{seed}.json').write_text(json.dumps(r))

    def test_complete_receipts_keep_provenance_and_all_targets(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)/'data'; self.prepare(directory)
            result=analyze(directory,Path(temporary)/'out')
            self.assertEqual(set(result['receipt_sha256']),{'0','1'})
            self.assertEqual(len(result['protocol_sha256']),64)
            self.assertEqual(len(result['summaries']['coherence']),3)
            self.assertEqual(len((Path(temporary)/'out'/'community-scores.csv').read_text().splitlines()),9)

    def test_mismatched_identity_or_invalid_score_cannot_be_summarized(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory=Path(temporary)/'data'; self.prepare(directory)
            receipt=directory/'seed-1.json'; r=json.loads(receipt.read_text())
            r['seed']=77; receipt.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'identities'):
                analyze(directory,Path(temporary)/'out')
            r['seed']=1; r['scores']['0.0625']['30']['coherence']['same_diet_pair_auc']=1.1
            receipt.write_text(json.dumps(r))
            with self.assertRaisesRegex(ValueError,'invalid score'):
                analyze(directory,Path(temporary)/'out')
