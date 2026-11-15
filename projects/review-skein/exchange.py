#!/usr/bin/env python3
"""Skein milestone 3: deterministic multi-reviewer comment merge and revised patches.

Consumes Skein's strict version-2 comment, anchor and packet formats using only
the Python standard library. It never contacts a forge, opens a network socket
or mutates a user's Git repository refs.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Iterable

import skein


DIVERGENT_RE = re.compile(
    r"\A(?P<base>[A-Za-z0-9][A-Za-z0-9._-]{0,79})--divergent-(?P<digest>[0-9a-f]{8})\Z"
)


@dataclass(frozen=True)
class MergeResult:
    comments: list[skein.Comment]
    kept_ids: tuple[str, ...]
    divergent_ids: tuple[str, ...]
    resolved_from_base_ids: tuple[str, ...]

    def to_dict(self, *, base_commit: str, head_commit: str) -> dict[str, Any]:
        return {
            "base_commit": base_commit,
            "head_commit": head_commit,
            "total_comments": len(self.comments),
            "anchored_comments": sum(c.state == "anchored" for c in self.comments),
            "orphan_comments": sum(c.state == "orphan" for c in self.comments),
            "open_comments": sum(c.resolution == "open" for c in self.comments),
            "resolved_comments": sum(c.resolution == "resolved" for c in self.comments),
            "kept_ids": list(self.kept_ids),
            "divergent_ids": list(self.divergent_ids),
            "resolved_from_base_ids": list(self.resolved_from_base_ids),
        }


def base_comment_id(identifier: str) -> str:
    """Return the logical comment ID before any deterministic divergence suffix."""
    match = DIVERGENT_RE.fullmatch(identifier)
    return match.group("base") if match is not None else identifier


def _normalized_comment(comment: skein.Comment) -> skein.Comment:
    return replace(comment, identifier=base_comment_id(comment.identifier))


def variant_digest(comment: skein.Comment) -> str:
    """Compute an 8-hex-character content digest of a normalized Comment record."""
    normalized = _normalized_comment(comment)
    canonical = json.dumps(
        normalized.to_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:8]


def _origin_digest(comment: skein.Comment) -> str:
    """Compute a revision-stable 8-hex digest from origin anchor, body and resolution."""
    origin = comment.rebased_from if comment.rebased_from is not None else comment.anchor
    payload = {
        "origin_anchor": origin.to_dict(),
        "body": comment.body,
        "resolution": comment.resolution,
    }
    canonical = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()[:8]


def divergent_comment_id(base_id: str, comment: skein.Comment, *, fallback_full: bool = False) -> str:
    prefix = base_id[:79].rstrip(".-_") or base_id[:79]
    digest = variant_digest(comment) if fallback_full else _origin_digest(comment)
    return f"{prefix}--divergent-{digest}"


def comment_sort_key(comment: skein.Comment) -> tuple[str, int, int, str, str]:
    side_rank = 0 if comment.anchor.side == "old" else 1
    return (
        comment.anchor.path,
        side_rank,
        comment.anchor.line,
        comment.anchor.commit,
        comment.identifier,
    )


def _load_comments_file(path: Path) -> list[skein.Comment]:
    if path.is_symlink() or not path.is_file():
        raise skein.SkeinError(f"comments must be a regular file, not a symlink: {path}")
    data = path.read_bytes()
    if len(data) > skein.JSON_LIMIT:
        raise skein.SkeinError(f"packet JSON exceeds {skein.JSON_LIMIT} bytes: {path.name}")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise skein.SkeinError(f"invalid UTF-8 in {path.name}: {exc}") from exc
    return skein.loads_comments(text)


def _validate_comments_for_packet(
    comments: list[skein.Comment], *, base_commit: str, head_commit: str,
    anchors: set[skein.Anchor],
) -> None:
    for comment in comments:
        expected_commit = base_commit if comment.anchor.side == "old" else head_commit
        if comment.anchor.commit != expected_commit:
            raise skein.SkeinError(
                f"comment {comment.identifier!r} commit does not match packet "
                f"{comment.anchor.side} revision"
            )
        if comment.state == "anchored" and comment.anchor not in anchors:
            raise skein.SkeinError(
                f"comment {comment.identifier!r} anchor does not match a rendered line in packet"
            )


def _load_packet_state(
    packet: Path,
) -> tuple[dict[str, Any], str, str, list[skein.Anchor], list[skein.Comment]]:
    raw = packet.expanduser()
    if raw.is_symlink() or not raw.is_dir():
        raise skein.SkeinError(f"packet must be a regular directory: {packet}")
    resolved = raw.resolve()
    metadata = skein._load_packet(resolved)
    base_commit = metadata["base"]["commit"]
    head_commit = metadata["head"]["commit"]
    anchors = skein._load_anchors(resolved)
    comments = _load_comments_file(resolved / "comments.json")
    _validate_comments_for_packet(
        comments, base_commit=base_commit, head_commit=head_commit, anchors=set(anchors),
    )
    return metadata, base_commit, head_commit, anchors, comments


def _load_source_comments(
    source: Path, *, target_base: str, target_head: str,
    target_anchors: set[skein.Anchor], require_same_revision: bool,
) -> list[skein.Comment]:
    raw = source.expanduser()
    if raw.is_symlink():
        raise skein.SkeinError(f"comment source must be a regular path, not a symlink: {source}")
    if raw.is_dir():
        _, src_base, src_head, _, comments = _load_packet_state(raw)
        if require_same_revision and (src_base, src_head) != (target_base, target_head):
            raise skein.SkeinError(
                "source packet revision pair does not match target packet; "
                "use carry or revise for revised patches"
            )
        if (src_base, src_head) == (target_base, target_head):
            _validate_comments_for_packet(
                comments, base_commit=target_base, head_commit=target_head,
                anchors=target_anchors,
            )
        return comments
    if raw.is_file():
        comments = _load_comments_file(raw.resolve())
        if require_same_revision:
            _validate_comments_for_packet(
                comments, base_commit=target_base, head_commit=target_head,
                anchors=target_anchors,
            )
        return comments
    raise skein.SkeinError(f"comment source does not exist: {source}")


def reanchor_comment_to_packet(
    comment: skein.Comment, *, target_base: str, target_head: str,
    old_anchors: list[skein.Anchor], new_anchors: list[skein.Anchor],
    old_set: set[skein.Anchor], new_set: set[skein.Anchor],
) -> skein.Comment:
    """Rebind a comment to a revised packet's base/head anchors idempotently."""
    if comment.anchor.side == "old":
        dest_commit = target_base
        pool = old_anchors
        pool_set = old_set
    else:
        dest_commit = target_head
        pool = new_anchors
        pool_set = new_set

    if comment.anchor.commit == dest_commit:
        if comment.state == "anchored" and comment.anchor in pool_set:
            return comment
        if comment.state == "orphan":
            return comment

    prior_anchor = (
        comment.rebased_from
        if comment.state == "orphan" and comment.rebased_from is not None
        else comment.anchor
    )
    rebound = skein.reanchor(comment, dest_commit, pool)
    if comment.state == "orphan" and comment.rebased_from is not None:
        rebound = replace(rebound, rebased_from=prior_anchor)
    return rebound


