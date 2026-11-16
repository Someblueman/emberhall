#!/usr/bin/env python3
"""Read-only offline two-revision interdiff and comment-transition view for Review Skein."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
import json
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence

import exchange
import review_view
import skein


VALID_FORMATS = ("text", "html", "json")


@dataclass(frozen=True)
class _CommentEntry:
    comment: skein.Comment
    origin: str  # "V2", "V1-only", or "V1" for an older divergent record
    transition: str


@dataclass(frozen=True)
class _PlacedInterdiffFile:
    change: skein.Change
    old_lines: list[str]
    new_lines: list[str]
    rows: list[review_view._DiffRow]
    # Per row: (V1 entries / V2 orphans, V2 anchored entries)
    row_comments: list[tuple[list[_CommentEntry], list[_CommentEntry]]]


@dataclass(frozen=True)
class _InterdiffPlan:
    meta_v1: dict[str, Any]
    meta_v2: dict[str, Any]
    comments_v1: list[skein.Comment]
    comments_v2: list[skein.Comment]
    transitions: dict[str, Any]
    all_entries: list[_CommentEntry]
    selected_entries: list[_CommentEntry]
    placed_files: list[_PlacedInterdiffFile]
    visible_files: list[_PlacedInterdiffFile]
    unchanged_entries: list[_CommentEntry]
    base_entries: list[_CommentEntry]
    orphan_entries: list[tuple[_CommentEntry, str]]
    placements: dict[str, list[str]]


def _visible(value: str) -> str:
    return review_view._visible(value)


def _visible_multiline(value: str) -> str:
    return review_view._visible_multiline(value)


def _validate_interdiff_options(
    output_format: str,
    resolution: str,
    state: str,
    context: int,
    max_file_bytes: int,
    paths: Sequence[str] | None = None,
    search: str = "",
    only_commented: bool = False,
) -> tuple[tuple[str, ...], str]:
    if output_format not in VALID_FORMATS:
        raise ValueError(f"output_format must be one of {VALID_FORMATS}: {output_format!r}")
    return review_view._validate_options(
        "text", resolution, state, context, max_file_bytes,
        paths=paths, search=search, only_commented=only_commented,
    )


def _load_interdiff_tree(
    first: Path,
    second: Path,
    head_v1: str,
    head_v2: str,
    max_file_bytes: int,
) -> list[tuple[skein.Change, list[str], list[str], list[review_view._DiffRow]]]:
    bundle_v1 = first.expanduser().resolve() / "changes.bundle"
    bundle_v2 = second.expanduser().resolve() / "changes.bundle"
    rendered: list[tuple[skein.Change, list[str], list[str], list[review_view._DiffRow]]] = []
    with tempfile.TemporaryDirectory(prefix="skein-interdiff-") as temporary:
        root = Path(temporary)
        repo = root / "repo.git"
        skein._git(root, "init", "--bare", "--quiet", str(repo))
        skein._git(repo, "fetch", "--quiet", str(bundle_v1), "refs/heads/skein-head:refs/skein/v1")
        skein._git(repo, "fetch", "--quiet", str(bundle_v2), "refs/heads/skein-head:refs/skein/v2")
        fetched_v1 = skein._git(repo, "rev-parse", "--verify", "refs/skein/v1^{commit}").stdout.decode("utf-8").strip()
        fetched_v2 = skein._git(repo, "rev-parse", "--verify", "refs/skein/v2^{commit}").stdout.decode("utf-8").strip()
        if fetched_v1 != head_v1 or fetched_v2 != head_v2:
            raise skein.SkeinError("bundle skein-head ref does not match packet head commit")

        old_tree = skein._tree(repo, head_v1)
        new_tree = skein._tree(repo, head_v2)
        changes = skein._changes(repo, head_v1, head_v2)
        reader = skein.BlobReader(repo, max_file_bytes)
        for change in changes:
            old_entry = old_tree.get(change.old_path) if change.old_path else None
            new_entry = new_tree.get(change.new_path) if change.new_path else None
            old_lines = reader.read(old_entry)
            new_lines = reader.read(new_entry)
            rows = review_view._build_rows(old_lines, new_lines)
            rendered.append((change, old_lines, new_lines, rows))
    return rendered


def _transition_label_map(transitions: dict[str, Any]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for key, label in (
        ("identical", "unchanged"),
        ("resolved_or_edited", "resolved/edited"),
        ("reanchored", "reanchored"),
        ("newly_orphaned", "newly orphaned"),
        ("only_in_second", "new in V2"),
        ("divergent", "divergent"),
    ):
        for identifier in transitions.get(key, ()):
            labels[identifier] = label
    return labels


def _entry_matches_paths(entry: _CommentEntry, patterns: Sequence[str]) -> bool:
    if not patterns:
        return True
    comment = entry.comment
    if review_view._comment_matches_paths(comment, patterns):
        return True
    if comment.rebased_from is not None:
        return any(review_view._path_matches(comment.rebased_from.path, p) for p in patterns)
    return False


def _entry_matches_search(entry: _CommentEntry, query: str) -> bool:
    if not query:
        return True
    if review_view._comment_matches_search(entry.comment, query):
        return True
    needle = query.casefold()
    return needle in entry.origin.casefold() or needle in entry.transition.casefold()


def _place_interdiff_comments(
    head_v1: str,
    head_v2: str,
    selected: Sequence[_CommentEntry],
    rendered: Sequence[tuple[skein.Change, list[str], list[str], list[review_view._DiffRow]]],
) -> tuple[
    list[_PlacedInterdiffFile],
    list[_CommentEntry],
    list[_CommentEntry],
    list[tuple[_CommentEntry, str]],
    dict[str, list[str]],
]:
    old_row_targets: dict[skein.Anchor, list[_CommentEntry]] = {}
    new_row_targets: dict[skein.Anchor, list[_CommentEntry]] = {}
    changed_old_paths = {change.old_path for change, *_ in rendered if change.old_path}
    changed_new_paths = {change.new_path for change, *_ in rendered if change.new_path}

    valid_old_anchors: set[skein.Anchor] = set()
    valid_new_anchors: set[skein.Anchor] = set()
    for change, _, _, rows in rendered:
        for row in rows:
            if change.old_path is not None and row.old_number is not None:
                valid_old_anchors.add(
                    skein.Anchor(head_v1, change.old_path, "new", row.old_number, row.old_text)
                )
            if change.new_path is not None and row.new_number is not None:
                valid_new_anchors.add(
                    skein.Anchor(head_v2, change.new_path, "new", row.new_number, row.new_text)
                )

    unchanged_entries: list[_CommentEntry] = []
    base_entries: list[_CommentEntry] = []
    orphan_entries: list[tuple[_CommentEntry, str]] = []
    placements: dict[str, list[str]] = {
        "inline_v2": [],
        "inline_v1_orphan": [],
        "inline_v1_only": [],
        "inline_v1_divergent": [],
        "unchanged_files": [],
        "base_side": [],
        "orphans_unplaced": [],
    }

    for entry in selected:
        comment = entry.comment
        if entry.origin == "V2":
            if comment.state == "anchored" and comment.anchor.side == "new":
                if comment.anchor in valid_new_anchors:
                    new_row_targets.setdefault(comment.anchor, []).append(entry)
                    placements["inline_v2"].append(comment.identifier)
                elif comment.anchor.path not in changed_new_paths:
                    unchanged_entries.append(entry)
                    placements["unchanged_files"].append(comment.identifier)
                else:
                    orphan_entries.append((entry, "anchor target does not match V2 head line"))
                    placements["orphans_unplaced"].append(comment.identifier)
            elif comment.state == "anchored" and comment.anchor.side == "old":
                base_entries.append(entry)
                placements["base_side"].append(comment.identifier)
            else:
                rebased = comment.rebased_from
                if (
                    rebased is not None
                    and rebased.side == "new"
                    and rebased.commit == head_v1
                    and rebased in valid_old_anchors
                ):
                    old_row_targets.setdefault(rebased, []).append(entry)
                    placements["inline_v1_orphan"].append(comment.identifier)
                else:
                    reason = comment.orphan_reason or "orphaned comment"
                    orphan_entries.append((entry, reason))
                    placements["orphans_unplaced"].append(comment.identifier)
        else:
            # V1-only comment (present in V1, absent from V2)
            if comment.state == "anchored" and comment.anchor.side == "new":
                if comment.anchor in valid_old_anchors:
                    old_row_targets.setdefault(comment.anchor, []).append(entry)
                    bucket = "inline_v1_divergent" if entry.origin == "V1" else "inline_v1_only"
                    placements[bucket].append(comment.identifier)
                elif comment.anchor.path not in changed_old_paths:
                    unchanged_entries.append(entry)
                    placements["unchanged_files"].append(comment.identifier)
                else:
                    orphan_entries.append((entry, "V1 anchor target does not match V1 head line"))
                    placements["orphans_unplaced"].append(comment.identifier)
            elif comment.state == "anchored" and comment.anchor.side == "old":
                base_entries.append(entry)
                placements["base_side"].append(comment.identifier)
            else:
                reason = comment.orphan_reason or "V1-only orphaned comment"
                orphan_entries.append((entry, reason))
                placements["orphans_unplaced"].append(comment.identifier)

    placed_files: list[_PlacedInterdiffFile] = []
    for change, old_lines, new_lines, rows in rendered:
        row_comments: list[tuple[list[_CommentEntry], list[_CommentEntry]]] = []
        for row in rows:
            old_list: list[_CommentEntry] = []
            new_list: list[_CommentEntry] = []
            if change.old_path is not None and row.old_number is not None:
                old_key = skein.Anchor(
                    head_v1, change.old_path, "new", row.old_number, row.old_text
                )
                old_list = old_row_targets.get(old_key, [])
            if change.new_path is not None and row.new_number is not None:
                new_key = skein.Anchor(
                    head_v2, change.new_path, "new", row.new_number, row.new_text
                )
                new_list = new_row_targets.get(new_key, [])
            row_comments.append((old_list, new_list))
        placed_files.append(_PlacedInterdiffFile(change, old_lines, new_lines, rows, row_comments))

    return placed_files, unchanged_entries, base_entries, orphan_entries, placements


def _file_entry_counts(placed: _PlacedInterdiffFile) -> tuple[int, int]:
    open_count = 0
    resolved_count = 0
    for old_c, new_c in placed.row_comments:
        for entry in (*old_c, *new_c):
            if entry.comment.resolution == "resolved":
                resolved_count += 1
            else:
                open_count += 1
    return open_count, resolved_count


def _build_plan(
    first: Path,
    second: Path,
    *,
    resolution: str,
    state: str,
    max_file_bytes: int,
    norm_paths: Sequence[str],
    norm_search: str,
    only_commented: bool,
) -> _InterdiffPlan:
    meta_v1, comments_v1, _ = review_view._load_verified_packet(first, max_file_bytes)
    meta_v2, comments_v2, _ = review_view._load_verified_packet(second, max_file_bytes)

    first_resolved = first.expanduser().resolve()
    second_resolved = second.expanduser().resolve()
    transitions = exchange.compare_packets(first_resolved, second_resolved)
    labels = _transition_label_map(transitions)
    only_first_set = set(transitions["only_in_first"])
    divergent = set(transitions["divergent"])
    second_by_id = {comment.identifier: comment for comment in comments_v2}

    all_entries: list[_CommentEntry] = [
        _CommentEntry(
            comment=comment,
            origin="V2",
            transition=labels.get(comment.identifier) or labels.get(exchange.base_comment_id(comment.identifier), "carried"),
        )
        for comment in comments_v2
    ]
    for comment in comments_v1:
        if comment.identifier in only_first_set:
            all_entries.append(_CommentEntry(comment, "V1-only", "only in V1"))
        elif (comment.identifier in divergent
              or exchange.base_comment_id(comment.identifier) in divergent):
            # compare_packets reports differing variant sets by logical ID. Keep
            # every distinct older record, even when its exact ID also exists in
            # V2; an identical shared record is already represented by V2.
            if comment != second_by_id.get(comment.identifier):
                all_entries.append(_CommentEntry(comment, "V1", "divergent"))

    selected_entries = [
        entry
        for entry in all_entries
        if (resolution == "all" or entry.comment.resolution == resolution)
        and (state == "all" or entry.comment.state == state)
        and _entry_matches_paths(entry, norm_paths)
        and _entry_matches_search(entry, norm_search)
    ]

    head_v1 = meta_v1["head"]["commit"]
    head_v2 = meta_v2["head"]["commit"]
    rendered = _load_interdiff_tree(first_resolved, second_resolved, head_v1, head_v2, max_file_bytes)
    placed_files, unchanged_entries, base_entries, orphan_entries, placements = _place_interdiff_comments(
        head_v1, head_v2, selected_entries, rendered,
    )
    visible_files = [
        placed
        for placed in placed_files
        if review_view._file_matches_paths(placed.change, norm_paths)
        and (not only_commented or sum(_file_entry_counts(placed)) > 0)
    ]

    return _InterdiffPlan(
        meta_v1=meta_v1,
        meta_v2=meta_v2,
        comments_v1=comments_v1,
        comments_v2=comments_v2,
        transitions=transitions,
        all_entries=all_entries,
        selected_entries=selected_entries,
        placed_files=placed_files,
        visible_files=visible_files,
        unchanged_entries=unchanged_entries,
        base_entries=base_entries,
        orphan_entries=orphan_entries,
        placements=placements,
    )


def _base_status_line(meta_v1: dict[str, Any], meta_v2: dict[str, Any]) -> str:
    b1 = meta_v1["base"]["commit"]
    b2 = meta_v2["base"]["commit"]
    r1 = _visible(meta_v1["base"]["ref"])
    r2 = _visible(meta_v2["base"]["ref"])
    if b1 == b2:
        return f"Base: {r2} ({b2}) — unchanged between revisions."
    return (
        f"Base revision changed between packets (rebased): "
        f"V1 {r1} ({b1}) -> V2 {r2} ({b2}); V1->V2 diff includes upstream base changes."
    )


def _transition_summary_line(transitions: dict[str, Any]) -> str:
    return (
        f"Transitions: {len(transitions['reanchored'])} reanchored, "
        f"{len(transitions['newly_orphaned'])} newly orphaned, "
        f"{len(transitions['resolved_or_edited'])} resolved/edited, "
        f"{len(transitions['identical'])} unchanged, "
        f"{len(transitions['only_in_first'])} V1-only, "
        f"{len(transitions['only_in_second'])} V2-only, "
        f"{len(transitions['divergent'])} divergent."
    )


def _inline_location(entry: _CommentEntry, side_label: str) -> tuple[str, int]:
    comment = entry.comment
    if (
        side_label == "V1"
        and entry.origin == "V2"
        and comment.state == "orphan"
        and comment.rebased_from is not None
    ):
        return side_label, comment.rebased_from.line
    return side_label, comment.anchor.line


def _format_text_entry(
    entry: _CommentEntry,
    *,
    side_label: str | None = None,
    extra_reason: str | None = None,
) -> list[str]:
    comment = entry.comment
    if side_label is not None:
        label, line_num = _inline_location(entry, side_label)
        loc = f"{label} line {line_num}"
    else:
        loc = f"{comment.anchor.side} line {comment.anchor.line}"
    lines = [
        f"    [{_visible(comment.identifier)} | {entry.origin} ({entry.transition}) | "
        f"{comment.resolution} | {comment.state} | {loc}]"
    ]
    if extra_reason is not None:
        lines.append(f"      Reason: {_visible(extra_reason)}")
    if comment.rebased_from is not None:
        lines.append(
            f"      Rebased from: {_visible(review_view.comments_view._anchor_text(comment.rebased_from))}"
        )
    for body_line in _visible_multiline(comment.body).split("\n"):
        lines.append(f"      {body_line}")
    return lines


def _render_text_bucket(title: str, items: Sequence[tuple[_CommentEntry, str | None]]) -> list[str]:
    if not items:
        return []
    lines = ["", f"{title} ({len(items)}):"]
    for entry, reason in items:
        c = entry.comment
        lines.append(
            f"- {_visible(c.identifier)} | {entry.origin} ({entry.transition}) | {c.resolution} | {c.state}"
        )
        lines.append(f"  Anchor: {_visible(review_view.comments_view._anchor_text(c.anchor))}")
        if reason is not None:
            lines.append(f"  Reason: {_visible(reason)}")
        if c.rebased_from is not None:
            lines.append(
                f"  Rebased from: {_visible(review_view.comments_view._anchor_text(c.rebased_from))}"
            )
        lines.append("  Body:")
        for body_line in _visible_multiline(c.body).split("\n"):
            lines.append(f"    {body_line}")
    return lines


def _render_text_hunk(
    rows: Sequence[review_view._DiffRow],
    row_comments: Sequence[tuple[list[_CommentEntry], list[_CommentEntry]]],
    start: int,
    end: int,
) -> list[str]:
    out = [review_view._hunk_header(rows, start, end)]
    index = start
    while index <= end:
        row = rows[index]
        old_c, new_c = row_comments[index]
        if row.kind == "equal":
            out.append(f" {row.old_number:>5} {row.new_number:>5}   {_visible(row.new_text)}")
            for side_label, entry in (
                *[("V1", e) for e in old_c],
                *[("V2", e) for e in new_c],
            ):
                out.extend(_format_text_entry(
                    entry, side_label=side_label, extra_reason=entry.comment.orphan_reason,
                ))
            index += 1
            continue
        if row.kind == "meta":
            note = row.old_text or row.new_text
            out.append(f"       note  {_visible(note)}")
            index += 1
            continue
        run_end = index
        while run_end <= end and rows[run_end].kind in {"delete", "insert", "replace"}:
            run_end += 1
        for pos in range(index, run_end):
            r = rows[pos]
            r_old_c, _ = row_comments[pos]
            if r.old_number is not None:
                out.append(f"-{r.old_number:>5}       - {_visible(r.old_text)}")
                for entry in r_old_c:
                    out.extend(_format_text_entry(
                        entry, side_label="V1", extra_reason=entry.comment.orphan_reason,
                    ))
        for pos in range(index, run_end):
            r = rows[pos]
            _, r_new_c = row_comments[pos]
            if r.new_number is not None:
                out.append(f"+      {r.new_number:>5} + {_visible(r.new_text)}")
                for entry in r_new_c:
                    out.extend(_format_text_entry(entry, side_label="V2"))
        index = run_end
    return out


def _render_text(
    plan: _InterdiffPlan,
    resolution: str,
    state: str,
    context: int,
    norm_paths: Sequence[str],
    norm_search: str,
    only_commented: bool,
) -> str:
    v1_open = sum(1 for c in plan.comments_v1 if c.resolution == "open")
    v1_res = sum(1 for c in plan.comments_v1 if c.resolution == "resolved")
    v2_open = sum(1 for c in plan.comments_v2 if c.resolution == "open")
    v2_res = sum(1 for c in plan.comments_v2 if c.resolution == "resolved")
    v2_orph = sum(1 for c in plan.comments_v2 if c.state == "orphan")

    lines = [
        "Skein revision interdiff",
        f'V1 head: {_visible(plan.meta_v1["head"]["ref"])} ({plan.meta_v1["head"]["commit"]})',
        f'V2 head: {_visible(plan.meta_v2["head"]["ref"])} ({plan.meta_v2["head"]["commit"]})',
        _base_status_line(plan.meta_v1, plan.meta_v2),
        review_view._filter_summary_line(
            len(plan.selected_entries), len(plan.all_entries), resolution, state,
            norm_paths, norm_search, only_commented,
        ),
        f"V1 comments: {len(plan.comments_v1)} ({v1_open} open, {v1_res} resolved). "
        f"V2 comments: {len(plan.comments_v2)} ({v2_open} open, {v2_res} resolved; {v2_orph} orphan).",
        _transition_summary_line(plan.transitions),
        f"Revision-changed files: {len(plan.visible_files)} of {len(plan.placed_files)} shown.",
        "This view is derived read-only from the offline packets; Git hashes bind bytes, not people.",
    ]

    if plan.visible_files:
        lines.append("")
        lines.append("Revision-changed files index:")
        for placed in plan.visible_files:
            change = placed.change
            f_open, f_res = _file_entry_counts(placed)
            summary = review_view._comment_count_summary(f_open, f_res)
            lines.append(f"- {_visible(change.status)}: {_visible(change.display_path)} — {summary}")

    lines.extend(_render_text_bucket(
        "Orphaned and unplaced comments",
        [(e, reason) for e, reason in plan.orphan_entries],
    ))
    lines.extend(_render_text_bucket(
        "Comments on files unchanged between revisions",
        [(e, None) for e in plan.unchanged_entries],
    ))
    lines.extend(_render_text_bucket(
        "Base-side comments (anchored to base commit)",
        [(e, None) for e in plan.base_entries],
    ))

    if not plan.placed_files:
        lines.append("")
        lines.append("The two head revisions have identical file trees.")
        return "\n".join(lines) + "\n"

    if not plan.visible_files:
        lines.append("")
        lines.append("No revision-changed files match the current filters.")
        return "\n".join(lines) + "\n"

    for placed in plan.visible_files:
        change = placed.change
        lines.append("")
        lines.append(
            f"=== {_visible(change.status)}: {_visible(change.display_path)} "
            f"({len(placed.old_lines)} V1 / {len(placed.new_lines)} V2 lines) ==="
        )
        ranges = review_view._visible_ranges(placed.rows, placed.row_comments, context)
        if not ranges:
            lines.append("(no diff lines or matching inline comments in current view)")
            continue
        for start, end in ranges:
            lines.extend(_render_text_hunk(placed.rows, placed.row_comments, start, end))
    return "\n".join(lines) + "\n"


def _render_html_entry_details(entry: _CommentEntry, extra_reason: str | None = None) -> str:
    return review_view._render_html_comment_details(entry.comment, extra_reason=extra_reason)


def _render_html_bucket(
    section_id: str,
    title: str,
    items: Sequence[tuple[_CommentEntry, str | None]],
    counter: list[int],
    navigation: list[str],
    jump_entries: list[tuple[str, _CommentEntry, str]],
) -> str:
    if not items:
        return ""
    navigation.append(f'<li><a href="#{section_id}">{html.escape(title)} ({len(items)})</a></li>')
    cards: list[str] = []
    for entry, reason in items:
        comment = entry.comment
        counter[0] += 1
        dom_id = f"comment-{counter[0]}"
        jump_entries.append((
            dom_id,
            entry,
            f"{section_id}: {_visible(comment.anchor.path)} ({comment.anchor.side} line {comment.anchor.line})",
        ))
        card_title = (
            f"{_visible(comment.identifier)} — {entry.origin} ({entry.transition}), "
            f"{comment.resolution}, {comment.state}"
        )
        anchor_text = _visible(review_view.comments_view._anchor_text(comment.anchor))
        cards.append(
            f'<article class="comment-card" id="{dom_id}">'
            f'<h3 id="{dom_id}-title">{html.escape(card_title)}</h3>'
            f'<p class="comment-extra">Anchor: <code>{html.escape(anchor_text)}</code></p>'
            f'{_render_html_entry_details(entry, extra_reason=reason)}'
            "</article>"
        )
    return (
        f'<section class="orphans" id="{section_id}" aria-labelledby="{section_id}-title">'
        f'<h2 id="{section_id}-title">{html.escape(title)} ({len(items)})</h2>'
        f'{"".join(cards)}</section>\n'
    )


def _render_html_file_rows(
    placed: _PlacedInterdiffFile,
    context: int,
    counter: list[int],
    jump_entries: list[tuple[str, _CommentEntry, str]],
) -> str:
    ranges = review_view._visible_ranges(placed.rows, placed.row_comments, context)
    if not placed.rows:
        return ""
    if not ranges:
        return skein._row(
            None, None,
            f"({len(placed.old_lines)} unchanged lines; no diff or matching comments)",
            "",
            "meta",
        )
    html_rows: list[str] = []
    previous_end = -1
    file_label = _visible(placed.change.display_path)
    for start, end in ranges:
        if start > previous_end + 1:
            skipped = start - (previous_end + 1)
            html_rows.append(skein._row(
                None, None,
                f"@@ {skipped} unchanged line(s) omitted @@",
                "",
                "meta",
            ))
        for index in range(start, end + 1):
            row = placed.rows[index]
            html_rows.append(skein._row(
                row.old_number, row.new_number,
                _visible(row.old_text), _visible(row.new_text), row.kind,
            ))
            old_c, new_c = placed.row_comments[index]
            for side_label, entry in (
                *[("V1", e) for e in old_c],
                *[("V2", e) for e in new_c],
            ):
                comment = entry.comment
                counter[0] += 1
                dom_id = f"comment-{counter[0]}"
                label, line_num = _inline_location(entry, side_label)
                jump_entries.append((
                    dom_id,
                    entry,
                    f"{file_label} ({label} line {line_num})",
                ))
                meta = (
                    f'<span class="sr">Comment.</span> '
                    f'<strong>{html.escape(_visible(comment.identifier))}</strong> '
                    f'({html.escape(entry.origin)}, {html.escape(entry.transition)}, '
                    f'{html.escape(comment.resolution)}, {html.escape(comment.state)}, '
                    f'{label} line {line_num})'
                )
                extra_reason = comment.orphan_reason if comment.state == "orphan" else None
                details = _render_html_entry_details(entry, extra_reason=extra_reason)
                html_rows.append(
                    f'<tr class="comment-row" id="{dom_id}">'
                    f'<th scope="row" colspan="2" class="comment-meta">{meta}</th>'
                    f'<td colspan="2" class="comment-cell">{details}</td></tr>\n'
                )
        previous_end = end
    if previous_end < len(placed.rows) - 1:
        skipped_tail = len(placed.rows) - 1 - previous_end
        html_rows.append(skein._row(
            None, None,
            f"@@ {skipped_tail} unchanged line(s) omitted @@",
            "",
            "meta",
        ))
    return "".join(html_rows)


def _render_html(
    plan: _InterdiffPlan,
    resolution: str,
    state: str,
    context: int,
    norm_paths: Sequence[str],
    norm_search: str,
    only_commented: bool,
) -> str:
    counter = [0]
    navigation: list[str] = []
    jump_entries: list[tuple[str, _CommentEntry, str]] = []

    orphans_html = _render_html_bucket(
        "orphans",
        "Orphaned and unplaced comments",
        [(e, reason) for e, reason in plan.orphan_entries],
        counter, navigation, jump_entries,
    )
    unchanged_html = _render_html_bucket(
        "unchanged-files",
        "Comments on files unchanged between revisions",
        [(e, None) for e in plan.unchanged_entries],
        counter, navigation, jump_entries,
    )
    base_html = _render_html_bucket(
        "base-comments",
        "Base-side comments",
        [(e, None) for e in plan.base_entries],
        counter, navigation, jump_entries,
    )

    sections: list[str] = []
    for index, placed in enumerate(plan.visible_files, 1):
        change = placed.change
        title = f"{_visible(change.status)}: {_visible(change.display_path)}"
        f_open, f_res = _file_entry_counts(placed)
        count_summary = review_view._comment_count_summary(f_open, f_res)
        navigation.append(
            f'<li><a href="#file-{index}">{html.escape(title)}</a> — {html.escape(count_summary)}</li>'
        )
        tbody = _render_html_file_rows(placed, context, counter, jump_entries)
        sections.append(
            f'<section id="file-{index}" aria-labelledby="file-{index}-title">'
            f'<h2 id="file-{index}-title">{html.escape(title)}</h2>\n'
            f'<div class="scroll"><table><caption>V1 line and V2 line; '
            f'{len(placed.old_lines)} V1 / {len(placed.new_lines)} V2</caption>\n'
            '<thead><tr><th scope="col">V1</th><th scope="col">V2</th>'
            '<th scope="col">V1 head text</th><th scope="col">V2 head text</th></tr></thead>\n'
            f'<tbody>{tbody}</tbody></table></div></section>\n'
        )

    buckets_html = "".join((orphans_html, unchanged_html, base_html))
    if not sections and not buckets_html:
        navigation.append("<li>No matching revision-changed files or comments in this view.</li>")
    if sections:
        files_body = "".join(sections)
    elif not plan.placed_files:
        files_body = "<p>The two head revisions have identical file trees.</p>"
    elif buckets_html:
        files_body = "<p>No revision-changed files match the current filters.</p>"
    else:
        files_body = "<p>No revision-changed files or comments match the current filters.</p>"

    comments_nav_html = ""
    if jump_entries:
        items = []
        for dom_id, entry, location in jump_entries:
            comment = entry.comment
            preview = review_view._preview_line(comment.body)
            preview_part = f": {preview}" if preview else ""
            items.append(
                f'<li><a href="#{dom_id}">{html.escape(_visible(comment.identifier))}</a> '
                f'({html.escape(entry.origin)}, {html.escape(entry.transition)}, '
                f'{html.escape(comment.resolution)}, {html.escape(comment.state)}) — '
                f'{html.escape(location)}{html.escape(preview_part)}</li>'
            )
        comments_nav_html = (
            f'<nav id="comments" aria-label="Comments">'
            f'<h2>Comments in view ({len(jump_entries)})</h2>'
            f'<ol>{"".join(items)}</ol></nav>\n'
        )

    v1_head_text = _visible(f'{plan.meta_v1["head"]["ref"]} ({plan.meta_v1["head"]["commit"]})')
    v2_head_text = _visible(f'{plan.meta_v2["head"]["ref"]} ({plan.meta_v2["head"]["commit"]})')
    base_line = _base_status_line(plan.meta_v1, plan.meta_v2)
    showing = review_view._filter_summary_line(
        len(plan.selected_entries), len(plan.all_entries), resolution, state,
        norm_paths, norm_search, only_commented,
    )
    v1_open = sum(1 for c in plan.comments_v1 if c.resolution == "open")
    v1_res = sum(1 for c in plan.comments_v1 if c.resolution == "resolved")
    v2_open = sum(1 for c in plan.comments_v2 if c.resolution == "open")
    v2_res = sum(1 for c in plan.comments_v2 if c.resolution == "resolved")
    v2_orph = sum(1 for c in plan.comments_v2 if c.state == "orphan")
    totals = (
        f"V1 comments: {len(plan.comments_v1)} ({v1_open} open, {v1_res} resolved). "
        f"V2 comments: {len(plan.comments_v2)} ({v2_open} open, {v2_res} resolved; {v2_orph} orphan)."
    )
    trans_line = _transition_summary_line(plan.transitions)
    files_line = f"Revision-changed files: {len(plan.visible_files)} of {len(plan.placed_files)} shown."

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Skein revision interdiff</title><style>{skein.STYLE}{review_view.EXTRA_STYLE}</style></head>
<body><a class="skip" href="#files">Skip to changed files</a><main><h1>Skein revision interdiff</h1>
<p class="identity">V1 head: <code>{html.escape(v1_head_text)}</code><br>V2 head: <code>{html.escape(v2_head_text)}</code><br>{html.escape(base_line)}</p>
<div class="summary"><p>{html.escape(showing)}<br>{html.escape(totals)}<br>{html.escape(trans_line)}<br>{html.escape(files_line)}</p>
<p>This static view is derived read-only from the offline packets; no network or JavaScript is used.</p></div>
<nav id="files" aria-label="Changed files"><ol>{"".join(navigation)}</ol></nav>
{comments_nav_html}{buckets_html}{files_body}<footer>Review Skein interdiff.
Bundle hashes bind bytes, not people. Comments live in comments.json.</footer></main></body></html>
'''


def _render_json(plan: _InterdiffPlan) -> str:
    payload = {
        "first": {
            "base": plan.meta_v1["base"]["commit"],
            "base_ref": plan.meta_v1["base"]["ref"],
            "head": plan.meta_v1["head"]["commit"],
            "head_ref": plan.meta_v1["head"]["ref"],
            "total_comments": len(plan.comments_v1),
        },
        "second": {
            "base": plan.meta_v2["base"]["commit"],
            "base_ref": plan.meta_v2["base"]["ref"],
            "head": plan.meta_v2["head"]["commit"],
            "head_ref": plan.meta_v2["head"]["ref"],
            "total_comments": len(plan.comments_v2),
        },
        "same_base": plan.meta_v1["base"]["commit"] == plan.meta_v2["base"]["commit"],
        "transitions": plan.transitions,
        "comments": [
            {"origin": entry.origin, "transition": entry.transition,
             "comment": entry.comment.to_dict()}
            for entry in plan.selected_entries
        ],
        "changed_files": [
            {
                "status": placed.change.status,
                "old_path": placed.change.old_path,
                "new_path": placed.change.new_path,
                "display_path": placed.change.display_path,
                "old_lines": len(placed.old_lines),
                "new_lines": len(placed.new_lines),
            }
            for placed in plan.visible_files
        ],
        "placements": plan.placements,
        "counts": {
            "all_entries": len(plan.all_entries),
            "selected_entries": len(plan.selected_entries),
            "changed_files_total": len(plan.placed_files),
            "changed_files_shown": len(plan.visible_files),
        },
    }
    return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def render_interdiff(
    first_packet: Path,
    second_packet: Path,
    *,
    output_format: str = "text",
    resolution: str = "all",
    state: str = "all",
    context: int = 3,
    max_file_bytes: int = skein.DEFAULT_MAX_FILE_BYTES,
    paths: Sequence[str] | None = None,
    search: str = "",
    only_commented: bool = False,
) -> str:
    """Verify two exported Skein packets and render the head_v1 -> head_v2 interdiff."""
    norm_paths, norm_search = _validate_interdiff_options(
        output_format, resolution, state, context, max_file_bytes,
        paths=paths, search=search, only_commented=only_commented,
    )
    plan = _build_plan(
        first_packet,
        second_packet,
        resolution=resolution,
        state=state,
        max_file_bytes=max_file_bytes,
        norm_paths=norm_paths,
        norm_search=norm_search,
        only_commented=only_commented,
    )
    if output_format == "json":
        return _render_json(plan)
    if output_format == "text":
        return _render_text(
            plan, resolution, state, context, norm_paths, norm_search, only_commented,
        )
    return _render_html(
        plan, resolution, state, context, norm_paths, norm_search, only_commented,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="interdiff.py",
        description="Render a read-only head-to-head interdiff and comment transitions between two Skein packets.",
    )
    parser.add_argument("first", type=Path, help="Path to the earlier Skein packet directory (V1)")
    parser.add_argument("second", type=Path, help="Path to the revised Skein packet directory (V2)")
    parser.add_argument("--format", dest="output_format", choices=VALID_FORMATS, default="text",
                        help="Output format (default: text)")
    parser.add_argument("--resolution", choices=review_view.VALID_RESOLUTIONS, default="all",
                        help="Filter comments by resolution status (default: all)")
    parser.add_argument("--state", choices=review_view.VALID_STATES, default="all",
                        help="Filter comments by anchor state (default: all)")
    parser.add_argument("--path", dest="paths", action="append", default=None,
                        help="Filter diff and comments to an exact file or directory prefix (repeatable)")
    parser.add_argument("--search", default="",
                        help="Filter comments by case-insensitive substring")
    parser.add_argument("--only-commented", action="store_true",
                        help="Show only revision-changed files that have matching inline comments")
    parser.add_argument("--context", type=int, default=3,
                        help="Context lines around changes and comments, or -1 for full files (default: 3)")
    parser.add_argument("--max-file-bytes", type=int, default=skein.DEFAULT_MAX_FILE_BYTES,
                        help=f"Maximum blob size in bytes (default: {skein.DEFAULT_MAX_FILE_BYTES})")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        output = render_interdiff(
            args.first,
            args.second,
            output_format=args.output_format,
            resolution=args.resolution,
            state=args.state,
            context=args.context,
            max_file_bytes=args.max_file_bytes,
            paths=args.paths,
            search=args.search,
            only_commented=args.only_commented,
        )
    except (OSError, UnicodeError, skein.SkeinError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
