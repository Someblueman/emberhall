"""Unit tests for the offline two-deletion codebook verifier."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))


class VerifyCodebookTests(unittest.TestCase):
    def test_valid_small_codes_and_distinct_output_counts(self):
        import verify

        code_6 = ["000000", "001110", "110001", "111111"]
        report = verify.verify_words(code_6, expected_length=6)
        self.assertEqual(report["count"], 4)
        self.assertEqual(report["length"], 6)
        self.assertEqual(report["pairs_per_word"], 15)
        self.assertGreater(report["total_subsequences"], 0)

    def test_duplicate_word_rejected(self):
        import verify

        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify.verify_words(["000000000000", "000000000000"], expected_length=12)

    def test_wrong_length_and_non_binary_rejected(self):
        import verify

        with self.assertRaisesRegex(ValueError, "length"):
            verify.verify_words(["00000000000"], expected_length=12)
        with self.assertRaisesRegex(ValueError, "binary"):
            verify.verify_words(["000000000002"], expected_length=12)

    def test_shared_two_deletion_subsequence_rejected(self):
        import verify

        with self.assertRaisesRegex(ValueError, "collision"):
            verify.verify_words(["000000000000", "000000000001"], expected_length=12)

    def test_empty_codebook_rejected(self):
        import verify

        with self.assertRaisesRegex(ValueError, "empty"):
            verify.verify_words([], expected_length=12)

    def test_cli_accepts_comments_and_rejects_bad_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp) / "good.txt"
            good.write_text("# comment\n\n000000\n001110\n110001\n111111\n")
            res = subprocess.run(
                [sys.executable, str(PROJECT_DIR / "verify.py"), str(good), "--length", "6"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(res.returncode, 0, res.stderr)
            self.assertIn("PASS", res.stdout)
            self.assertIn("4 words", res.stdout)

            bad = Path(tmp) / "bad.txt"
            bad.write_text("000000\n000001\n")
            res_bad = subprocess.run(
                [sys.executable, str(PROJECT_DIR / "verify.py"), str(bad), "--length", "6"],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(res_bad.returncode, 0)
            self.assertIn("FAIL", res_bad.stdout + res_bad.stderr)

    def test_recorded_12bit_codebook_and_min_size_gate(self):
        codebook = PROJECT_DIR / "codebook_12.txt"
        self.assertTrue(codebook.is_file())

        res_ok = subprocess.run(
            [
                sys.executable,
                str(PROJECT_DIR / "verify.py"),
                str(codebook),
                "--length",
                "12",
                "--min-size",
                "36",
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(res_ok.returncode, 0, res_ok.stderr)
        self.assertIn("PASS: 36 words of length 12", res_ok.stdout)

        res_miss = subprocess.run(
            [
                sys.executable,
                str(PROJECT_DIR / "verify.py"),
                str(codebook),
                "--length",
                "12",
                "--min-size",
                "38",
            ],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(res_miss.returncode, 0)
        self.assertIn("below required minimum 38", res_miss.stderr)


if __name__ == "__main__":
    unittest.main()
