#!/usr/bin/env python3
"""Skein milestone 4: packet diagnostics, deterministic rebuild and comment salvage.

Recovers damaged or partial Skein review packets from either their embedded
changes.bundle or a local Git repository containing the base and head commits,
and salvages v1, drifted or duplicate-ID comment files without silent data loss.
"""
from __future__ import annotations

import argparse
from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
import tempfile
from typing import Any

import exchange
import probe
import skein


CANONICAL_MEMBERS = (
    "packet.json",
    "anchors.json",
    "review.html",
    "comments.json",
    "changes.bundle",
)


def _is_temp_entry(name: str) -> bool:
    if name in CANONICAL_MEMBERS:
        return False
    return (
        name.startswith(".comments-")
        or name.endswith(".tmp")
        or ".tmp-" in name
        or name == "bundle-source.git"
    )


def _list_temp_entries(packet: Path) -> list[str]:
    found: list[str] = []
    for entry in sorted(packet.iterdir(), key=lambda p: p.name):
        if _is_temp_entry(entry.name):
            found.append(entry.name)
    return found


def _bundle_commits_and_clone(bundle_path: Path, scratch_root: Path) -> tuple[str, str, Path]:
    """Verify a Skein bundle in an isolated clone and return (base_oid, head_oid, clone_path)."""
    if bundle_path.is_symlink() or not bundle_path.is_file():
        raise skein.SkeinError(f"bundle is missing or not a regular file: {bundle_path.name}")
    heads_out = skein._git(scratch_root, "bundle", "list-heads", str(bundle_path)).stdout
    refs: dict[str, str] = {}
    for raw_line in heads_out.decode("utf-8", errors="replace").splitlines():
        parts = raw_line.strip().split()
        if len(parts) == 2:
            oid, refname = parts
            refs[refname] = skein._oid(oid, f"bundle head {refname}")
    base_oid = refs.get("refs/heads/skein-base")
    head_oid = refs.get("refs/heads/skein-head")
    if not base_oid or not head_oid:
        raise skein.SkeinError(
            "changes.bundle does not contain both refs/heads/skein-base and refs/heads/skein-head"
        )
    clone = scratch_root / "bundle-clone"
    skein._git(scratch_root, "clone", "--quiet", "--no-checkout", str(bundle_path), str(clone))
    skein._git(clone, "bundle", "verify", str(bundle_path))
    for commit in (base_oid, head_oid):
        skein._git(clone, "cat-file", "-e", f"{commit}^{{commit}}")
    return base_oid, head_oid, clone


def _reconstruct_members(
    worktree: Path,
    *,
    base_ref: str,
    base_commit: str,
    head_ref: str,
    head_commit: str,
    max_file_bytes: int = skein.DEFAULT_MAX_FILE_BYTES,
) -> tuple[dict[str, Any], str, str, str, list[skein.Anchor]]:
    """Deterministically reconstruct packet.json, anchors.json and review.html from Git objects."""
    skein._oid(base_commit, "base commit")
    skein._oid(head_commit, "head commit")
    for commit in (base_commit, head_commit):
        skein._git(worktree, "cat-file", "-e", f"{commit}^{{commit}}")
    old_tree = skein._tree(worktree, base_commit)
    new_tree = skein._tree(worktree, head_commit)
    changes = skein._changes(worktree, base_commit, head_commit)
    reader = skein.BlobReader(worktree, max_file_bytes)
    rendered: list[tuple[skein.Change, list[str], list[str]]] = []
    anchors: list[skein.Anchor] = []
    file_records: list[dict[str, Any]] = []
    for change in changes:
        old_entry = old_tree.get(change.old_path) if change.old_path else None
        new_entry = new_tree.get(change.new_path) if change.new_path else None
        old = reader.read(old_entry)
        new = reader.read(new_entry)
        rendered.append((change, old, new))
        file_records.append({
            "status": change.status,
            "old_path": change.old_path,
            "new_path": change.new_path,
            "old_lines": len(old),
            "new_lines": len(new),
        })
        if change.old_path:
            anchors.extend(
                skein.Anchor(base_commit, change.old_path, "old", number, text)
                for number, text in enumerate(old, 1)
            )
        if change.new_path:
            anchors.extend(
                skein.Anchor(head_commit, change.new_path, "new", number, text)
                for number, text in enumerate(new, 1)
            )
    metadata = {
        "format": skein.FORMAT,
        "version": skein.VERSION,
        "base": {"ref": base_ref, "commit": base_commit},
        "head": {"ref": head_ref, "commit": head_commit},
        "bundle": "changes.bundle",
        "diff": "review.html",
        "anchors": "anchors.json",
        "comments": "comments.json",
        "files": file_records,
    }
    packet_text = skein._json_text(metadata)
    anchors_text = skein._json_text({
        "format": skein.ANCHOR_FORMAT,
        "version": skein.VERSION,
        "anchors": [item.to_dict() for item in anchors],
    })
    review_html = skein._render_html(metadata, rendered)
    return metadata, packet_text, anchors_text, review_html, anchors