def _combine_comment_lists(
    comment_lists: list[list[skein.Comment]], *,
    base_comments: list[skein.Comment] | None,
    on_divergent: str,
) -> MergeResult:
    if on_divergent not in {"keep", "reject"}:
        raise skein.SkeinError("on_divergent must be 'keep' or 'reject'")

    base_digests_by_id: dict[str, set[str]] = {}
    if base_comments is not None:
        for item in base_comments:
            bid = base_comment_id(item.identifier)
            base_digests_by_id.setdefault(bid, set()).add(variant_digest(item))

    variants_by_id: dict[str, dict[str, skein.Comment]] = {}
    raw_ids_by_id: dict[str, set[str]] = {}
    for group in comment_lists:
        for item in group:
            bid = base_comment_id(item.identifier)
            digest = variant_digest(item)
            variants_by_id.setdefault(bid, {})[digest] = _normalized_comment(item)
            raw_ids_by_id.setdefault(bid, set()).add(item.identifier)

    emitted: list[skein.Comment] = []
    divergent_ids: list[str] = []
    resolved_from_base_ids: list[str] = []

    for bid in sorted(variants_by_id):
        variants = dict(variants_by_id[bid])
        base_digests = base_digests_by_id.get(bid, set())
        if len(variants) > 1 and base_digests:
            modified = {d: v for d, v in variants.items() if d not in base_digests}
            if modified:
                variants = modified
                if len(variants) == 1:
                    resolved_from_base_ids.append(bid)

        if len(variants) == 1:
            only_comment = next(iter(variants.values()))
            raw_ids = raw_ids_by_id[bid]
            chosen_id = (
                next(iter(raw_ids))
                if len(raw_ids) == 1 and bid not in raw_ids
                else bid
            )
            emitted.append(replace(only_comment, identifier=chosen_id))
        else:
            divergent_ids.append(bid)
            if on_divergent == "keep":
                ordered_variants = [variants[d] for d in sorted(variants)]
                candidate_ids = [divergent_comment_id(bid, v) for v in ordered_variants]
                use_full = len(set(candidate_ids)) != len(candidate_ids)
                for variant in ordered_variants:
                    emitted.append(
                        replace(
                            variant,
                            identifier=divergent_comment_id(bid, variant, fallback_full=use_full),
                        )
                    )

    if divergent_ids and on_divergent == "reject":
        raise skein.SkeinError(
            f"divergent comment ID(s) require --on-divergent keep: {', '.join(divergent_ids)}"
        )

    emitted.sort(key=comment_sort_key)
    return MergeResult(
        comments=emitted,
        kept_ids=tuple(item.identifier for item in emitted),
        divergent_ids=tuple(divergent_ids),
        resolved_from_base_ids=tuple(resolved_from_base_ids),
    )


