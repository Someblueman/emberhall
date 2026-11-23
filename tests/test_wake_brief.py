import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import wake_brief  # noqa: E402


def ev(seq, op="say", actor="resident-abcdef1234567890", **data):
    return {"sequence": seq, "op": op, "actor": actor, "data": data}


def page(through, latest, events, has_more=None):
    return {"through": through, "latest": latest,
            "has_more": (through < latest) if has_more is None else has_more,
            "events": events}


def journal_fetch(latest, calls):
    """Dense journal 1..latest; fetch honours after/limit like `read`."""

    def fetch(after, limit):
        calls.append((after, limit))
        seqs = list(range(after + 1, min(latest, after + limit) + 1))
        return page(seqs[-1] if seqs else after, latest,
                    [ev(s, text=f"event {s}") for s in seqs])

    return fetch


class RecentWindowTests(unittest.TestCase):
    def test_default_shows_recent_window_not_oldest(self):
        calls = []
        out = wake_brief.run(journal_fetch(34663, calls), None,
                             window=40, limit=20, max_pages=10)
        lines = out.splitlines()
        self.assertIn("journal latest 34663", lines[0])
        self.assertIn("window through 34663", lines[0])
        self.assertTrue(lines[1].startswith("34624 "), lines[1])
        self.assertEqual(calls[0], (0, 1))  # probe only reads latest
        self.assertEqual(calls[1][0], 34663 - 40)
        self.assertNotIn("\n1 say", out)

    def test_default_window_clamps_at_journal_start(self):
        calls = []
        out = wake_brief.run(journal_fetch(5, calls), None,
                             window=40, limit=20, max_pages=10)
        self.assertIn("showing 5 event(s) 1..5", out.splitlines()[0])

    def test_explicit_after_still_works_and_skips_probe(self):
        calls = []
        out = wake_brief.run(journal_fetch(105, calls), 100,
                             window=40, limit=20, max_pages=10)
        self.assertEqual(calls[0], (100, 20))
        self.assertIn("showing 5 event(s) 101..105", out.splitlines()[0])


class LatestVsThroughTests(unittest.TestCase):
    """Regression: latest greater than through must never read as head."""

    def test_saved_page_with_latest_above_through(self):
        saved = page(18329, 34663,
                     [ev(18328, text="old"), ev(18329, text="older")])
        lines, through, latest = wake_brief.brief_pages([saved])
        self.assertEqual((through, latest), (18329, 34663))
        self.assertIn("journal latest 34663", lines[0])
        self.assertIn("window through 18329", lines[0])
        self.assertIn("window ends before latest", lines[0])
        self.assertNotIn("head", lines[0].lower().replace("ahead", ""))

    def test_page_bound_stops_before_latest_and_says_next(self):
        calls = []
        out = wake_brief.run(journal_fetch(500, calls), 0,
                             window=40, limit=10, max_pages=2)
        lines = out.splitlines()
        self.assertIn("journal latest 500", lines[0])
        self.assertIn("window through 20", lines[0])
        self.assertIn("480 newer", lines[0])
        self.assertEqual(lines[-1],
                         "next: read --after 20 "
                         "(reading has acknowledged nothing)")

    def test_caught_up_window_has_no_next_line(self):
        out = wake_brief.run(journal_fetch(3, []), 0,
                             window=40, limit=20, max_pages=10)
        self.assertNotIn("next: read", out)
        self.assertNotIn("window ends before latest", out)

    def test_empty_window_still_reports_latest(self):
        out = wake_brief.run(journal_fetch(7, []), 7,
                             window=40, limit=20, max_pages=10)
        self.assertIn("journal latest 7; showing 0 event(s) none",
                      out.splitlines()[0])


class ValidationTests(unittest.TestCase):
    def test_missing_latest_is_an_error_not_a_guess(self):
        bad = {"through": 2, "has_more": False,
               "events": [ev(1, text="x"), ev(2, text="y")]}
        with self.assertRaises(ValueError):
            wake_brief.brief_pages([bad])

    def test_overlapping_pages_rejected(self):
        pages = [page(102, 105, [ev(101), ev(102)]),
                 page(103, 105, [ev(102), ev(103)])]
        with self.assertRaises(ValueError):
            wake_brief.brief_pages(pages)

    def test_negative_after_rejected(self):
        with self.assertRaises(ValueError):
            wake_brief.run(journal_fetch(9, []), -1, 40, 20, 10)


class MainTests(unittest.TestCase):
    def test_page_mode_from_file(self):
        import contextlib
        import io
        import json
        import tempfile

        saved = page(18329, 34663, [ev(18329, text="seen at wake")])
        with tempfile.NamedTemporaryFile(
                "w", suffix=".json", delete=False) as fh:
            json.dump(saved, fh)
            path = fh.name
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = wake_brief.main(["--page", path])
        self.assertEqual(rc, 0)
        self.assertIn("journal latest 34663", buf.getvalue())
        self.assertIn("next: read --after 18329", buf.getvalue())

    def test_live_mode_needs_resident(self):
        self.assertEqual(wake_brief.main([]), 2)


if __name__ == "__main__":
    unittest.main()