def salvage_comments_list(
    raw_text: str,
    *,
    base_commit: str,
    head_commit: str,
    anchors: list[skein.Anchor],
) -> tuple[list[skein.Comment], dict[str, Any]]:
    """Upgrade v1 records, split duplicate IDs, and reanchor or orphan mismatched anchors."""
    try:
        value = json.loads(raw_text, object_pairs_hook=skein._unique_object)
    except json.JSONDecodeError as exc:
        raise skein.SkeinError(f"invalid comments JSON: {exc}") from exc
    if (
        not isinstance(value, dict)
        or set(value) != {"format", "version", "comments"}
        or value["format"] != skein.COMMENT_FORMAT
        or type(value["version"]) is not int
        or value["version"] not in {1, skein.COMMENT_VERSION}
        or not isinstance(value["comments"], list)
    ):
        raise skein.SkeinError("unsupported comments header")

    was_v1 = value["version"] == 1
    raw_records = value["comments"]
    parsed: list[skein.Comment] = []
    for item in raw_records:
        if not isinstance(item, dict):
            raise skein.SkeinError("malformed comment record")
        if was_v1 and "resolution" not in item:
            v1_required = {"id", "anchor", "body", "state", "rebased_from", "orphan_reason"}
            if set(item) != v1_required:
                raise skein.SkeinError("malformed version-1 comment record")
            item = {**item, "resolution": "open"}
        parsed.append(skein.Comment.from_dict(item))

    old_anchors = [a for a in anchors if a.side == "old"]
    new_anchors = [a for a in anchors if a.side == "new"]
    old_set = set(old_anchors)
    new_set = set(new_anchors)

    rebound: list[skein.Comment] = []
    reanchored_ids: list[str] = []
    orphaned_ids: list[str] = []
    intact_ids: list[str] = []

    for comment in parsed:
        expected_commit = base_commit if comment.anchor.side == "old" else head_commit
        pool = old_anchors if comment.anchor.side == "old" else new_anchors
        pool_set = old_set if comment.anchor.side == "old" else new_set

        if comment.anchor.commit == expected_commit and comment.state == "anchored" and comment.anchor in pool_set:
            rebound.append(comment)
            intact_ids.append(comment.identifier)
            continue
        if comment.anchor.commit == expected_commit and comment.state == "orphan":
            rebound.append(comment)
            intact_ids.append(comment.identifier)
            continue

        prior_anchor = (
            comment.rebased_from
            if comment.state == "orphan" and comment.rebased_from is not None
            else comment.anchor
        )
        probe_comment = replace(
            comment,
            anchor=prior_anchor,
            state="anchored",
            rebased_from=None,
            orphan_reason=None,
        )
        updated = skein.reanchor(probe_comment, expected_commit, pool)
        if updated.state == "anchored":
            if updated.anchor == comment.anchor and comment.rebased_from is None:
                updated = replace(updated, rebased_from=None)
            reanchored_ids.append(comment.identifier)
        else:
            orphaned_ids.append(comment.identifier)
        rebound.append(updated)

    # Deduplicate identical records and split divergent same-ID records deterministically
    by_base: dict[str, list[skein.Comment]] = {}
    for comment in rebound:
        bid = exchange.base_comment_id(comment.identifier)
        normalized = replace(comment, identifier=bid)
        bucket = by_base.setdefault(bid, [])
        if normalized not in bucket:
            bucket.append(normalized)

    final_comments: list[skein.Comment] = []
    divergent_ids: list[str] = []
    for bid in sorted(by_base):
        variants = by_base[bid]
        if len(variants) == 1:
            final_comments.append(variants[0])
        else:
            provisional = [exchange.divergent_comment_id(bid, v, fallback_full=False) for v in variants]
            use_full = len(set(provisional)) < len(variants)
            for variant in variants:
                div_id = exchange.divergent_comment_id(bid, variant, fallback_full=use_full)
                final_comments.append(replace(variant, identifier=div_id))
                divergent_ids.append(div_id)

    final_comments.sort(key=exchange.comment_sort_key)
    summary = {
        "migrated_from_v1": was_v1,
        "total_comments": len(final_comments),
        "intact_ids": intact_ids,
        "reanchored_ids": reanchored_ids,
        "orphaned_ids": orphaned_ids,
        "divergent_ids": sorted(divergent_ids),
    }
    return final_comments, summary


