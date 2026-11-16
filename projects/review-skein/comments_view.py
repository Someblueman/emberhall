"""Read strict Skein comments as text or a standalone, offline HTML snapshot."""
from __future__ import annotations

import argparse
import html
from pathlib import Path
import sys
from typing import Sequence
import unicodedata

import skein


def _normalize_paths(paths: Sequence[str] | None) -> tuple[str, ...]:
    if paths is None:
        return ()
    if isinstance(paths, (str, bytes)):
        raise ValueError("paths must be a sequence of path strings")
    normalized: list[str] = []
    for raw in paths:
        if not isinstance(raw, str) or not raw.strip():
            raise ValueError("each path filter must be a non-empty string")
        cleaned = raw.strip()
        while cleaned.startswith("./"):
            cleaned = cleaned[2:]
        if not cleaned or not cleaned.rstrip("/"):
            raise ValueError(f"invalid path filter: {raw!r}")
        normalized.append(cleaned)
    return tuple(normalized)


def _path_matches(candidate: str, pattern: str) -> bool:
    prefix = pattern.rstrip("/")
    return candidate == prefix or candidate.startswith(prefix + "/")


def _matches_search(comment: skein.Comment, query: str) -> bool:
    if not query:
        return True
    needle = query.casefold()
    fields = [
        comment.identifier,
        comment.body,
        comment.anchor.path,
        comment.anchor.text,
        comment.orphan_reason or "",
    ]
    if comment.rebased_from is not None:
        fields.extend([comment.rebased_from.path, comment.rebased_from.text])
    return any(needle in value.casefold() for value in fields)


def _visible(value: str) -> str:
    """Keep multiline prose while displaying control and direction markers literally."""
    return "".join(
        (f"\\u{ord(character):04x}" if ord(character) <= 0xFFFF
         else f"\\U{ord(character):08x}")
        if character not in "\n\t" and unicodedata.category(character) in {"Cc", "Cf"}
        else character
        for character in value
    )


def _anchor_text(anchor: skein.Anchor) -> str:
    return (f"{_visible(anchor.path)} | {anchor.side} line {anchor.line}\n"
            f"Commit: {anchor.commit}\n{_visible(anchor.text)}")


