import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))

from bfs_verify import verify
from exact_completion import attempt, main, supports_in_order, target_size


class ExactCompletionTests(unittest.TestCase):
    def test_tip_support_witness_is_bfs_verified(self):
        summary = attempt((45, 20, 8))
        self.assertEqual(summary["status"], "witness")
        self.assertEqual(summary["size"], 36)
        self.assertEqual(summary["omitted"], [[1, 45], [2, 20]])
        self.assertEqual(summary["supports_tried"], 1)
        self.assertEqual(verify(summary["payload"]),
                         {"ok": True, "size": 36, "difference": {}})

    def test_pool_fallback_after_tip_support_obstruction(self):
        # (50,30,5): the tip support is exactly obstructed; the pool's
        # (1,50),(3,5) support carries a witness (GRID_EXACT_COMPLETION.md).
        only_tips = attempt((50, 30, 5), use_pool=False)
        self.assertEqual(only_tips["status"], "no_witness_on_tried_supports")
        self.assertEqual(only_tips["verdicts"], {"support_obstructed": 1,
                                                 "inconclusive": 0})
        self.assertFalse(only_tips["all_omissions_obstructed"])
        summary = attempt((50, 30, 5))
        self.assertEqual(summary["status"], "witness")
        self.assertEqual(summary["omitted"], [[1, 50], [3, 5]])
        self.assertTrue(verify(summary["payload"])["ok"])

    def test_support_order_starts_with_tips_and_has_no_repeats(self):
        supports = list(supports_in_order((10, 7, 4)))
        self.assertEqual(supports[0], [(1, 10), (2, 7)])
        as_tuples = [tuple(s) for s in supports]
        self.assertEqual(len(as_tuples), len(set(as_tuples)))

    def test_cli_writes_witness_and_rejects_bad_lengths(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "w.json"
            rc = main(["55", "20", "5", "--out", str(out)])
            self.assertEqual(rc, 0)
            payload = json.loads(out.read_text())
            self.assertEqual(verify(payload)["size"], target_size((55, 20, 5)))
        with self.assertRaises(SystemExit):
            main(["0", "2", "1"])


if __name__ == "__main__":
    unittest.main()