def diagnose_packet(packet: Path, *, repo: Path | None = None) -> dict[str, Any]:
    """Inspect a packet directory read-only and report health, missing/corrupt files and recovery path."""
    raw = packet.expanduser()
    if raw.is_symlink() or not raw.is_dir():
        return {
            "status": "unrecoverable",
            "missing_members": [],
            "corrupted_members": [],
            "temp_files": [],
            "comments_status": "unreadable",
            "issues": [f"packet must be a regular directory: {packet}"],
        }
    resolved = raw.resolve()
    missing_members: list[str] = []
    corrupted_members: list[str] = []
    issues: list[str] = []

    for name in CANONICAL_MEMBERS:
        member = resolved / name
        if member.is_symlink():
            corrupted_members.append(name)
            issues.append(f"{name} is a symlink")
        elif not member.is_file():
            missing_members.append(name)

    if missing_members:
        issues.append(f"missing packet member(s): {', '.join(missing_members)}")

    temp_files = _list_temp_entries(resolved)
    if temp_files:
        issues.append(f"leftover temporary files present: {', '.join(temp_files)}")

    metadata: dict[str, Any] | None = None
    if "packet.json" not in missing_members and "packet.json" not in corrupted_members:
        try:
            metadata = skein._load_packet(resolved)
        except skein.SkeinError as exc:
            corrupted_members.append("packet.json")
            issues.append(f"packet.json: {exc}")

    with tempfile.TemporaryDirectory(prefix="skein-diagnose-") as scratch_dir:
        scratch = Path(scratch_dir)
        bundle_base: str | None = None
        bundle_head: str | None = None
        source_worktree: Path | None = None

        if "changes.bundle" not in missing_members and "changes.bundle" not in corrupted_members:
            try:
                bundle_base, bundle_head, source_worktree = _bundle_commits_and_clone(
                    resolved / "changes.bundle", scratch,
                )
            except skein.SkeinError as exc:
                corrupted_members.append("changes.bundle")
                issues.append(f"changes.bundle: {exc}")

        if metadata is not None and bundle_base is not None and bundle_head is not None:
            if (metadata["base"]["commit"], metadata["head"]["commit"]) != (bundle_base, bundle_head):
                issues.append(
                    "commit mismatch between packet.json "
                    f"({metadata['base']['commit']}..{metadata['head']['commit']}) "
                    f"and changes.bundle ({bundle_base}..{bundle_head})"
                )
                return {
                    "status": "unrecoverable",
                    "missing_members": missing_members,
                    "corrupted_members": sorted(set(corrupted_members)),
                    "temp_files": temp_files,
                    "comments_status": "unverified",
                    "issues": issues,
                }

        base_commit = metadata["base"]["commit"] if metadata is not None else bundle_base
        head_commit = metadata["head"]["commit"] if metadata is not None else bundle_head
        base_ref = metadata["base"]["ref"] if metadata is not None else (base_commit or "skein-base")
        head_ref = metadata["head"]["ref"] if metadata is not None else (head_commit or "skein-head")

        if source_worktree is None and repo is not None and base_commit and head_commit:
            try:
                wt = skein._worktree(repo)
                for commit in (base_commit, head_commit):
                    skein._git(wt, "cat-file", "-e", f"{commit}^{{commit}}")
                source_worktree = wt
            except skein.SkeinError as exc:
                issues.append(f"supplied --repo cannot supply commits: {exc}")

        if source_worktree is None or not base_commit or not head_commit:
            issues.append(
                "no verified Git object source available (changes.bundle is missing or invalid and no valid --repo was provided)"
            )
            return {
                "status": "unrecoverable",
                "missing_members": missing_members,
                "corrupted_members": sorted(set(corrupted_members)),
                "temp_files": temp_files,
                "comments_status": "unverified",
                "issues": issues,
            }

        try:
            _, exp_packet_text, exp_anchors_text, exp_html_text, expected_anchors = _reconstruct_members(
                source_worktree,
                base_ref=base_ref,
                base_commit=base_commit,
                head_ref=head_ref,
                head_commit=head_commit,
            )
        except skein.SkeinError as exc:
            issues.append(f"cannot reconstruct packet from Git objects: {exc}")
            return {
                "status": "unrecoverable",
                "missing_members": missing_members,
                "corrupted_members": sorted(set(corrupted_members)),
                "temp_files": temp_files,
                "comments_status": "unverified",
                "issues": issues,
            }

        for member_name, expected_text in (
            ("packet.json", exp_packet_text),
            ("anchors.json", exp_anchors_text),
            ("review.html", exp_html_text),
        ):
            if member_name not in missing_members and member_name not in corrupted_members:
                actual_bytes = (resolved / member_name).read_bytes()
                if actual_bytes != expected_text.encode("utf-8"):
                    corrupted_members.append(member_name)
                    issues.append(f"{member_name} bytes do not match deterministic export for {base_commit}..{head_commit}")

        comments_status = "intact_v2"
        if "comments.json" in missing_members:
            comments_status = "missing"
            issues.append("comments.json is missing")
        elif "comments.json" in corrupted_members:
            comments_status = "corrupted"
        else:
            raw_comments_bytes = (resolved / "comments.json").read_bytes()
            try:
                raw_text = raw_comments_bytes.decode("utf-8")
                comments = skein.loads_comments(raw_text)
                exchange._validate_comments_for_packet(
                    comments,
                    base_commit=base_commit,
                    head_commit=head_commit,
                    anchors=set(expected_anchors),
                )
                # Valid human-authored v2 state need not use our JSON formatting.
                # Rebuild preserves these bytes; formatting alone needs no repair.
            except (UnicodeDecodeError, skein.SkeinError) as exc:
                msg = str(exc)
                if "migrate-comments" in msg:
                    try:
                        salvage_comments_list(
                            raw_comments_bytes.decode("utf-8"),
                            base_commit=base_commit,
                            head_commit=head_commit,
                            anchors=expected_anchors,
                        )
                        comments_status = "legacy_v1"
                        issues.append("comments.json uses version 1 and needs migration to version 2")
                    except (UnicodeDecodeError, skein.SkeinError) as sub_exc:
                        comments_status = "corrupted"
                        corrupted_members.append("comments.json")
                        issues.append(f"comments.json: {sub_exc}")
                else:
                    try:
                        salvage_comments_list(
                            raw_comments_bytes.decode("utf-8"),
                            base_commit=base_commit,
                            head_commit=head_commit,
                            anchors=expected_anchors,
                        )
                        comments_status = "needs_salvage"
                        issues.append(f"comments.json requires salvage ({msg})")
                    except (UnicodeDecodeError, skein.SkeinError) as sub_exc:
                        comments_status = "corrupted"
                        corrupted_members.append("comments.json")
                        issues.append(f"comments.json: {sub_exc}")

        is_healthy = (
            not missing_members
            and not corrupted_members
            and not temp_files
            and comments_status == "intact_v2"
        )
        return {
            "status": "healthy" if is_healthy else "recoverable",
            "base_commit": base_commit,
            "head_commit": head_commit,
            "missing_members": missing_members,
            "corrupted_members": sorted(set(corrupted_members)),
            "temp_files": temp_files,
            "comments_status": comments_status,
            "issues": issues,
        }


