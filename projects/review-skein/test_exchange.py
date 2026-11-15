"""TDD unit and real-Git two-repository exchange tests for Skein Milestone 3."""
from __future__ import annotations

import contextlib
from dataclasses import replace
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import comments_view
import probe
import skein
from test_skein import SkeinFixture

import exchange


class ExchangeMergeTests(SkeinFixture):
    def setUp(self) -> None:
        super().setUp()
        self.packet_alice = self.root / "packet-alice"
        self.packet_bob = self.root / "packet-bob"
        self.packet_target = self.root / "packet-target"
        self.export(self.packet_alice)
        self.export(self.packet_bob)
        self.export(self.packet_target)

    def test_merge_is_commutative_associative_idempotent_and_preserves_packet_members(self) -> None:
        skein.add_comment(
            self.packet_alice, "shared-note", self.head, "alpha.txt", "new", 2,
            "Shared observation on line 2.",
        )
        skein.add_comment(
            self.packet_alice, "alice-note", self.head, "café-☃.txt", "new", 1,
            "Alice checks Unicode ☃ file.",
        )
        skein.add_comment(
            self.packet_bob, "shared-note", self.head, "alpha.txt", "new", 2,
            "Shared observation on line 2.",
        )
        skein.add_comment(
            self.packet_bob, "bob-note", self.base, "alpha.txt", "old", 1,
            "Bob notes original first line.",
        )

        non_comment_members = {
            name: (self.packet_alice / name).read_bytes()
            for name in ("packet.json", "anchors.json", "review.html", "changes.bundle")
        }

        ab_target = self.root / "ab"
        ba_target = self.root / "ba"
        self.export(ab_target)
        self.export(ba_target)

        res_ab = exchange.merge_comments(ab_target, [self.packet_alice, self.packet_bob])
        res_ba = exchange.merge_comments(ba_target, [self.packet_bob, self.packet_alice])

        self.assertEqual(
            (ab_target / "comments.json").read_bytes(),
            (ba_target / "comments.json").read_bytes(),
        )
        self.assertEqual(res_ab.comments, res_ba.comments)
        self.assertEqual((), res_ab.divergent_ids)
        self.assertEqual(
            ["bob-note", "shared-note", "alice-note"],
            [item.identifier for item in res_ab.comments],
        )

        # Idempotence: merging Alice or Bob again produces identical bytes.
        before = (ab_target / "comments.json").read_bytes()
        exchange.merge_comments(ab_target, [self.packet_alice])
        self.assertEqual(before, (ab_target / "comments.json").read_bytes())
        exchange.merge_comments(ab_target, [ab_target, self.packet_bob])
        self.assertEqual(before, (ab_target / "comments.json").read_bytes())

        # Non-comment packet members are byte-unchanged and packet still verifies.
        for name, expected in non_comment_members.items():
            self.assertEqual(expected, (ab_target / name).read_bytes(), name)
        self.assertEqual((self.base, self.head), skein.verify_packet(ab_target))

    def test_three_way_base_reconciles_one_sided_edit_or_resolution_without_conflict(self) -> None:
        base_packet = self.root / "packet-base"
        self.export(base_packet)
        skein.add_comment(
            base_packet, "thread-1", self.head, "alpha.txt", "new", 1, "Initial question.",
        )
        skein.add_comment(
            base_packet, "thread-2", self.head, "alpha.txt", "new", 3, "Tab check.",
        )
        # Copy base comments to Alice and Bob.
        base_bytes = (base_packet / "comments.json").read_bytes()
        (self.packet_alice / "comments.json").write_bytes(base_bytes)
        (self.packet_bob / "comments.json").write_bytes(base_bytes)
        (self.packet_target / "comments.json").write_bytes(base_bytes)

        # Alice edits thread-1 and adds alice-2; leaves thread-2 untouched.
        skein.update_comment(self.packet_alice, "thread-1", body="Clarified question.")
        skein.add_comment(
            self.packet_alice, "alice-2", self.head, "renamed.txt", "new", 1, "Rename ok.",
        )
        # Bob leaves thread-1 untouched and resolves thread-2.
        skein.update_comment(self.packet_bob, "thread-2", resolution="resolved")

        result = exchange.merge_comments(
            self.packet_target,
            [self.packet_alice, self.packet_bob],
            base=base_packet,
            on_divergent="reject",
        )
        self.assertEqual((), result.divergent_ids)
        self.assertEqual(("thread-1", "thread-2"), result.resolved_from_base_ids)
        by_id = {item.identifier: item for item in result.comments}
        self.assertEqual("Clarified question.", by_id["thread-1"].body)
        self.assertEqual("open", by_id["thread-1"].resolution)
        self.assertEqual("Tab check.", by_id["thread-2"].body)
        self.assertEqual("resolved", by_id["thread-2"].resolution)
        self.assertIn("alice-2", by_id)

    def test_divergent_same_id_comments_keep_both_deterministically_or_reject_cleanly(self) -> None:
        skein.add_comment(
            self.packet_alice, "collide", self.head, "alpha.txt", "new", 1,
            "Alice thinks this should use html.escape.",
        )
        skein.add_comment(
            self.packet_bob, "collide", self.head, "alpha.txt", "new", 1,
            "Bob thinks this line should be deleted.",
        )
        skein.update_comment(self.packet_bob, "collide", resolution="resolved")

        original_target = (self.packet_target / "comments.json").read_bytes()
        with self.assertRaisesRegex(skein.SkeinError, "divergent comment ID"):
            exchange.merge_comments(
                self.packet_target, [self.packet_alice, self.packet_bob],
                on_divergent="reject",
            )
        self.assertEqual(original_target, (self.packet_target / "comments.json").read_bytes())

        ab = self.root / "div-ab"
        ba = self.root / "div-ba"
        self.export(ab)
        self.export(ba)
        res_ab = exchange.merge_comments(ab, [self.packet_alice, self.packet_bob], on_divergent="keep")
        res_ba = exchange.merge_comments(ba, [self.packet_bob, self.packet_alice], on_divergent="keep")
        self.assertEqual(("collide",), res_ab.divergent_ids)
        self.assertEqual(
            (ab / "comments.json").read_bytes(),
            (ba / "comments.json").read_bytes(),
        )
        self.assertEqual(2, len(res_ab.comments))
        bodies = {item.body: item for item in res_ab.comments}
        self.assertIn("Alice thinks this should use html.escape.", bodies)
        self.assertIn("Bob thinks this line should be deleted.", bodies)
        self.assertEqual("resolved", bodies["Bob thinks this line should be deleted."].resolution)
        for item in res_ab.comments:
            self.assertTrue(item.identifier.startswith("collide--divergent-"))

        # Re-merging a split packet with Alice or Bob is idempotent (no double-splitting).
        merged_bytes = (ab / "comments.json").read_bytes()
        exchange.merge_comments(ab, [self.packet_alice], on_divergent="keep")
        self.assertEqual(merged_bytes, (ab / "comments.json").read_bytes())
        exchange.merge_comments(ab, [self.packet_bob], on_divergent="keep")
        self.assertEqual(merged_bytes, (ab / "comments.json").read_bytes())

        # Viewer and verifier accept the merged divergent comments without error.
        self.assertEqual((self.base, self.head), skein.verify_packet(ab))
        rendered = comments_view.render_comments(res_ab.comments, output_format="text")
        self.assertIn("Showing 2 of 2 comments.", rendered)

    def test_merge_rejects_mismatched_revisions_invalid_anchors_v1_and_symlinks(self) -> None:
        # Create a second commit so revision pair differs.
        self.write("alpha.txt", "revised\n")
        self.commit("second revision")
        other_packet = self.root / "packet-v2"
        skein.export_packet(self.repository, "base", "feature", other_packet)
        self.restore_head()

        before = (self.packet_target / "comments.json").read_bytes()
        with self.assertRaisesRegex(skein.SkeinError, "revision"):
            exchange.merge_comments(self.packet_target, [other_packet])
        self.assertEqual(before, (self.packet_target / "comments.json").read_bytes())

        # Forged standalone comments.json with non-existent line anchor.
        forged = self.root / "forged-comments.json"
        bad_comment = skein.Comment(
            "forged",
            skein.Anchor(self.head, "alpha.txt", "new", 999, "nonexistent"),
            "Forged anchor.",
        )
        forged.write_text(skein.dumps_comments([bad_comment]), encoding="utf-8")
        with self.assertRaisesRegex(skein.SkeinError, "rendered line"):
            exchange.merge_comments(self.packet_target, [forged])
        self.assertEqual(before, (self.packet_target / "comments.json").read_bytes())

        # Symlink source rejected.
        symlink_source = self.root / "symlink-comments.json"
        symlink_source.symlink_to(self.packet_alice / "comments.json")
        with self.assertRaisesRegex(skein.SkeinError, "regular"):
            exchange.merge_comments(self.packet_target, [symlink_source])
        self.assertEqual(before, (self.packet_target / "comments.json").read_bytes())


