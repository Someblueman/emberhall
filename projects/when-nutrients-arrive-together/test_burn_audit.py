import unittest
from burn_audit import compare


class ReplayToleranceTests(unittest.TestCase):
    def test_roundoff_is_distinct_from_changed_evidence(self):
        self.assertLess(compare({'ratios': [1+4e-13]}, {'ratios': [1.]}), 1e-12)
        with self.assertRaisesRegex(ValueError, 'tolerance'):
            compare({'score': 1.001}, {'score': 1.})
        with self.assertRaisesRegex(ValueError, 'keys'):
            compare({}, {'score': 1.})
        with self.assertRaisesRegex(ValueError, 'finite'):
            compare([float('nan')], [1.])


if __name__ == '__main__':
    unittest.main()