def rebuild_packet(
    damaged_packet: Path,
    output: Path,
    *,
    repo: Path | None = None,
    base_ref: str | None = None,
    head_ref: str | None = None,
    salvage_comments: bool = False,
    trust_bundle: bool = False,
    max_file_bytes: int = skein.DEFAULT_MAX_FILE_BYTES,
) -> dict[str, Any]:
    """Rebuild a damaged or partial packet into a new verified packet directory."""
    raw_in = damaged_packet.expanduser()
    if raw_in.is_symlink() or not raw_in.is_dir():
        raise skein.SkeinError(f"damaged packet must be a regular directory: {damaged_packet}")
    source_dir = raw_in.resolve()

    raw_out = output.expanduser()
    if raw_out.exists() or raw_out.is_symlink():
        raise skein.SkeinError("output packet path must be a new directory; refusing to overwrite")
    target_dir = raw_out.resolve()
    if target_dir == source_dir or target_dir.is_relative_to(source_dir):
        raise skein.SkeinError("output packet must be outside the damaged packet directory")

    worktree_repo: Path | None = None
    if repo is not None:
        worktree_repo = skein._worktree(repo)
        if target_dir == worktree_repo or target_dir.is_relative_to(worktree_repo):
            raise skein.SkeinError("output packet must be outside the source repository worktree")

    for name in CANONICAL_MEMBERS:
        candidate = source_dir / name
        if candidate.is_symlink():
            raise skein.SkeinError(f"refusing symlink member in packet: {name}")

    metadata: dict[str, Any] | None = None
    if (source_dir / "packet.json").is_file():
        try:
            metadata = skein._load_packet(source_dir)
        except skein.SkeinError:
            metadata = None

    with tempfile.TemporaryDirectory(prefix="skein-rebuild-") as scratch_dir:
        scratch = Path(scratch_dir)
        bundle_base: str | None = None
        bundle_head: str | None = None
        bundle_clone: Path | None = None

        if (source_dir / "changes.bundle").is_file():
            try:
                bundle_base, bundle_head, bundle_clone = _bundle_commits_and_clone(
                    source_dir / "changes.bundle", scratch,
                )
            except skein.SkeinError:
                bundle_base = None
                bundle_head = None
                bundle_clone = None

        if metadata is not None and bundle_base is not None and bundle_head is not None:
            if (metadata["base"]["commit"], metadata["head"]["commit"]) != (bundle_base, bundle_head):
                if not trust_bundle:
                    raise skein.SkeinError(
                        "commit mismatch between packet.json and changes.bundle; "
                        "pass --trust-bundle to rebuild using changes.bundle commits"
                    )
                metadata = None

        resolved_base = (
            bundle_base if (trust_bundle and bundle_base)
            else (metadata["base"]["commit"] if metadata is not None else bundle_base)
        )
        resolved_head = (
            bundle_head if (trust_bundle and bundle_head)
            else (metadata["head"]["commit"] if metadata is not None else bundle_head)
        )
        if not resolved_base or not resolved_head:
            raise skein.SkeinError(
                "cannot determine base and head commit IDs from either packet.json or changes.bundle"
            )

        resolved_base_ref = (
            base_ref
            or (metadata["base"]["ref"] if metadata is not None else None)
            or resolved_base
        )
        resolved_head_ref = (
            head_ref
            or (metadata["head"]["ref"] if metadata is not None else None)
            or resolved_head
        )

        git_source: Path | None = bundle_clone
        if git_source is None and worktree_repo is not None:
            for commit in (resolved_base, resolved_head):
                skein._git(worktree_repo, "cat-file", "-e", f"{commit}^{{commit}}")
            git_source = worktree_repo
        if git_source is None:
            raise skein.SkeinError(
                "changes.bundle is missing or corrupted and no --repo containing the packet commits was provided"
            )

        rebuilt_meta, packet_text, anchors_text, html_text, anchors = _reconstruct_members(
            git_source,
            base_ref=resolved_base_ref,
            base_commit=resolved_base,
            head_ref=resolved_head_ref,
            head_commit=resolved_head,
            max_file_bytes=max_file_bytes,
        )

        # Handle comments.json before creating output directory
        comments_path = source_dir / "comments.json"
        comments_action = "intact_v2"
        salvage_report: dict[str, Any] | None = None
        if not comments_path.is_file():
            if not salvage_comments:
                raise skein.SkeinError(
                    "comments.json is missing; pass --salvage-comments to initialize an empty comments.json"
                )
            comments_text = skein.dumps_comments([])
            comments_action = "initialized_empty"
        else:
            raw_bytes = comments_path.read_bytes()
            if len(raw_bytes) > skein.JSON_LIMIT:
                raise skein.SkeinError("comments.json exceeds size limit")
            try:
                raw_str = raw_bytes.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise skein.SkeinError(f"invalid UTF-8 in comments.json: {exc}") from exc
            try:
                loaded = skein.loads_comments(raw_str)
                exchange._validate_comments_for_packet(
                    loaded,
                    base_commit=resolved_base,
                    head_commit=resolved_head,
                    anchors=set(anchors),
                )
                comments_text = raw_str
            except skein.SkeinError as exc:
                if "migrate-comments" in str(exc):
                    migrated, salvage_report = salvage_comments_list(
                        raw_str,
                        base_commit=resolved_base,
                        head_commit=resolved_head,
                        anchors=anchors,
                    )
                    if salvage_report["reanchored_ids"] or salvage_report["orphaned_ids"] or salvage_report["divergent_ids"]:
                        if not salvage_comments:
                            raise skein.SkeinError(
                                "version-1 comments contain mismatched or duplicate anchors; pass --salvage-comments"
                            ) from exc
                        comments_action = "salvaged_v1"
                    else:
                        comments_action = "migrated_v1"
                    comments_text = skein.dumps_comments(migrated)
                elif salvage_comments:
                    salvaged, salvage_report = salvage_comments_list(
                        raw_str,
                        base_commit=resolved_base,
                        head_commit=resolved_head,
                        anchors=anchors,
                    )
                    comments_text = skein.dumps_comments(salvaged)
                    comments_action = "salvaged"
                else:
                    raise skein.SkeinError(
                        f"comments.json validation failed ({exc}); pass --salvage-comments to reanchor/orphan mismatched records"
                    ) from exc

        target_dir.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=f".{target_dir.name}.tmp-", dir=target_dir.parent))
        published = False
        try:
            skein._write(staging / "packet.json", packet_text)
            skein._write(staging / "anchors.json", anchors_text)
            skein._write(staging / "review.html", html_text)
            skein._write(staging / "comments.json", comments_text)
            if bundle_clone is not None and (source_dir / "changes.bundle").is_file():
                shutil.copy2(source_dir / "changes.bundle", staging / "changes.bundle")
            else:
                skein._make_bundle(git_source, staging, resolved_base, resolved_head)
                shutil.rmtree(staging / "bundle-source.git", ignore_errors=True)
            skein.verify_packet(staging)
            tree, notes = probe.load_packet(staging)
            audit_errors = [f for f in probe.audit(tree, notes) if f.severity == "error"]
            if audit_errors:
                raise skein.SkeinError(f"rebuilt review.html failed probe audit: {audit_errors[0].detail}")
            staging.rename(target_dir)
            published = True
        finally:
            if not published:
                shutil.rmtree(staging, ignore_errors=True)

    return {
        "output": str(target_dir),
        "base_ref": resolved_base_ref,
        "base_commit": resolved_base,
        "head_ref": resolved_head_ref,
        "head_commit": resolved_head,
        "comments_action": comments_action,
        "salvage_report": salvage_report,
    }


