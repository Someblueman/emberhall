"""Read-only annotated diff-and-comment renderer for exported Review Skein packets."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import html
from pathlib import Path
import sys
import tempfile
from typing import Any, Sequence

import comments_view
import skein


VALID_FORMATS = ("text", "html")
VALID_RESOLUTIONS = ("all", "open", "resolved")
VALID_STATES = ("all", "anchored", "orphan")

EXTRA_STYLE = """
.summary { border-left: 3px solid var(--border); padding: .2rem .8rem; margin: 1rem 0; }
.orphans { border: 1px solid var(--border); padding: .75rem 1rem; margin: 1.5rem 0; }
.comment-card { border-top: 1px solid var(--border); padding-top: .75rem; margin-top: .75rem; }
.comment-card:first-of-type { border-top: 0; padding-top: 0; margin-top: 0; }
.comment-card h3 { font-size: 1rem; margin: 0 0 .35rem 0; overflow-wrap: anywhere; }
.comment-meta { text-align: left; font-weight: normal; padding: .45rem .6rem;
  background: var(--bg); color: var(--fg); overflow-wrap: anywhere; }
.comment-cell { padding: .45rem .6rem; background: var(--bg); }
.comment-body { margin: .25rem 0 0 0; white-space: pre-wrap; overflow-wrap: anywhere;
  font: 13px/1.45 ui-monospace, SFMono-Regular, Consolas, monospace; }
.comment-extra { margin: .2rem 0 0 0; color: var(--muted); font-size: .9rem;
  overflow-wrap: anywhere; }