def merge_comments(
    target: Path, sources: Iterable[Path], *,
    base: Path | None = None, on_divergent: str = "keep",
) -> MergeResult:
    """Deterministically merge one or more same-revision comment sets into target."""
    if on_divergent not in {"keep", "reject"}:
        raise skein.SkeinError("on_divergent must be 'keep' or 'reject'")
    source_paths = list(sources)
    if not source_paths:
        raise skein.SkeinError("at least one comment source is required")

    _, target_base, target_head, anchors, target_comments = _load_packet_state(target)
    anchor_set = set(anchors)
    loaded_sources = [
        _load_source_comments(
            src, target_base=target_base, target_head=target_head,
            target_anchors=anchor_set, require_same_revision=True,
        )
        for src in source_paths
    ]
    loaded_base = (
        _load_source_comments(
            base, target_base=target_base, target_head=target_head,
            target_anchors=anchor_set, require_same_revision=True,
        )
        if base is not None else None
    )

    result = _combine_comment_lists(
        [target_comments, *loaded_sources],
        base_comments=loaded_base,
        on_divergent=on_divergent,
    )
    skein._atomic_comments(target.expanduser().resolve(), result.comments)
    return result


def carry_comments(
    target: Path, sources: Iterable[Path], *,
    base: Path | None = None, on_divergent: str = "keep",
) -> MergeResult:
    """Reanchor and deterministically merge comments from earlier revisions into target."""
    if on_divergent not in {"keep", "reject"}:
        raise skein.SkeinError("on_divergent must be 'keep' or 'reject'")
    source_paths = list(sources)
    if not source_paths:
        raise skein.SkeinError("at least one comment source is required")

    _, target_base, target_head, anchors, target_comments = _load_packet_state(target)
    old_anchors = [a for a in anchors if a.side == "old" and a.commit == target_base]
    new_anchors = [a for a in anchors if a.side == "new" and a.commit == target_head]
    old_set = set(old_anchors)
    new_set = set(new_anchors)
    anchor_set = set(anchors)

    def reanchor_group(comments: list[skein.Comment]) -> list[skein.Comment]:
        return [
            reanchor_comment_to_packet(
                item, target_base=target_base, target_head=target_head,
                old_anchors=old_anchors, new_anchors=new_anchors,
                old_set=old_set, new_set=new_set,
            )
            for item in comments
        ]

    loaded_sources = [
        reanchor_group(
            _load_source_comments(
                src, target_base=target_base, target_head=target_head,
                target_anchors=anchor_set, require_same_revision=False,
            )
        )
        for src in source_paths
    ]
    loaded_base = (
        reanchor_group(
            _load_source_comments(
                base, target_base=target_base, target_head=target_head,
                target_anchors=anchor_set, require_same_revision=False,
            )
        )
        if base is not None else None
    )

    result = _combine_comment_lists(
        [reanchor_group(target_comments), *loaded_sources],
        base_comments=loaded_base,
        on_divergent=on_divergent,
    )
    skein._atomic_comments(target.expanduser().resolve(), result.comments)
    return result


