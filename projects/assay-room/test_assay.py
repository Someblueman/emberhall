"""Tests for the standalone Assay Room review and integration auditor."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ASSAY_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(ASSAY_DIR))

import assay  # noqa: E402


def sample_events() -> list[dict]:
    return [
        {"sequence": 1, "at": 1000.0, "actor": "resident-a", "op": "arrive", "data": {"name": "Yarrow"}},
        {"sequence": 2, "at": 1001.0, "actor": "resident-b", "op": "arrive", "data": {"name": "Mallow"}},
        {"sequence": 3, "at": 1002.0, "actor": "resident-c", "op": "arrive", "data": {"name": "Fern"}},
        {
            "sequence": 4, "at": 1010.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-start", "run": "run-work-1", "resident": "resident-a", "agent": "agy", "model": "gemini-4"},
        },
        {
            "sequence": 5, "at": 1011.0, "actor": "watch-keeper", "op": "say",
            "data": {"text": 'house-assignment-v1 {"run": "run-work-1", "lane": "work", "reason": "balanced"}'},
        },
        {
            "sequence": 6, "at": 1020.0, "actor": "resident-a", "op": "finish",
            "data": {"task": "site-polish", "token": "t1", "artifacts": {"site/house.js": {"sha256": "aaa"}}},
        },
        {
            "sequence": 7, "at": 1030.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-finish", "run": "run-work-1", "outcome": "success"},
        },
        {
            "sequence": 8, "at": 1031.0, "actor": "watch-keeper", "op": "life",
            "data": {
                "kind": "help", "request": "source-review-run-work-1", "review_run": "run-work-1",
                "reason": "Review run-work-1",
            },
        },
        {
            "sequence": 9, "at": 1032.0, "actor": "watch-keeper", "op": "life",
            "data": {
                "kind": "run-start", "run": "run-rev-1", "resident": "resident-b",
                "agent": "codex", "model": "gpt-6.1-sol", "help_request": "source-review-run-work-1",
            },
        },
        {
            "sequence": 10, "at": 1033.0, "actor": "watch-keeper", "op": "say",
            "data": {"text": 'house-assignment-v1 {"run": "run-rev-1", "lane": "review", "reason": "balanced", "help_request": "source-review-run-work-1"}'},
        },
        {
            "sequence": 11, "at": 1040.0, "actor": "resident-b", "op": "say",
            "data": {"text": 'house-integration-v1 {"actor": "resident-b", "run": "run-work-1", "base": "1111", "contribution": "2222", "status": "rejected", "reason": "Missing gap regression."}'},
        },
        {
            "sequence": 12, "at": 1041.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "help-resolved", "request": "source-review-run-work-1", "reason": "terminal receipt"},
        },
        {
            "sequence": 13, "at": 1050.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-start", "run": "run-work-2", "resident": "resident-b", "agent": "codex", "model": "gpt-6.1-sol"},
        },
        {
            "sequence": 14, "at": 1060.0, "actor": "resident-b", "op": "finish",
            "data": {"task": "site-polish-repair", "token": "t2", "artifacts": {"site/house.js": {"sha256": "bbb"}}},
        },
        {
            "sequence": 15, "at": 1065.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-finish", "run": "run-work-2", "outcome": "success"},
        },
        {
            "sequence": 16, "at": 1066.0, "actor": "watch-keeper", "op": "life",
            "data": {
                "kind": "help", "request": "source-review-run-work-2", "review_run": "run-work-2",
                "reason": "Review run-work-2",
            },
        },
        {
            "sequence": 17, "at": 1075.0, "actor": "resident-c", "op": "say",
            "data": {"text": 'house-integration-v1 {"actor": "resident-c", "run": "run-work-2", "base": "1111", "contribution": "3333", "candidate_head": "4444", "status": "integrated", "test_scope": "foundation", "test_exit": 0}'},
        },
        {
            "sequence": 18, "at": 1076.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "help-resolved", "request": "source-review-run-work-2", "reason": "terminal receipt"},
        },
        {
            "sequence": 19, "at": 1080.0, "actor": "watch-keeper", "op": "say",
            "data": {"text": 'house-source-delivery-v1 {"commit": "4444", "remote_main": "4444", "repository": "Someblueman/emberhall"}'},
        },
        {
            "sequence": 20, "at": 1090.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-start", "run": "run-work-3", "resident": "resident-a", "agent": "agy", "model": "gemini-4"},
        },
        {
            "sequence": 21, "at": 1095.0, "actor": "resident-a", "op": "finish",
            "data": {"task": "assay-room", "token": "t3", "artifacts": {"projects/assay-room/assay.py": {"sha256": "ccc"}}},
        },
        {
            "sequence": 22, "at": 1100.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "help", "request": "source-review-run-work-3", "review_run": "run-work-3", "reason": "Review run-work-3"},
        },
    ]


class AssayToolTests(unittest.TestCase):
    def test_run_scars_require_result_receipts_and_keep_the_first_recorded_scar(self):
        for legacy in (False, True):
            def event(kind, **fields):
                data = {"kind": kind, "run": "recovered", **fields}
                return {"actor": "watch-keeper", "op": "say" if legacy else "life",
                        "data": {"text": "house-watch-v1 " + json.dumps(data)} if legacy else data}

            start = event("start" if legacy else "run-start", resident="author", agent="codex")
            recovered = event("recovered-interruption", outcome="success")
            for receipts, expected in (
                ([], (0, 0, 0)),
                ([recovered], (0, 0, 1)),
                ([recovered, recovered], (0, 0, 1)),
                ([recovered, event("run-finish", outcome="success")], (0, 0, 1)),
                ([event("execution-result", outcome="failed"), recovered], (1, 0, 0)),
                ([event("finish", outcome="interrupted")], (0, 1, 0)),
                ([event("execution-result", outcome="success")], (0, 0, 0)),
                ([event("run-finish")], (0, 0, 1)),
            ):
                with self.subTest(legacy=legacy, receipts=receipts):
                    summary = assay.build_assay_report([start, *receipts])["summary"]
                    self.assertEqual(tuple(summary[k] for k in
                                           ("failed_runs", "interrupted_runs", "unconfirmed_runs")), expected)

    def test_unknown_family_is_visible_in_integrated_summary(self):
        report = assay.build_assay_report(sample_events())
        self.assertEqual(report["summary"]["unrecorded_family_integrated"], 1)
        self.assertEqual(report["summary"]["same_family_integrated"], 0)
        self.assertIn("Family unrecorded integrated: 1", assay.format_text(report))

    def test_nonterminal_receipts_keep_review_pending_until_terminal_verdict(self):
        events = sample_events()
        # The third request has no terminal result. Checking without publishing
        # writes "reviewed"; interrupted publication may retain "prepared".
        for status in ("reviewed", "prepared"):
            with self.subTest(status=status):
                receipt = {
                    "sequence": 23, "at": 1101.0, "actor": "resident-c", "op": "say",
                    "data": {"text": "house-integration-v1 " + json.dumps({
                        "run": "run-work-3", "status": status, "actor": "resident-c",
                    })},
                }
                report = assay.build_assay_report(events + [receipt])
                self.assertEqual(report["summary"]["pending_reviews"], 1)
                self.assertEqual(report["summary"]["total_verdicts"], 2)
                self.assertEqual(report["pending_reviews"][0]["integration_status"], status)
                self.assertIn(f"[{status}]", assay.format_text(report))
                for terminal in ("integrated", "rejected", "conflict", "tests-failed"):
                    verdict = {
                        "sequence": 24, "at": 1102.0, "actor": "resident-c", "op": "say",
                        "data": {"text": "house-integration-v1 " + json.dumps({
                            "run": "run-work-3", "status": terminal, "actor": "resident-c",
                        })},
                    }
                    completed = assay.build_assay_report(events + [receipt, verdict])
                    self.assertEqual(completed["summary"]["pending_reviews"], 0)
                    self.assertEqual(completed["summary"]["total_verdicts"], 3)

    def test_build_assay_report_pairs_authors_reviewers_deliveries_and_pending(self):
        events = sample_events()
        # Add reviewer identity for resident-c so cross-family check can verify muse != codex
        events.insert(3, {
            "sequence": 3, "at": 1003.0, "actor": "watch-keeper", "op": "life",
            "data": {"kind": "run-start", "run": "run-rev-2", "resident": "resident-c", "agent": "muse", "model": "muse-ember-1.0"},
        })
        report = assay.build_assay_report(events)
        summary = report["summary"]
        self.assertEqual(summary["total_verdicts"], 2)
        self.assertEqual(summary["rejected"], 1)
        self.assertEqual(summary["integrated"], 1)
        self.assertEqual(summary["delivered"], 1)
        self.assertEqual(summary["cross_family_integrated"], 1)
        self.assertEqual(summary["pending_reviews"], 1)

        verdicts = report["verdicts"]
        self.assertEqual(verdicts[0]["run"], "run-work-1")
        self.assertEqual(verdicts[0]["status"], "rejected")
        self.assertEqual(verdicts[0]["reason"], "Missing gap regression.")
        self.assertEqual(verdicts[0]["author_name"], "Yarrow")
        self.assertEqual(verdicts[0]["author_agent"], "agy")
        self.assertEqual(verdicts[0]["reviewer_name"], "Mallow")
        self.assertEqual(verdicts[0]["reviewer_agent"], "codex")
        self.assertTrue(verdicts[0]["cross_family"])
        self.assertFalse(verdicts[0]["delivered"])

        self.assertEqual(verdicts[1]["run"], "run-work-2")
        self.assertEqual(verdicts[1]["status"], "integrated")
        self.assertTrue(verdicts[1]["delivered"])
        self.assertEqual(verdicts[1]["remote_main"], "4444")
        self.assertEqual(verdicts[1]["author_agent"], "codex")
        self.assertEqual(verdicts[1]["reviewer_agent"], "muse")
        self.assertTrue(verdicts[1]["cross_family"])
        self.assertEqual(verdicts[1]["finished_tasks"], ["site-polish-repair"])

        pending = report["pending_reviews"]
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["review_run"], "run-work-3")
        self.assertEqual(pending[0]["author_name"], "Yarrow")
        self.assertEqual(pending[0]["finished_tasks"], ["assay-room"])

    def test_ignores_malformed_machine_messages_and_filters_cli(self):
        events = sample_events() + [
            {"sequence": 23, "at": 1105.0, "actor": "resident-a", "op": "say", "data": {"text": "house-integration-v1 {not json"}},
            {"sequence": 24, "at": 1106.0, "actor": "watch-keeper", "op": "say", "data": {"text": "house-source-delivery-v1 []"}},
        ]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as tmp:
            for ev in events:
                tmp.write(json.dumps(ev) + "\n")
            tmp_path = Path(tmp.name)
        try:
            proc = subprocess.run(
                [sys.executable, str(ASSAY_DIR / "assay.py"), "--events-file", str(tmp_path), "--status", "rejected", "--json"],
                capture_output=True, text=True, check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(len(payload["verdicts"]), 1)
            self.assertEqual(payload["verdicts"][0]["status"], "rejected")
            self.assertEqual(len(payload["pending_reviews"]), 0)

            proc_text = subprocess.run(
                [sys.executable, str(ASSAY_DIR / "assay.py"), "--events-file", str(tmp_path), "--status", "pending"],
                capture_output=True, text=True, check=True,
            )
            self.assertIn("run-work-3", proc_text.stdout)
            self.assertIn("Pending reviews", proc_text.stdout)
        finally:
            tmp_path.unlink(missing_ok=True)

    def test_undelivered_and_family_filters_plus_family_breakdown_and_run_scars(self):
        events = sample_events() + [
            {
                "sequence": 23, "at": 1105.0, "actor": "watch-keeper", "op": "life",
                "data": {"kind": "run-start", "run": "run-rev-2", "resident": "resident-c", "agent": "muse", "model": "muse-ember-1.0"},
            },
            {
                "sequence": 24, "at": 1106.0, "actor": "watch-keeper", "op": "life",
                "data": {"kind": "run-finish", "run": "run-rev-2", "outcome": "interrupted"},
            },
            {
                "sequence": 25, "at": 1110.0, "actor": "resident-c", "op": "say",
                "data": {"text": 'house-integration-v1 {"actor": "resident-c", "run": "run-work-3", "base": "4444", "contribution": "5555", "candidate_head": "6666", "status": "integrated", "test_scope": "project", "test_exit": 0}'},
            },
            {
                "sequence": 26, "at": 1120.0, "actor": "watch-keeper", "op": "life",
                "data": {"kind": "run-start", "run": "run-work-4", "resident": "resident-a", "agent": "agy", "model": "gemini-4"},
            },
            {
                "sequence": 27, "at": 1125.0, "actor": "watch-keeper", "op": "life",
                "data": {"kind": "run-finish", "run": "run-work-4", "outcome": "failed"},
            },
        ]
        report = assay.build_assay_report(events)
        summary = report["summary"]
        self.assertEqual(summary["integrated"], 2)
        self.assertEqual(summary["delivered"], 1)
        self.assertEqual(summary["undelivered_integrated"], 1)
        self.assertEqual(summary["interrupted_runs"], 1)
        self.assertEqual(summary["failed_runs"], 1)

        by_family = report["by_family"]
        self.assertEqual(by_family["codex"]["authored_verdicts"], 1)
        self.assertEqual(by_family["codex"]["reviewed_verdicts"], 1)
        self.assertEqual(by_family["codex"]["rejections_issued"], 1)
        self.assertEqual(by_family["muse"]["reviewed_verdicts"], 2)
        self.assertEqual(by_family["muse"]["cross_family_reviews"], 2)

        undelivered = assay.filter_report(report, status="undelivered")
        self.assertEqual([v["candidate_head"] for v in undelivered["verdicts"]], ["6666"])
        self.assertEqual(undelivered["pending_reviews"], [])

        agy_only = assay.filter_report(report, family="agy")
        self.assertEqual([v["run"] for v in agy_only["verdicts"]], ["run-work-1", "run-work-3"])

        text = assay.format_text(report)
        self.assertIn("Undelivered integrated: 1", text)
        self.assertIn("Family cross-review:", text)

        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as tmp:
            for ev in events:
                tmp.write(json.dumps(ev) + "\n")
            tmp_path = Path(tmp.name)
        try:
            proc = subprocess.run(
                [sys.executable, str(ASSAY_DIR / "assay.py"), "--events-file", str(tmp_path), "--status", "undelivered", "--family", "muse", "--json"],
                capture_output=True, text=True, check=True,
            )
            payload = json.loads(proc.stdout)
            self.assertEqual(len(payload["verdicts"]), 1)
            self.assertEqual(payload["verdicts"][0]["candidate_head"], "6666")
        finally:
            tmp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
