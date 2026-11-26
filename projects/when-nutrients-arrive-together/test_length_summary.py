"""The diagnostic must retain failed communities and reject incomplete evidence."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from summarize_length import load


class ReceiptIntegrity(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.config = dict(communities=list(range(8, 16)), retained=20000,
                           baseline_retained=4096, burn=512, mesh=.0625,
                           tolerance=1e-8, segment=30, supply_seed_offset=20000,
                           code_sha256={name: hashlib.sha256(
                               Path(__file__).with_name(name).read_bytes()).hexdigest()
                               for name in ('reference.py', 'extend_length.py')})
        self.write_protocol()
        for seed in range(8, 16):
            (self.directory / f'seed-{seed}.json').write_text(json.dumps(
                dict(seed=seed, status='failure', error='witnessed solver failure')))

    def write_protocol(self):
        (self.directory / 'protocol.json').write_text(json.dumps(self.config))

    def test_failed_communities_are_not_dropped(self):
        records, hashes = load([self.directory])
        self.assertEqual(set(records), set(range(8, 16)))
        self.assertTrue(all(r['status'] == 'failure' for r in records.values()))
        self.assertEqual(len(hashes), 8)

    def test_absent_receipt_is_not_a_failed_attempt(self):
        (self.directory / 'seed-15.json').unlink()
        with self.assertRaises(FileNotFoundError):
            load([self.directory])

    def test_duplicate_partition_cannot_increase_sample_size(self):
        with self.assertRaisesRegex(ValueError, 'duplicate'):
            load([self.directory, self.directory])

    def test_wrong_identity_is_rejected(self):
        (self.directory / 'seed-8.json').write_text(json.dumps(dict(seed=9, status='failure')))
        with self.assertRaisesRegex(ValueError, 'identity'):
            load([self.directory])

    def test_missing_source_hash_is_rejected(self):
        self.config['code_sha256'].pop('reference.py')
        self.write_protocol()
        with self.assertRaisesRegex(ValueError, 'hashes'):
            load([self.directory])

    def test_failed_prefix_cannot_be_reported_as_success(self):
        (self.directory / 'seed-8.json').write_text(json.dumps(
            dict(seed=8, status='success', prefix_max_error=1e-5)))
        with self.assertRaisesRegex(ValueError, 'prefix'):
            load([self.directory])


if __name__ == '__main__':
    unittest.main()