def revise_packet(
    repository: Path, base_ref: str, head_ref: str, output: Path, *,
    sources: Iterable[Path], base: Path | None = None,
    on_divergent: str = "keep",
    max_file_bytes: int = skein.DEFAULT_MAX_FILE_BYTES,
) -> tuple[dict[str, Any], MergeResult]:
    """Export a revised packet and atomically carry comments from prior packet(s)."""
    if on_divergent not in {"keep", "reject"}:
        raise skein.SkeinError("on_divergent must be 'keep' or 'reject'")
    source_paths = list(sources)
    if not source_paths:
        raise skein.SkeinError("at least one comment source is required")

    # Pre-validate all sources and base before exporting so bad sources fail early.
    empty_anchors: set[skein.Anchor] = set()
    for src in source_paths:
        _load_source_comments(
            src, target_base="0" * 40, target_head="0" * 40,
            target_anchors=empty_anchors, require_same_revision=False,
        )
    if base is not None:
        _load_source_comments(
            base, target_base="0" * 40, target_head="0" * 40,
            target_anchors=empty_anchors, require_same_revision=False,
        )

    metadata = skein.export_packet(
        repository, base_ref, head_ref, output, max_file_bytes=max_file_bytes,
    )
    completed = False
    try:
        result = carry_comments(output, source_paths, base=base, on_divergent=on_divergent)
        skein.verify_packet(output)
        completed = True
        return metadata, result
    finally:
        if not completed:
            shutil.rmtree(output.expanduser().resolve(), ignore_errors=True)


def _load_comparison_endpoint(
    endpoint: Path,
) -> tuple[str | None, str | None, list[skein.Comment]]:
    raw = endpoint.expanduser()
    if raw.is_symlink():
        raise skein.SkeinError(f"comparison path must not be a symlink: {endpoint}")
    if raw.is_dir():
        _, base_commit, head_commit, _, comments = _load_packet_state(raw)
        return base_commit, head_commit, comments
    if raw.is_file():
        return None, None, _load_comments_file(raw.resolve())
    raise skein.SkeinError(f"comparison path does not exist: {endpoint}")


def compare_packets(first: Path, second: Path) -> dict[str, Any]:
    """Compare two packets or comments.json files without mutating either input."""
    base_a, head_a, comments_a = _load_comparison_endpoint(first)
    base_b, head_b, comments_b = _load_comparison_endpoint(second)

    def group(comments: list[skein.Comment]) -> dict[str, dict[str, skein.Comment]]:
        by_id: dict[str, dict[str, skein.Comment]] = {}
        for item in comments:
            bid = base_comment_id(item.identifier)
            by_id.setdefault(bid, {})[item.identifier] = item
        return by_id

    map_a = group(comments_a)
    map_b = group(comments_b)

    only_in_first: list[str] = []
    only_in_second: list[str] = []
    identical: list[str] = []
    resolved_or_edited: list[str] = []
    reanchored: list[str] = []
    newly_orphaned: list[str] = []
    divergent: list[str] = []

    for bid in sorted(set(map_a) | set(map_b)):
        if bid not in map_b:
            only_in_first.extend(sorted(map_a[bid]))
            continue
        if bid not in map_a:
            only_in_second.extend(sorted(map_b[bid]))
            continue
        va = map_a[bid]
        vb = map_b[bid]
        if set(va) != set(vb):
            divergent.append(bid)
            continue
        for cid in sorted(va):
            ca = va[cid]
            cb = vb[cid]
            if ca == cb:
                identical.append(cid)
            elif ca.anchor.commit == cb.anchor.commit:
                if (ca.anchor != cb.anchor or ca.state != cb.state
                        or ca.rebased_from != cb.rebased_from):
                    divergent.append(cid)
                else:
                    resolved_or_edited.append(cid)
            else:
                expected_origin = (
                    ca.rebased_from
                    if ca.state == "orphan" and ca.rebased_from is not None
                    else ca.anchor
                )
                if (cb.rebased_from is None
                        or (cb.rebased_from.path, cb.rebased_from.side, cb.rebased_from.text)
                        != (expected_origin.path, expected_origin.side, expected_origin.text)):
                    divergent.append(cid)
                elif ca.state != "orphan" and cb.state == "orphan":
                    newly_orphaned.append(cid)
                elif ca.anchor != cb.anchor or ca.state != cb.state:
                    reanchored.append(cid)
                else:
                    resolved_or_edited.append(cid)

    same_revision = (
        base_a is not None and base_b is not None
        and (base_a, head_a) == (base_b, head_b)
    )
    return {
        "first": {"base": base_a, "head": head_a, "total_comments": len(comments_a)},
        "second": {"base": base_b, "head": head_b, "total_comments": len(comments_b)},
        "same_revision": same_revision,
        "only_in_first": only_in_first,
        "only_in_second": only_in_second,
        "identical": identical,
        "resolved_or_edited": resolved_or_edited,
        "reanchored": reanchored,
        "newly_orphaned": newly_orphaned,
        "divergent": divergent,
    }