"""


@dataclass(frozen=True)
class _DiffRow:
    old_number: int | None
    new_number: int | None
    old_text: str
    new_text: str
    kind: str


@dataclass(frozen=True)
class _PlacedFile:
    change: skein.Change
    old_lines: list[str]
    new_lines: list[str]
    rows: list[_DiffRow]
    row_comments: list[tuple[list[skein.Comment], list[skein.Comment]]]


def _visible(value: str) -> str:
    return comments_view._visible(value)


def _visible_multiline(value: str) -> str:
    return "\n".join(_visible(line) for line in value.split("\n"))


def _validate_options(
    output_format: str, resolution: str, state: str, context: int, max_file_bytes: int,
) -> None:
    if output_format not in VALID_FORMATS:
        raise ValueError(f"output_format must be one of {VALID_FORMATS}: {output_format!r}")
    if resolution not in VALID_RESOLUTIONS:
        raise ValueError(f"resolution must be one of {VALID_RESOLUTIONS}: {resolution!r}")
    if state not in VALID_STATES:
        raise ValueError(f"state must be one of {VALID_STATES}: {state!r}")
    if type(context) is not int or context < -1:
        raise ValueError(f"context must be an integer >= -1: {context!r}")
    if type(max_file_bytes) is not int or max_file_bytes < 1:
        raise ValueError(f"max_file_bytes must be a positive integer: {max_file_bytes!r}")


def _require_regular_file(path: Path, label: str, max_bytes: int | None = None) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise skein.SkeinError(f"{label} is missing or is not a regular file: {path.name}")
    if max_bytes is not None:
        size = path.stat().st_size
        if size > max_bytes:
            raise skein.SkeinError(f"{label} exceeds {max_bytes} bytes: {path.name}")
    return path.read_bytes() if max_bytes is not None else b""


def _build_rows(old: list[str], new: list[str]) -> list[_DiffRow]:
    import difflib

    rows: list[_DiffRow] = []
    matcher = difflib.SequenceMatcher(a=old, b=new, autojunk=False)
    for operation, a1, a2, b1, b2 in matcher.get_opcodes():
        if operation == "equal":
            for offset in range(a2 - a1):
                rows.append(_DiffRow(
                    a1 + offset + 1, b1 + offset + 1,
                    old[a1 + offset], new[b1 + offset], "equal",
                ))
        elif operation == "replace":
            width = max(a2 - a1, b2 - b1)
            for offset in range(width):
                ai, bi = a1 + offset, b1 + offset
                rows.append(_DiffRow(
                    ai + 1 if ai < a2 else None,
                    bi + 1 if bi < b2 else None,
                    old[ai] if ai < a2 else "",
                    new[bi] if bi < b2 else "",
                    "replace",
                ))
        elif operation == "delete":
            for ai in range(a1, a2):
                rows.append(_DiffRow(ai + 1, None, old[ai], "", "delete"))
        elif operation == "insert":
            for bi in range(b1, b2):
                rows.append(_DiffRow(None, bi + 1, "", new[bi], "insert"))
    if old or new:
        old_final = getattr(old, "final_newline", True)
        new_final = getattr(new, "final_newline", True)
        if not old_final or not new_final:
            rows.append(_DiffRow(
                None, None,
                "" if old_final else "\\ No newline at end of file",
                "" if new_final else "\\ No newline at end of file",
                "meta",
            ))
    return rows


def _load_verified_packet(
    packet: Path, max_file_bytes: int,
) -> tuple[dict[str, Any], list[skein.Comment], list[tuple[skein.Change, list[str], list[str], list[_DiffRow]]]]:
    packet = packet.expanduser()
    if packet.is_symlink() or not packet.is_dir():
        raise skein.SkeinError(f"packet path is not a regular directory: {packet}")
    resolved = packet.resolve()
    metadata = skein._load_packet(resolved)
    anchors = skein._load_anchors(resolved)

    comments_bytes = _require_regular_file(
        resolved / "comments.json", "packet comments", max_bytes=skein.JSON_LIMIT,
    )
    try:
        comments_text = comments_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise skein.SkeinError(f"packet comments are not valid UTF-8: {exc}") from exc
    comments = skein.loads_comments(comments_text)

    bundle = resolved / "changes.bundle"
    _require_regular_file(bundle, "packet bundle")

    base_commit = metadata["base"]["commit"]
    head_commit = metadata["head"]["commit"]

    rendered: list[tuple[skein.Change, list[str], list[str], list[_DiffRow]]] = []
    file_records: list[dict[str, Any]] = []
    expected_anchors: list[skein.Anchor] = []
    with tempfile.TemporaryDirectory(prefix="skein-view-") as temporary:
        root = Path(temporary)
        clone = root / "clone"
        skein._git(root, "clone", "--quiet", "--no-checkout", str(bundle), str(clone))
        skein._git(clone, "bundle", "verify", str(bundle))
        for commit in (base_commit, head_commit):
            skein._git(clone, "cat-file", "-e", f"{commit}^{{commit}}")
        old_tree = skein._tree(clone, base_commit)
        new_tree = skein._tree(clone, head_commit)
        changes = skein._changes(clone, base_commit, head_commit)
        reader = skein.BlobReader(clone, max_file_bytes)
        for change in changes:
            old_entry = old_tree.get(change.old_path) if change.old_path else None
            new_entry = new_tree.get(change.new_path) if change.new_path else None
            old = reader.read(old_entry)
            new = reader.read(new_entry)
            for commit, path, side, lines in (
                (base_commit, change.old_path, "old", old),
                (head_commit, change.new_path, "new", new),
            ):
                if path is not None:
                    expected_anchors.extend(
                        skein.Anchor(commit, path, side, number, text)
                        for number, text in enumerate(lines, 1)
                    )
            rows = _build_rows(old, new)
            rendered.append((change, old, new, rows))
            file_records.append({
                "status": change.status,
                "old_path": change.old_path,
                "new_path": change.new_path,
                "old_lines": len(old),
                "new_lines": len(new),
            })

    if metadata["files"] != file_records:
        raise skein.SkeinError("packet.json file inventory does not match changes.bundle")
    if len(anchors) != len(expected_anchors) or set(anchors) != set(expected_anchors):
        raise skein.SkeinError("anchors.json does not match changes.bundle line anchors")
    return metadata, comments, rendered


def _place_comments(
    metadata: dict[str, Any],
    selected: Sequence[skein.Comment],
    rendered: list[tuple[skein.Change, list[str], list[str], list[_DiffRow]]],
) -> tuple[list[_PlacedFile], list[tuple[skein.Comment, str]]]:
    base_commit = metadata["base"]["commit"]
    head_commit = metadata["head"]["commit"]
    by_target: dict[skein.Anchor, list[skein.Comment]] = {}
    orphans: list[tuple[skein.Comment, str]] = []

    for comment in selected:
        if comment.state == "orphan":
            orphans.append((comment, comment.orphan_reason or "orphaned comment"))
            continue
        by_target.setdefault(comment.anchor, []).append(comment)

    placed_keys: set[skein.Anchor] = set()
    placed_files: list[_PlacedFile] = []

    for change, old_lines, new_lines, rows in rendered:
        row_comments: list[tuple[list[skein.Comment], list[skein.Comment]]] = []
        for row in rows:
            old_list: list[skein.Comment] = []
            new_list: list[skein.Comment] = []
            if change.old_path is not None and row.old_number is not None:
                old_key = skein.Anchor(base_commit, change.old_path, "old",
                                       row.old_number, row.old_text)
                if old_key in by_target:
                    old_list = by_target[old_key]
                    placed_keys.add(old_key)
            if change.new_path is not None and row.new_number is not None:
                new_key = skein.Anchor(head_commit, change.new_path, "new",
                                       row.new_number, row.new_text)
                if new_key in by_target:
                    new_list = by_target[new_key]
                    placed_keys.add(new_key)
            row_comments.append((old_list, new_list))
        placed_files.append(_PlacedFile(change, old_lines, new_lines, rows, row_comments))

    # Compare raw text before display escaping; a coordinate alone is not an anchor match.
    for key, comments_at_key in by_target.items():
        if key not in placed_keys:
            for comment in comments_at_key:
                orphans.append((comment, "anchor target or text does not match verified packet diffs"))

    order = {comment.identifier: index for index, comment in enumerate(selected)}
    orphans.sort(key=lambda item: order[item[0].identifier])
    return placed_files, orphans


def _visible_ranges(
    rows: Sequence[_DiffRow],
    row_comments: Sequence[tuple[list[skein.Comment], list[skein.Comment]]],
    context: int,
) -> list[tuple[int, int]]:
    if not rows:
        return []
    if context == -1:
        return [(0, len(rows) - 1)]
    interesting = [
        index
        for index, (row, (old_c, new_c)) in enumerate(zip(rows, row_comments))
        if row.kind != "equal" or old_c or new_c
    ]
    if not interesting:
        return []
    ranges: list[tuple[int, int]] = []
    last = len(rows) - 1
    for index in interesting:
        start = max(0, index - context)
        end = min(last, index + context)
        if ranges and start <= ranges[-1][1] + 1:
            ranges[-1] = (ranges[-1][0], max(ranges[-1][1], end))
        else:
            ranges.append((start, end))
    return ranges


def _hunk_header(rows: Sequence[_DiffRow], start: int, end: int) -> str:
    old_nums = [r.old_number for r in rows[start : end + 1] if r.old_number is not None]
    new_nums = [r.new_number for r in rows[start : end + 1] if r.new_number is not None]
    old_part = f"{old_nums[0]},{len(old_nums)}" if old_nums else "0,0"
    new_part = f"{new_nums[0]},{len(new_nums)}" if new_nums else "0,0"
    return f"@@ -{old_part} +{new_part} @@"


def _format_text_inline_comment(comment: skein.Comment) -> list[str]:
    lines = [
        f"    [{_visible(comment.identifier)} | {comment.resolution} | "
        f"{comment.state} | {comment.anchor.side} line {comment.anchor.line}]"
    ]
    if comment.rebased_from is not None:
        lines.append(f"      Rebased from: {_visible(comments_view._anchor_text(comment.rebased_from))}")
    for body_line in _visible_multiline(comment.body).split("\n"):
        lines.append(f"      {body_line}")
    return lines


def _render_text_hunk(
    rows: Sequence[_DiffRow],
    row_comments: Sequence[tuple[list[skein.Comment], list[skein.Comment]]],
    start: int,
    end: int,
) -> list[str]:
    out = [_hunk_header(rows, start, end)]
    index = start
    while index <= end:
        row = rows[index]
        old_c, new_c = row_comments[index]
        if row.kind == "equal":
            out.append(f" {row.old_number:>5} {row.new_number:>5}   {_visible(row.new_text)}")
            for comment in (*old_c, *new_c):
                out.extend(_format_text_inline_comment(comment))
            index += 1
            continue
        if row.kind == "meta":
            note = row.old_text or row.new_text
            out.append(f"       note  {_visible(note)}")
            index += 1
            continue
        # Emit contiguous non-equal lines as '-' old block then '+' new block
        # so multi-line replacements stay grouped cleanly while keeping line comments paired.
        run_end = index
        while run_end <= end and rows[run_end].kind in {"delete", "insert", "replace"}:
            run_end += 1
        for pos in range(index, run_end):
            r = rows[pos]
            r_old_c, _ = row_comments[pos]
            if r.old_number is not None:
                out.append(f"-{r.old_number:>5}       - {_visible(r.old_text)}")
                for comment in r_old_c:
                    out.extend(_format_text_inline_comment(comment))
        for pos in range(index, run_end):
            r = rows[pos]
            _, r_new_c = row_comments[pos]
            if r.new_number is not None:
                out.append(f"+      {r.new_number:>5} + {_visible(r.new_text)}")
                for comment in r_new_c:
                    out.extend(_format_text_inline_comment(comment))
        index = run_end
    return out


def _render_text(
    metadata: dict[str, Any],
    all_comments: Sequence[skein.Comment],
    selected: Sequence[skein.Comment],
    placed_files: Sequence[_PlacedFile],
    orphans: Sequence[tuple[skein.Comment, str]],
    resolution: str,
    state: str,
    context: int,
) -> str:
    open_count = sum(1 for c in all_comments if c.resolution == "open")
    resolved_count = sum(1 for c in all_comments if c.resolution == "resolved")
    orphan_count = sum(1 for c in all_comments if c.state == "orphan")

    lines = [
        "Skein review",
        f'Base: {_visible(metadata["base"]["ref"])} ({metadata["base"]["commit"]})',
        f'Head: {_visible(metadata["head"]["ref"])} ({metadata["head"]["commit"]})',
        f"Showing {len(selected)} of {len(all_comments)} comments. Filters: resolution={resolution}, state={state}.",
        f"All comments: {open_count} open, {resolved_count} resolved; {orphan_count} orphan.",
        "This view is derived read-only from the offline packet; Git hashes bind bytes, not people.",
    ]

    if orphans:
        lines.append("")
        lines.append(f"Orphaned and unplaced comments ({len(orphans)}):")
        for comment, reason in orphans:
            lines.append(f"- {_visible(comment.identifier)} | {comment.resolution} | {comment.state}")
            lines.append(f"  Anchor: {_visible(comments_view._anchor_text(comment.anchor))}")
            lines.append(f"  Reason: {_visible(reason)}")
            if comment.rebased_from is not None:
                lines.append(f"  Rebased from: {_visible(comments_view._anchor_text(comment.rebased_from))}")
            lines.append("  Body:")
            for body_line in _visible_multiline(comment.body).split("\n"):
                lines.append(f"    {body_line}")

    if not placed_files:
        lines.append("")
        lines.append("The two commits have identical file trees.")
        return "\n".join(lines) + "\n"

    for placed in placed_files:
        change = placed.change
        lines.append("")
        lines.append(
            f"=== {_visible(change.status)}: {_visible(change.display_path)} "
            f"({len(placed.old_lines)} old / {len(placed.new_lines)} new lines) ==="
        )
        ranges = _visible_ranges(placed.rows, placed.row_comments, context)
        if not ranges:
            lines.append("(no diff lines or matching inline comments in current view)")
            continue
        for start, end in ranges:
            lines.extend(_render_text_hunk(placed.rows, placed.row_comments, start, end))
    return "\n".join(lines) + "\n"


def _render_html_comment_details(comment: skein.Comment, extra_reason: str | None = None) -> str:
    parts: list[str] = []
    if extra_reason is not None:
        parts.append(f'<p class="comment-extra">Reason: {html.escape(_visible(extra_reason))}</p>')
    if comment.rebased_from is not None:
        anchor_str = _visible(comments_view._anchor_text(comment.rebased_from))
        parts.append(f'<p class="comment-extra">Rebased from: <code>{html.escape(anchor_str)}</code></p>')
    body_text = html.escape(_visible_multiline(comment.body))
    parts.append(f'<pre class="comment-body">{body_text}</pre>')
    return "".join(parts)


def _render_html_file_rows(placed: _PlacedFile, context: int, counter: list[int]) -> str:
    ranges = _visible_ranges(placed.rows, placed.row_comments, context)
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
            for comment in (*old_c, *new_c):
                counter[0] += 1
                dom_id = f"comment-{counter[0]}"
                meta = (
                    f'<span class="sr">Comment.</span> '
                    f'<strong>{html.escape(_visible(comment.identifier))}</strong> '
                    f'({html.escape(comment.resolution)}, {html.escape(comment.state)}, '
                    f'{html.escape(comment.anchor.side)} line {comment.anchor.line})'
                )
                details = _render_html_comment_details(comment)
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
    metadata: dict[str, Any],
    all_comments: Sequence[skein.Comment],
    selected: Sequence[skein.Comment],
    placed_files: Sequence[_PlacedFile],
    orphans: Sequence[tuple[skein.Comment, str]],
    resolution: str,
    state: str,
    context: int,
) -> str:
    open_count = sum(1 for c in all_comments if c.resolution == "open")
    resolved_count = sum(1 for c in all_comments if c.resolution == "resolved")
    orphan_count = sum(1 for c in all_comments if c.state == "orphan")

    counter = [0]
    navigation: list[str] = []
    orphan_html = ""
    if orphans:
        navigation.append(
            f'<li><a href="#orphans">Orphaned and unplaced comments ({len(orphans)})</a></li>'
        )
        cards: list[str] = []
        for comment, reason in orphans:
            counter[0] += 1
            dom_id = f"comment-{counter[0]}"
            title = (
                f"{_visible(comment.identifier)} — {comment.resolution}, {comment.state}"
            )
            anchor_text = _visible(comments_view._anchor_text(comment.anchor))
            cards.append(
                f'<article class="comment-card" id="{dom_id}">'
                f'<h3 id="{dom_id}-title">{html.escape(title)}</h3>'
                f'<p class="comment-extra">Anchor: <code>{html.escape(anchor_text)}</code></p>'
                f'{_render_html_comment_details(comment, extra_reason=reason)}'
                '</article>'
            )
        orphan_html = (
            f'<section class="orphans" id="orphans" aria-labelledby="orphans-title">'
            f'<h2 id="orphans-title">Orphaned and unplaced comments ({len(orphans)})</h2>'
            f'{"".join(cards)}</section>\n'
        )

    sections: list[str] = []
    for index, placed in enumerate(placed_files, 1):
        change = placed.change
        title = f"{_visible(change.status)}: {_visible(change.display_path)}"
        navigation.append(f'<li><a href="#file-{index}">{html.escape(title)}</a></li>')
        tbody = _render_html_file_rows(placed, context, counter)
        sections.append(
            f'<section id="file-{index}" aria-labelledby="file-{index}-title">'
            f'<h2 id="file-{index}-title">{html.escape(title)}</h2>\n'
            f'<div class="scroll"><table><caption>Old line and new line; '
            f'{len(placed.old_lines)} old / {len(placed.new_lines)} new</caption>\n'
            '<thead><tr><th scope="col">Old</th><th scope="col">New</th>'
            '<th scope="col">Base text</th><th scope="col">Head text</th></tr></thead>\n'
            f'<tbody>{tbody}</tbody></table></div></section>\n'
        )

    if not sections and not orphan_html:
        navigation.append("<li>No textual changes or comments in this view.</li>")
    files_body = "".join(sections) or "<p>The two commits have identical file trees.</p>"

    base_text = _visible(f'{metadata["base"]["ref"]} ({metadata["base"]["commit"]})')
    head_text = _visible(f'{metadata["head"]["ref"]} ({metadata["head"]["commit"]})')
    showing = f"Showing {len(selected)} of {len(all_comments)} comments. Filters: resolution={resolution}, state={state}."
    totals = f"All comments: {open_count} open, {resolved_count} resolved; {orphan_count} orphan."

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Skein review</title><style>{skein.STYLE}{EXTRA_STYLE}</style></head>
<body><a class="skip" href="#files">Skip to changed files</a><main><h1>Skein review</h1>
<p class="identity">Base: <code>{html.escape(base_text)}</code><br>Head: <code>{html.escape(head_text)}</code></p>
<div class="summary"><p>{html.escape(showing)}<br>{html.escape(totals)}</p>
<p>This static view is derived read-only from the offline packet; no network or JavaScript is used.</p></div>
<nav id="files" aria-label="Changed files"><ol>{''.join(navigation)}</ol></nav>
{orphan_html}{files_body}<footer>Review Skein packet format {html.escape(str(metadata.get("version", skein.VERSION)))}.
Bundle hashes bind bytes, not people. Comments live in comments.json.</footer></main></body></html>
'''


def render_packet(
    packet: Path,
    *,
    output_format: str = "text",
    resolution: str = "all",
    state: str = "all",
    context: int = 3,
    max_file_bytes: int = skein.DEFAULT_MAX_FILE_BYTES,
) -> str:
    """Verify an exported Skein packet and render diffs together with comments."""
    _validate_options(output_format, resolution, state, context, max_file_bytes)
    metadata, all_comments, rendered = _load_verified_packet(packet, max_file_bytes)
    selected = [
        comment
        for comment in all_comments
        if (resolution == "all" or comment.resolution == resolution)
        and (state == "all" or comment.state == state)
    ]
    placed_files, orphans = _place_comments(metadata, selected, rendered)
    if output_format == "text":
        return _render_text(
            metadata, all_comments, selected, placed_files, orphans,
            resolution, state, context,
        )
    return _render_html(
        metadata, all_comments, selected, placed_files, orphans,
        resolution, state, context,
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="review_view.py",
        description="Render a read-only diff and anchored comment view from an exported Skein packet.",
    )
    parser.add_argument("packet", type=Path, help="Path to the exported Skein packet directory")
    parser.add_argument("--format", dest="output_format", choices=VALID_FORMATS, default="text",
                        help="Output format (default: text)")
    parser.add_argument("--resolution", choices=VALID_RESOLUTIONS, default="all",
                        help="Filter comments by resolution status (default: all)")
    parser.add_argument("--state", choices=VALID_STATES, default="all",
                        help="Filter comments by anchor state (default: all)")
    parser.add_argument("--context", type=int, default=3,
                        help="Context lines around changes and comments, or -1 for full files (default: 3)")
    parser.add_argument("--max-file-bytes", type=int, default=skein.DEFAULT_MAX_FILE_BYTES,
                        help=f"Maximum blob size in bytes (default: {skein.DEFAULT_MAX_FILE_BYTES})")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        output = render_packet(
            args.packet,
            output_format=args.output_format,
            resolution=args.resolution,
            state=args.state,
            context=args.context,
            max_file_bytes=args.max_file_bytes,
        )
    except (OSError, UnicodeError, skein.SkeinError, ValueError) as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