def clean_temp_files(packet: Path, *, apply: bool = False) -> dict[str, Any]:
    """List or remove leftover temporary files inside a packet directory."""
    raw = packet.expanduser()
    if raw.is_symlink() or not raw.is_dir():
        raise skein.SkeinError(f"packet must be a regular directory: {packet}")
    resolved = raw.resolve()
    temp_files = _list_temp_entries(resolved)
    removed: list[str] = []
    if apply:
        for name in temp_files:
            target = resolved / name
            if target.is_symlink():
                raise skein.SkeinError(f"refusing to remove symlink temp entry: {name}")
            if target.is_dir():
                shutil.rmtree(target)
            elif target.is_file():
                target.unlink()
            removed.append(name)
    return {
        "packet": str(resolved),
        "temp_files": temp_files,
        "removed": removed,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    diag_p = subcommands.add_parser(
        "diagnose", help="inspect a packet directory read-only and report recovery status",
    )
    diag_p.add_argument("packet", type=Path)
    diag_p.add_argument("--repo", type=Path, default=None)
    diag_p.add_argument("--json", action="store_true", dest="as_json")

    rebuild_p = subcommands.add_parser(
        "rebuild", help="rebuild a damaged or bundle-less packet into a new directory",
    )
    rebuild_p.add_argument("damaged_packet", type=Path)
    rebuild_p.add_argument("output", type=Path)
    rebuild_p.add_argument("--repo", type=Path, default=None)
    rebuild_p.add_argument("--base-ref", default=None)
    rebuild_p.add_argument("--head-ref", default=None)
    rebuild_p.add_argument("--salvage-comments", action="store_true")
    rebuild_p.add_argument("--trust-bundle", action="store_true")
    rebuild_p.add_argument("--json", action="store_true", dest="as_json")

    salvage_p = subcommands.add_parser(
        "salvage-comments",
        help="upgrade v1, split duplicate IDs, and reanchor/orphan comments against a target packet",
    )
    salvage_p.add_argument("source_comments", type=Path)
    salvage_p.add_argument("target_packet", type=Path)
    salvage_p.add_argument("--output", type=Path, default=None)
    salvage_p.add_argument("--in-place", action="store_true")
    salvage_p.add_argument("--json", action="store_true", dest="as_json")

    clean_p = subcommands.add_parser(
        "clean-temp", help="list or remove leftover atomic temporary files in a packet",
    )
    clean_p.add_argument("packet", type=Path)
    clean_p.add_argument("--apply", action="store_true")
    clean_p.add_argument("--json", action="store_true", dest="as_json")

    args = parser.parse_args(argv)
    try:
        if args.command == "diagnose":
            report = diagnose_packet(args.packet, repo=args.repo)
            if args.as_json:
                print(skein._json_text(report), end="")
            else:
                print(
                    f"Diagnosed {args.packet}: status={report['status']}, "
                    f"missing={len(report['missing_members'])}, "
                    f"corrupted={len(report['corrupted_members'])}, "
                    f"temp={len(report['temp_files'])}, "
                    f"comments={report['comments_status']}"
                )
            if report["status"] == "healthy":
                return 0
            return 1 if report["status"] == "recoverable" else 2

        if args.command == "rebuild":
            result = rebuild_packet(
                args.damaged_packet,
                args.output,
                repo=args.repo,
                base_ref=args.base_ref,
                head_ref=args.head_ref,
                salvage_comments=args.salvage_comments,
                trust_bundle=args.trust_bundle,
            )
            if args.as_json:
                print(skein._json_text(result), end="")
            else:
                print(
                    f"Rebuilt packet into {result['output']} "
                    f"({result['base_commit']} -> {result['head_commit']}, "
                    f"comments={result['comments_action']})"
                )
            return 0

        if args.command == "salvage-comments":
            if (args.output is None) == (not args.in_place):
                raise skein.SkeinError("specify exactly one of --output PATH or --in-place")
            target = args.target_packet.expanduser()
            if target.is_symlink() or not target.is_dir():
                raise skein.SkeinError(f"target packet must be a regular directory: {args.target_packet}")
            target_resolved = target.resolve()
            meta = skein._load_packet(target_resolved)
            anchors = skein._load_anchors(target_resolved)

            src = args.source_comments.expanduser()
            if src.is_symlink():
                raise skein.SkeinError("source comments must not be a symlink")
            src_file = (src / "comments.json") if src.is_dir() else src
            if src_file.is_symlink() or not src_file.is_file():
                raise skein.SkeinError(f"source comments file does not exist: {src_file}")
            raw_bytes = src_file.read_bytes()
            if len(raw_bytes) > skein.JSON_LIMIT:
                raise skein.SkeinError("source comments exceed size limit")

            salvaged, summary = salvage_comments_list(
                raw_bytes.decode("utf-8"),
                base_commit=meta["base"]["commit"],
                head_commit=meta["head"]["commit"],
                anchors=anchors,
            )
            if args.in_place:
                skein._atomic_comments(target_resolved, salvaged)
                summary["output"] = str(target_resolved / "comments.json")
            else:
                out_path = args.output.expanduser()
                if out_path.exists() or out_path.is_symlink():
                    raise skein.SkeinError(f"refusing to overwrite existing file: {args.output}")
                out_path.parent.mkdir(parents=True, exist_ok=True)
                skein._write(out_path, skein.dumps_comments(salvaged))
                summary["output"] = str(out_path)
            if args.as_json:
                print(skein._json_text(summary), end="")
            else:
                print(
                    f"Salvaged {summary['total_comments']} comments to {summary['output']} "
                    f"(intact={len(summary['intact_ids'])}, "
                    f"reanchored={len(summary['reanchored_ids'])}, "
                    f"orphaned={len(summary['orphaned_ids'])}, "
                    f"divergent={len(summary['divergent_ids'])})"
                )
            return 0

        if args.command == "clean-temp":
            result = clean_temp_files(args.packet, apply=args.apply)
            if args.as_json:
                print(skein._json_text(result), end="")
            else:
                print(
                    f"Temp files in {args.packet}: found={len(result['temp_files'])}, "
                    f"removed={len(result['removed'])}"
                )
            return 0
    except (skein.SkeinError, OSError, UnicodeDecodeError) as exc:
        print(f"recovery: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