def _format_merge_summary(action: str, target: Path, report: dict[str, Any]) -> str:
    lines = [
        f"{action} into {target}: {report['total_comments']} comments "
        f"({report['anchored_comments']} anchored, {report['orphan_comments']} orphan; "
        f"{report['open_comments']} open, {report['resolved_comments']} resolved)",
        f"Revision pair: {report['base_commit']} -> {report['head_commit']}",
    ]
    if report["resolved_from_base_ids"]:
        lines.append("Reconciled against base: " + ", ".join(report["resolved_from_base_ids"]))
    if report["divergent_ids"]:
        lines.append("Divergent base IDs kept: " + ", ".join(report["divergent_ids"]))
    return "\n".join(lines)


def _format_comparison(report: dict[str, Any]) -> str:
    lines = [
        f"First: {report['first']['total_comments']} comments "
        f"({report['first']['base']} -> {report['first']['head']})",
        f"Second: {report['second']['total_comments']} comments "
        f"({report['second']['base']} -> {report['second']['head']})",
        f"Same revision pair: {'yes' if report['same_revision'] else 'no'}",
    ]
    for key, label in (
        ("identical", "Identical"),
        ("only_in_first", "Only in first"),
        ("only_in_second", "Only in second"),
        ("resolved_or_edited", "Resolved or edited"),
        ("reanchored", "Reanchored"),
        ("newly_orphaned", "Newly orphaned"),
        ("divergent", "Divergent"),
    ):
        values = report[key]
        lines.append(f"{label} ({len(values)}): {', '.join(values) if values else 'none'}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subcommands = parser.add_subparsers(dest="command", required=True)

    for cmd, help_text in (
        ("merge", "deterministically merge same-revision reviewer packets or comments.json files"),
        ("carry", "reanchor and merge comments from earlier packet revisions into target"),
    ):
        sub = subcommands.add_parser(cmd, help=help_text)
        sub.add_argument("packet", type=Path, help="target packet directory to update")
        sub.add_argument("sources", type=Path, nargs="+", help="source packet directories or comments.json files")
        sub.add_argument("--base", type=Path, default=None, help="optional common-ancestor packet or comments.json")
        sub.add_argument(
            "--on-divergent", choices=("keep", "reject"), default="keep",
            help="keep divergent same-ID comments under deterministic content suffixes or reject",
        )
        sub.add_argument("--json", action="store_true", dest="as_json", help="print machine-readable JSON summary")

    revise = subcommands.add_parser(
        "revise", help="export a revised packet and atomically carry comments from earlier packets",
    )
    revise.add_argument("repository", type=Path)
    revise.add_argument("base_ref")
    revise.add_argument("head_ref")
    revise.add_argument("output", type=Path)
    revise.add_argument("--from", dest="sources", type=Path, nargs="+", required=True)
    revise.add_argument("--base", type=Path, default=None)
    revise.add_argument("--on-divergent", choices=("keep", "reject"), default="keep")
    revise.add_argument("--max-file-bytes", type=int, default=skein.DEFAULT_MAX_FILE_BYTES)
    revise.add_argument("--json", action="store_true", dest="as_json")

    compare = subcommands.add_parser(
        "compare", help="compare comments across two packets or comments.json files without writing",
    )
    compare.add_argument("first", type=Path)
    compare.add_argument("second", type=Path)
    compare.add_argument("--json", action="store_true", dest="as_json")

    arguments = parser.parse_args(argv)
    try:
        if arguments.command in {"merge", "carry"}:
            fn = merge_comments if arguments.command == "merge" else carry_comments
            result = fn(
                arguments.packet, arguments.sources,
                base=arguments.base, on_divergent=arguments.on_divergent,
            )
            _, base_commit, head_commit, _, _ = _load_packet_state(arguments.packet)
            report = result.to_dict(base_commit=base_commit, head_commit=head_commit)
            if arguments.as_json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                label = "Merged comments" if arguments.command == "merge" else "Carried comments"
                print(_format_merge_summary(label, arguments.packet, report))
            return 0
        if arguments.command == "revise":
            metadata, result = revise_packet(
                arguments.repository, arguments.base_ref, arguments.head_ref,
                arguments.output, sources=arguments.sources, base=arguments.base,
                on_divergent=arguments.on_divergent, max_file_bytes=arguments.max_file_bytes,
            )
            report = result.to_dict(
                base_commit=metadata["base"]["commit"],
                head_commit=metadata["head"]["commit"],
            )
            if arguments.as_json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(_format_merge_summary("Exported revised packet and carried comments", arguments.output, report))
            return 0
        if arguments.command == "compare":
            report = compare_packets(arguments.first, arguments.second)
            if arguments.as_json:
                print(json.dumps(report, indent=2, sort_keys=True))
            else:
                print(_format_comparison(report))
            return 0
    except (skein.SkeinError, OSError) as exc:
        parser.exit(2, f"exchange: {exc}\n")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
