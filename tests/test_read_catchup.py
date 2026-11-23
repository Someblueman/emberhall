import contextlib
import io
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import read_catchup  # noqa: E402


def ev(seq, op="say", actor="resident-abcdef1234567890", **data):
    return {"sequence": seq, "op": op, "actor": actor, "data": data}


PAGE1 = {"through": 102, "has_more": True, "latest": 105, "events": [
    ev(101, text="first catch-up line " + "x" * 300),
    ev(102, "life", "watch-keeper", kind="run-finish",
       run="deadbeefcafe", outcome="success"),
]}
PAGE2 = {"through": 104, "has_more": True, "latest": 105, "events": [
    ev(103, claim="some-task", seconds=1800),
    ev(104, "shelf", idea="some-idea", kind="idea-brief"),
]}
PAGE3 = {"through": 105, "has_more": False, "latest": 105, "events": [
    ev(105, "sleep", note="caught up; next useful action is the tool"),
]}


def fake_fetch(pages):
    calls = []

    def fetch(after, limit):
        calls.append(after)
        for page in pages:
            if page["through"] > after:
                return page
        return {"through": after, "has_more": False, "latest": after,
                "events": []}

    fetch.calls = calls  # type: ignore[attr-defined]
    return fetch


class MergePagesTests(unittest.TestCase):
    def test_merges_saved_pages_in_order(self):
        lines, through, has_more, latest, count = read_catchup.merge_pages(
            [PAGE1, PAGE2, PAGE3])
        self.assertEqual(count, 5)
        self.assertEqual(through, 105)
        self.assertFalse(has_more)
        self.assertEqual(latest, 105)
        self.assertEqual(len(lines), 5)
        self.assertTrue(lines[0].startswith("101 say abcdef12 first catch-up"))
        self.assertIn("…", lines[0])  # long text marked shortened
        self.assertEqual(lines[1],
                         "102 life watch-keeper [run-finish] run=deadbeef success")
        self.assertEqual(lines[2], "103 say abcdef12 some-task")
        self.assertIn("105 sleep", lines[4])

    def test_rejects_overlap_between_saved_pages(self):
        stale = {"through": 103, "has_more": False, "latest": 103,
                 "events": [ev(101, text="re-read"), ev(103, text="again")]}
        with self.assertRaises(ValueError):
            read_catchup.merge_pages([PAGE1, stale])

    def test_rejects_empty_page_list(self):
        with self.assertRaises(ValueError):
            read_catchup.merge_pages([])

    def test_main_merges_saved_pages(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            paths = []
            for i, page in enumerate((PAGE1, PAGE2, PAGE3)):
                path = Path(tmp) / f"page{i}.json"
                path.write_text(json.dumps(page), encoding="utf-8")
                paths.append(str(path))
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                rc = read_catchup.main(["--page", *paths])
            self.assertEqual(rc, 0)
            text = out.getvalue()
            self.assertIn("101 say", text)
            self.assertIn("105 sleep", text)
            self.assertIn("through 105 has_more False latest 105 pages 3 "
                          "events 5", text)
            self.assertNotIn("next:", text)


class CatchUpTests(unittest.TestCase):
    def test_pages_to_head_and_stops(self):
        fetch = fake_fetch([PAGE1, PAGE2, PAGE3])
        seen = list(read_catchup.catch_up(fetch, 100, 20, 25))
        self.assertEqual([t for _, t, _, _ in seen], [102, 104, 105])
        self.assertEqual(fetch.calls, [100, 102, 104])  # type: ignore[attr-defined]
        self.assertFalse(seen[-1][2])

    def test_stops_at_max_pages(self):
        fetch = fake_fetch([PAGE1, PAGE2, PAGE3])
        seen = list(read_catchup.catch_up(fetch, 100, 20, 2))
        self.assertEqual(len(seen), 2)
        self.assertTrue(seen[-1][2])  # more remains

    def test_stuck_cursor_errors_instead_of_looping(self):
        def fetch(after, limit):
            return {"through": after, "has_more": True, "latest": 999,
                    "events": []}

        with self.assertRaises(ValueError):
            list(read_catchup.catch_up(fetch, 50, 20, 25))

    def test_page_at_or_before_cursor_errors(self):
        def fetch(after, limit):
            return {"through": after + 1, "has_more": False, "latest": after + 1,
                    "events": [ev(after, text="old")]}

        with self.assertRaises(ValueError):
            list(read_catchup.catch_up(fetch, 50, 20, 25))

    def test_live_failure_reports_cursor_and_exits_two(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = read_catchup.main(["--client", "/nonexistent-house-client-xyz",
                                    "--as", "resident-test", "--after", "7"])
        self.assertEqual(rc, 2)
        self.assertIn("through 7", err.getvalue())

    def test_live_mode_needs_as_and_after(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            rc = read_catchup.main([])
        self.assertEqual(rc, 2)


if __name__ == "__main__":
    unittest.main()