class ExchangeRevisedPatchTests(SkeinFixture):
    def test_carry_and_revise_reanchor_exact_moved_duplicate_deleted_and_resolved_comments(self) -> None:
        packet_v1 = self.root / "packet-v1"
        self.export(packet_v1)

        # Reviewer 1 and Reviewer 2 add comments on v1:
        # 1. Exact line that stays at line 2 in v2: "<danger> & value"
        c_exact = skein.add_comment(
            packet_v1, "exact-line", self.head, "alpha.txt", "new", 2,
            "Keep escaping this <danger> line.",
        )
        # 2. Unique line "\tTabbed" at line 3 in v1, which will shift to line 4 in v2.
        c_moved = skein.add_comment(
            packet_v1, "moved-line", self.head, "alpha.txt", "new", 3,
            "Tab indentation moves down in v2.",
        )
        skein.update_comment(packet_v1, "moved-line", resolution="resolved")
        # 3. Duplicate line "duplicate" at line 4 in v1, which shifts to lines 5 & 6 in v2 -> ambiguous orphan!
        c_dup = skein.add_comment(
            packet_v1, "dup-line", self.head, "alpha.txt", "new", 4,
            "Ambiguous duplicate line after shift.",
        )
        # 4. Deleted/replaced line 1 "<script>..." which is fixed in v2 -> missing-line orphan!
        c_fixed = skein.add_comment(
            packet_v1, "fixed-script", self.head, "alpha.txt", "new", 1,
            "Remove this script tag.",
        )
        # 5. Base-side comment on alpha.txt old line 1 ("first"), which stays valid on same base.
        c_base = skein.add_comment(
            packet_v1, "base-note", self.base, "alpha.txt", "old", 1,
            "Base line 1 reference.",
        )

        # Author creates revised patch v2 on branch feature-v2:
        self.git("checkout", "--quiet", "-b", "feature-v2", self.head)
        self.write(
            "alpha.txt",
            "safe replacement line 1\n<danger> & value\ninserted banner\n"
            "\tTabbed\nduplicate\nduplicate\nlast\nhead tail\n",
        )
        self.commit("v2: replace script line and insert banner above Tabbed")
        head_v2 = self.rev_parse("feature-v2")

        packet_v2 = self.root / "packet-v2"
        metadata, result = exchange.revise_packet(
            self.repository, "base", "feature-v2", packet_v2,
            sources=[packet_v1],
        )
        self.assertEqual(self.base, metadata["base"]["commit"])
        self.assertEqual(head_v2, metadata["head"]["commit"])
        self.assertEqual((self.base, head_v2), skein.verify_packet(packet_v2))

        by_id = {item.identifier: item for item in result.comments}
        self.assertEqual(5, len(by_id))

        # 1. Exact line stays anchored at line 2 on head_v2 with rebased_from = v1 anchor.
        self.assertEqual("anchored", by_id["exact-line"].state)
        self.assertEqual(head_v2, by_id["exact-line"].anchor.commit)
        self.assertEqual(2, by_id["exact-line"].anchor.line)
        self.assertEqual(c_exact.anchor, by_id["exact-line"].rebased_from)

        # 2. Moved unique line rebinds to line 4 on head_v2 and preserves resolved status.
        self.assertEqual("anchored", by_id["moved-line"].state)
        self.assertEqual("resolved", by_id["moved-line"].resolution)
        self.assertEqual(head_v2, by_id["moved-line"].anchor.commit)
        self.assertEqual(4, by_id["moved-line"].anchor.line)
        self.assertEqual(c_moved.anchor, by_id["moved-line"].rebased_from)

        # 3. Shifted duplicate line becomes an explicit ambiguous orphan.
        self.assertEqual("orphan", by_id["dup-line"].state)
        self.assertIn("ambiguous", by_id["dup-line"].orphan_reason or "")
        self.assertEqual(head_v2, by_id["dup-line"].anchor.commit)
        self.assertEqual(c_dup.anchor, by_id["dup-line"].rebased_from)

        # 4. Fixed/replaced line becomes an explicit missing-text orphan.
        self.assertEqual("orphan", by_id["fixed-script"].state)
        self.assertIn("uniquely matching text are missing", by_id["fixed-script"].orphan_reason or "")
        self.assertEqual(head_v2, by_id["fixed-script"].anchor.commit)
        self.assertEqual(c_fixed.anchor, by_id["fixed-script"].rebased_from)

        # 5. Unchanged base-side anchor on the same base commit stays anchored without false rebase.
        self.assertEqual("anchored", by_id["base-note"].state)
        self.assertEqual(self.base, by_id["base-note"].anchor.commit)
        self.assertEqual(1, by_id["base-note"].anchor.line)
        self.assertIsNone(by_id["base-note"].rebased_from)

        # Carrying packet_v1 into packet_v2 a second time is byte-idempotent.
        saved_v2_bytes = (packet_v2 / "comments.json").read_bytes()
        exchange.carry_comments(packet_v2, [packet_v1])
        self.assertEqual(saved_v2_bytes, (packet_v2 / "comments.json").read_bytes())

        # Compare packet_v1 and packet_v2 reports the exact transitions.
        comparison = exchange.compare_packets(packet_v1, packet_v2)
        self.assertFalse(comparison["same_revision"])
        self.assertEqual(["base-note"], comparison["identical"])
        self.assertEqual(["exact-line", "moved-line"], comparison["reanchored"])
        self.assertEqual(["dup-line", "fixed-script"], comparison["newly_orphaned"])

        # Multi-hop rebase to v3: restore the deleted "<script>..." line uniquely,
        # while keeping dup-line ambiguous so one orphan re-anchors and one keeps v1 provenance.
        self.git("checkout", "--quiet", "-b", "feature-v3", head_v2)
        self.write(
            "alpha.txt",
            "<script>alert(\"x\")</script> & value\n<danger> & value\ninserted banner\n"
            "\tTabbed\nduplicate\nduplicate\nlast\nhead tail\n",
        )
        self.commit("v3: restore original line 1 while keeping duplicate lines shifted")
        head_v3 = self.rev_parse("feature-v3")

        packet_v3 = self.root / "packet-v3"
        _, result_v3 = exchange.revise_packet(
            self.repository, "base", "feature-v3", packet_v3,
            sources=[packet_v2],
        )
        by_id_v3 = {item.identifier: item for item in result_v3.comments}
        # fixed-script was orphaned in v2 and re-anchors cleanly in v3!
        self.assertEqual("anchored", by_id_v3["fixed-script"].state)
        self.assertIsNone(by_id_v3["fixed-script"].orphan_reason)
        self.assertEqual(head_v3, by_id_v3["fixed-script"].anchor.commit)
        self.assertEqual(1, by_id_v3["fixed-script"].anchor.line)
        self.assertEqual(c_fixed.anchor, by_id_v3["fixed-script"].rebased_from)

        # dup-line remains orphaned in v3 and preserves its original v1 anchor in rebased_from.
        self.assertEqual("orphan", by_id_v3["dup-line"].state)
        self.assertEqual(head_v3, by_id_v3["dup-line"].anchor.commit)
        self.assertEqual(c_dup.anchor, by_id_v3["dup-line"].rebased_from)

    def test_failed_revise_cleans_up_output_and_compare_distinguishes_same_revision_states(self) -> None:
        packet_a = self.root / "cmp-a"
        packet_b = self.root / "cmp-b"
        self.export(packet_a)
        self.export(packet_b)

        skein.add_comment(packet_a, "only-a", self.head, "alpha.txt", "new", 1, "Only A.")
        skein.add_comment(packet_b, "only-b", self.head, "alpha.txt", "new", 2, "Only B.")
        skein.add_comment(packet_a, "edited", self.head, "alpha.txt", "new", 3, "Before edit.")
        skein.add_comment(packet_b, "edited", self.head, "alpha.txt", "new", 3, "After edit.")
        skein.update_comment(packet_b, "edited", resolution="resolved")
        # Same ID anchored at different lines on the same commit -> divergent, not reanchored!
        skein.add_comment(packet_a, "wrong-line", self.head, "alpha.txt", "new", 1, "Line 1.")
        skein.add_comment(packet_b, "wrong-line", self.head, "alpha.txt", "new", 2, "Line 2.")

        cmp_report = exchange.compare_packets(packet_a, packet_b)
        self.assertTrue(cmp_report["same_revision"])
        self.assertEqual(["only-a"], cmp_report["only_in_first"])
        self.assertEqual(["only-b"], cmp_report["only_in_second"])
        self.assertEqual(["edited"], cmp_report["resolved_or_edited"])
        self.assertEqual(["wrong-line"], cmp_report["divergent"])
        self.assertEqual([], cmp_report["reanchored"])

        # revise with --on-divergent reject must fail and leave no output directory behind.
        failed_out = self.root / "failed-revise-packet"
        with self.assertRaisesRegex(skein.SkeinError, "divergent"):
            exchange.revise_packet(
                self.repository, "base", "feature", failed_out,
                sources=[packet_a, packet_b], on_divergent="reject",
            )
        self.assertFalse(failed_out.exists())

        # Human-readable CLI text mode and error exit code 2.
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            self.assertEqual(0, exchange.main(["compare", str(packet_a), str(packet_b)]))
        self.assertIn("Same revision pair: yes", stdout.getvalue())
        self.assertIn("Resolved or edited (1): edited", stdout.getvalue())
        self.assertIn("Divergent (1): wrong-line", stdout.getvalue())

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as caught:
            exchange.main([
                "merge", str(packet_a), str(packet_b), "--on-divergent", "reject",
            ])
        self.assertEqual(2, caught.exception.code)
        self.assertIn("divergent comment ID", stderr.getvalue())

    def test_two_repository_cli_exchange_and_revised_patch_lifecycle(self) -> None:
        """End-to-end CLI lifecycle across two independent Git repositories."""
        skein_cli = Path(skein.__file__).resolve()
        exchange_cli = Path(exchange.__file__).resolve()
        probe_cli = Path(probe.__file__).resolve()
        view_cli = Path(comments_view.__file__).resolve()

        def run_cli(script: Path, *args: str) -> subprocess.CompletedProcess[str]:
            result = subprocess.run(
                [sys.executable, str(script), *args],
                env=self.environment, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(0, result.returncode, f"cmd={args}\nstdout={result.stdout}\nstderr={result.stderr}")
            return result

        # Step 1: Author exports packet-v1 from self.repository.
        packet_v1 = self.root / "exchange-v1"
        run_cli(skein_cli, "export", str(self.repository), "base", "feature", str(packet_v1))

        # Step 2: Reviewer A and Reviewer B each receive copies of packet-v1 in isolated directories,
        # and Reviewer B clones the bundle into a separate second Git repository (repo_b) with no
        # link to self.repository.
        reviewer_a_v1 = self.root / "reviewer-a-v1"
        reviewer_b_v1 = self.root / "reviewer-b-v1"
        self.export(reviewer_a_v1)
        self.export(reviewer_b_v1)

        repo_b = self.root / "repo-b"
        self.git("clone", "--quiet", str(reviewer_b_v1 / "changes.bundle"), str(repo_b), cwd=self.root)
        self.git("checkout", "--quiet", "-B", "base", self.base, cwd=repo_b)
        self.git("checkout", "--quiet", "-B", "feature", self.head, cwd=repo_b)

        # Reviewer A adds two comments on reviewer_a_v1.
        run_cli(
            skein_cli, "comment", str(reviewer_a_v1),
            "--id", "r1-escape", "--commit", self.head,
            "--path", "alpha.txt", "--side", "new", "--line", "1",
            "--body", "Reviewer 1: replace inline script test line.",
        )
        run_cli(
            skein_cli, "comment", str(reviewer_a_v1),
            "--id", "shared-id", "--commit", self.head,
            "--path", "alpha.txt", "--side", "new", "--line", "3",
            "--body", "Reviewer 1: keep Tabbed line.",
        )

        # Reviewer B adds a distinct comment and a divergent comment with the same ID 'shared-id'.
        run_cli(
            skein_cli, "comment", str(reviewer_b_v1),
            "--id", "r2-unicode", "--commit", self.head,
            "--path", "café-☃.txt", "--side", "new", "--line", "2",
            "--body", "Reviewer 2: second Unicode line looks good.",
        )
        run_cli(
            skein_cli, "comment", str(reviewer_b_v1),
            "--id", "shared-id", "--commit", self.head,
            "--path", "alpha.txt", "--side", "new", "--line", "3",
            "--body", "Reviewer 2: also check tab width in CSS.",
        )

        # Step 3: Merge Reviewer A and Reviewer B comments into packet_v1 via CLI.
        merged_out = run_cli(
            exchange_cli, "merge", str(packet_v1),
            str(reviewer_a_v1), str(reviewer_b_v1), "--json",
        )
        merged_report = json.loads(merged_out.stdout)
        self.assertEqual(["shared-id"], merged_report["divergent_ids"])
        self.assertEqual(4, merged_report["total_comments"])

        # Step 4: In repo_b (the second repository), prepare a revised commit fixing r1-escape,
        # and run `exchange.py revise` to export packet_v2 while carrying the merged comments.
        (repo_b / "alpha.txt").write_text(
            "escaped header\n<danger> & value\ninserted context\n"
            "\tTabbed\nduplicate\nduplicate\nlast\nhead tail\n",
            encoding="utf-8", newline="\n",
        )
        self.git("add", "alpha.txt", cwd=repo_b)
        self.git("-c", "commit.gpgsign=false", "commit", "--quiet", "-m", "repo-b revised patch", cwd=repo_b)

        packet_v2 = self.root / "exchange-v2"
        revise_out = run_cli(
            exchange_cli, "revise", str(repo_b), "base", "feature", str(packet_v2),
            "--from", str(packet_v1), "--json",
        )
        revise_report = json.loads(revise_out.stdout)
        self.assertEqual(4, revise_report["total_comments"])
        self.assertEqual(1, revise_report["orphan_comments"])
        self.assertEqual(3, revise_report["anchored_comments"])

        # Verify packet_v2 with skein.py, probe.py, and comments_view.py!
        run_cli(skein_cli, "verify", str(packet_v2))
        run_cli(probe_cli, "audit", str(packet_v2))
        view_out = run_cli(view_cli, str(packet_v2 / "comments.json"))
        self.assertIn("Showing 4 of 4 comments.", view_out.stdout)
        self.assertIn("1 orphan", view_out.stdout)

        # Compare packet_v1 and packet_v2 via CLI.
        cmp_out = run_cli(exchange_cli, "compare", str(packet_v1), str(packet_v2), "--json")
        cmp_data = json.loads(cmp_out.stdout)
        self.assertEqual(["r1-escape"], cmp_data["newly_orphaned"])
        self.assertEqual(3, len(cmp_data["reanchored"]))


if __name__ == "__main__":
    unittest.main()