def render_comments(
    comments: list[skein.Comment], *, output_format: str = "text",
    resolution: str = "all", state: str = "all",
    paths: Sequence[str] | None = None, search: str = "",
) -> str:
    """Render a snapshot; filters hide rows without changing the underlying comments."""
    if output_format not in {"text", "html"}:
        raise ValueError("format must be text or html")
    if resolution not in {"all", "open", "resolved"} or state not in {"all", "anchored", "orphan"}:
        raise ValueError("unsupported comment filter")
    if not isinstance(search, str):
        raise ValueError("search must be a string")
    path_patterns = _normalize_paths(paths)
    search_query = search.strip()
    selected = [
        comment for comment in comments
        if (resolution == "all" or comment.resolution == resolution)
        and (state == "all" or comment.state == state)
        and (not path_patterns or any(_path_matches(comment.anchor.path, p) for p in path_patterns))
        and _matches_search(comment, search_query)
    ]
    filter_parts = [f"resolution={resolution}", f"state={state}"]
    if path_patterns:
        filter_parts.append(f"path={', '.join(path_patterns)}")
    if search_query:
        filter_parts.append(f"search={search_query!r}")
    summary = (f"Showing {len(selected)} of {len(comments)} comments. "
               f"Filters: {', '.join(filter_parts)}.")
    totals = (f"All comments: {sum(c.resolution == 'open' for c in comments)} open, "
              f"{sum(c.resolution == 'resolved' for c in comments)} resolved; "
              f"{sum(c.state == 'orphan' for c in comments)} orphan.")
    if output_format == "text":
        parts = ["Skein comments", _visible(summary), totals]
        for comment in selected:
            parts.extend([
                "", f"{comment.identifier} | {comment.resolution} | {comment.state}",
                _anchor_text(comment.anchor), "Body:", _visible(comment.body),
            ])
            if comment.orphan_reason is not None:
                parts.append(f"Orphan reason: {_visible(comment.orphan_reason)}")
            if comment.rebased_from is not None:
                parts.extend(["Rebased from:", _anchor_text(comment.rebased_from)])
        if not selected:
            parts.extend(["", "No comments match these filters."])
        return "\n".join(parts) + "\n"

    def escaped(value: str) -> str:
        return html.escape(_visible(value))

    navigation = "".join(
        f'<li><a href="#note-{comment.identifier}">{comment.identifier}: '
        f'{comment.resolution}, {comment.state}</a></li>' for comment in selected
    )
    articles = []
    for comment in selected:
        provenance = ""
        if comment.orphan_reason is not None:
            provenance += f'<p>Orphan reason: {escaped(comment.orphan_reason)}</p>'
        if comment.rebased_from is not None:
            provenance += (f'<h3>Rebased from</h3><pre>'
                           f'{escaped(_anchor_text(comment.rebased_from))}</pre>')
        articles.append(
            f'<article id="note-{comment.identifier}" aria-labelledby="title-{comment.identifier}">'
            f'<h2 id="title-{comment.identifier}">{comment.identifier}</h2>'
            f'<p>Status: {comment.resolution}. Anchor: {comment.state}.</p>'
            f'<h3>Anchor</h3><pre>{escaped(_anchor_text(comment.anchor))}</pre>'
            f'<h3>Comment</h3><pre>{escaped(comment.body)}</pre>{provenance}</article>'
        )
    body = "\n".join(articles) or "<p>No comments match these filters.</p>"
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'">
<title>Skein comments</title><style>
body {{ margin: auto; max-width: 64rem; padding: 1rem; color: #20252b; background: #fff; }}
body, pre {{ font: 1rem/1.6 system-ui, sans-serif; }}
pre, a, h2 {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
article {{ border-top: 2px solid #596774; padding-block: 1rem; }}
pre {{ border-left: 3px solid #596774; padding: .5rem 1rem; }}
a {{ color: #153f8c; }}
a:focus-visible, article:target {{ outline: 3px solid #964400; outline-offset: 3px; }}
</style></head><body><a href="#comments">Skip to comments</a><main>
<h1>Skein comments</h1><p>{escaped(summary)}</p><p>{totals}</p>
<p>Read-only snapshot of comments.json. Regenerate after editing or resolving comments.
This page neither verifies the Git bundle nor authenticates a reviewer.</p>
<nav id="comments" aria-label="Comments"><ol>{navigation}</ol></nav>
{body}
</main></body></html>
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("comments", type=Path, help="the packet's version-2 comments.json")
    parser.add_argument("--format", choices=("text", "html"), default="text", dest="output_format")
    parser.add_argument("--resolution", choices=("all", "open", "resolved"), default="all")
    parser.add_argument("--state", choices=("all", "anchored", "orphan"), default="all")
    parser.add_argument("--path", action="append", dest="paths", default=None,
                        help="filter comments by exact file path or directory prefix (repeatable)")
    parser.add_argument("--search", default="",
                        help="case-insensitive substring search across ID, body, path, line text, orphan reason, or rebase origin")
    arguments = parser.parse_args(argv)
    try:
        path = arguments.comments
        if path.is_symlink() or not path.is_file():
            raise skein.SkeinError("comments must be a regular file, not a symlink")
        with path.open("rb") as stream:
            data = stream.read(skein.JSON_LIMIT + 1)
        if len(data) > skein.JSON_LIMIT:
            raise skein.SkeinError(f"comments exceed {skein.JSON_LIMIT} bytes")
        comments = skein.loads_comments(data.decode("utf-8"))
        result = render_comments(comments, output_format=arguments.output_format,
                                 resolution=arguments.resolution, state=arguments.state,
                                 paths=arguments.paths, search=arguments.search)
        sys.stdout.write(result)
        sys.stdout.flush()
    except BrokenPipeError:
        return 1
    except (OSError, UnicodeError, skein.SkeinError) as exc:
        print(f"comments-view: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"comments-view: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
