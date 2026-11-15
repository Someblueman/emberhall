"""Generate an offline comment editor and validate its downloaded edits."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
from pathlib import Path
import sys

import skein


EDIT_FORMAT = "skein-comment-edits"
EDIT_VERSION = 1


def _read(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise skein.SkeinError(f"expected a regular file, not a symlink: {path.name}")
    with path.open("rb") as stream:
        data = stream.read(skein.JSON_LIMIT + 1)
    if len(data) > skein.JSON_LIMIT:
        raise skein.SkeinError(f"input exceeds {skein.JSON_LIMIT} bytes: {path.name}")
    return data


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _comments(text: str) -> list[skein.Comment]:
    try:
        return skein.loads_comments(text)
    except (TypeError, RecursionError) as exc:
        raise skein.SkeinError("malformed comment data") from exc


def render_editor(data: bytes) -> str:
    """Validate all comments before embedding inert data in a deterministic page."""
    if len(data) > skein.JSON_LIMIT:
        raise skein.SkeinError(f"input exceeds {skein.JSON_LIMIT} bytes")
    comments = _comments(data.decode("utf-8"))
    envelope = {
        "format": EDIT_FORMAT, "version": EDIT_VERSION, "base_sha256": _digest(data),
        "document": json.loads(skein.dumps_comments(comments)),
    }
    return _render(envelope)


def _render(envelope: dict, anchors: list[skein.Anchor] | None = None) -> str:
    payload = _inert_json(envelope)
    addition = ""
    if anchors is not None:
        addition = ('<script type="application/json" id="anchor-data">'
                    + _inert_json([anchor.to_dict() for anchor in anchors]) + "</script>")
    script = Path(__file__).with_suffix(".js").read_text(encoding="utf-8")
    digest = base64.b64encode(hashlib.sha256(script.encode("utf-8")).digest()).decode("ascii")
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{digest}'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>Edit Skein comments</title><style>
body {{ max-width: 64rem; margin: auto; padding: 1rem; color: #20252b; background: #fff; font: 1rem/1.6 system-ui,sans-serif; }}
article {{ border-top: 2px solid #596774; padding-block: 1rem; }}
pre, h2, a {{ white-space: pre-wrap; overflow-wrap: anywhere; }}
pre {{ border-left: 3px solid #596774; padding: .5rem; }}
label {{ display: block; font-weight: bold; margin-top: .8rem; }}
textarea {{ box-sizing: border-box; width: 100%; min-height: 8rem; }}
input, textarea, select, button {{ max-width: 100%; font: inherit; padding: .5rem; }}
button {{ margin-block: .75rem; }}
:focus-visible {{ outline: 3px solid #964400; outline-offset: 3px; }}
</style></head><body><a href="#comments">Skip to comments</a><main>
<h1>Edit Skein comments</h1>
<p>Edit existing comment bodies and open/resolved status. Anchors and orphan history stay fixed.
A packet-bound compose page also lets you select a rendered line and add a new comment below.
This local page does not write your packet. Download edits, then apply them with the CLI.
Keep one writer at a time. Changes here are lost if you close or reload before downloading.</p>
<p>Open the packet's review.html separately to read the code diff. This page does not verify
the bundle or authenticate anyone.</p>
<noscript>This editor needs JavaScript. Use skein.py comment, edit-comment, resolve-comment or
reopen-comment instead; this page has made no changes.</noscript>
<p id="editor-status" role="status" aria-live="polite">Loading comments…</p>
<button id="download" type="button" disabled>Download edits</button>
<nav aria-label="Comments"><ol id="comment-index"></ol></nav>
<section id="composer" aria-label="Add an anchored comment"></section>
<section id="comments" tabindex="-1" aria-label="Comment editor"></section>
</main><script type="application/json" id="editor-data">{payload}</script>{addition}<script>{script}</script>
</body></html>
'''


def _inert_json(value: object) -> str:
    # Imported code and comments must never close a script data element.
    return (json.dumps(value, ensure_ascii=True, sort_keys=True)
            .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e"))


def _packet_context(packet: Path) -> tuple[dict[str, bytes], list[skein.Anchor]]:
    snapshots = {name: _read(packet / name) for name in ("packet.json", "anchors.json")}
    metadata = skein._load_packet(packet)
    anchors = skein._load_anchors(packet)
    slots = [(a.commit, a.path, a.side, a.line) for a in anchors]
    if len(slots) != len(set(slots)):
        raise skein.SkeinError("ambiguous duplicate packet anchors")
    for anchor in anchors:
        side = "base" if anchor.side == "old" else "head"
        if anchor.commit != metadata[side]["commit"]:
            raise skein.SkeinError("anchor commit does not match its packet side")
    if any(_read(packet / name) != value for name, value in snapshots.items()):
        raise skein.SkeinError("packet changed during validation")
    return snapshots, anchors


def render_composer(packet: Path) -> str:
    """Bind additions to this exact packet and existing comment baseline."""
    snapshots, anchors = _packet_context(packet)
    original = _read(packet / "comments.json")
    comments = _comments(original.decode("utf-8"))
    envelope = {
        "format": EDIT_FORMAT, "version": 2, "base_sha256": _digest(original),
        "packet_sha256": _digest(snapshots["packet.json"]),
        "anchors_sha256": _digest(snapshots["anchors.json"]),
        "document": json.loads(skein.dumps_comments(comments)),
    }
    return _render(envelope, anchors)


def apply_edits(packet: Path, edits: Path) -> int:
    """Validate edits and optional packet-bound additions before one atomic write."""
    packet = packet.expanduser().resolve()
    skein._load_packet(packet)
    original = _read(packet / "comments.json")
    before = _comments(original.decode("utf-8"))
    try:
        value = json.loads(_read(edits).decode("utf-8"), object_pairs_hook=skein._unique_object)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise skein.SkeinError(f"invalid edits JSON: {exc}") from exc
    keys = {"format", "version", "base_sha256", "document"}
    if (not isinstance(value, dict) or value.get("format") != EDIT_FORMAT
            or type(value.get("version")) is not int or value["version"] not in {1, 2}):
        raise skein.SkeinError("unsupported comment edits header")
    composing = value["version"] == 2
    if set(value) != keys | ({"packet_sha256", "anchors_sha256"} if composing else set()):
        raise skein.SkeinError("unsupported comment edits header")
    snapshots, anchors = _packet_context(packet) if composing else ({}, [])
    for name, raw in snapshots.items():
        if value[name.removesuffix(".json") + "_sha256"] != _digest(raw):
            raise skein.SkeinError("stale edits: packet identity or anchors changed")
    if value["base_sha256"] != _digest(original):
        raise skein.SkeinError("stale edits: comments.json changed; generate a fresh editor")
    after = _comments(json.dumps(value["document"], ensure_ascii=True))
    if len(after) < len(before) or (not composing and len(before) != len(after)):
        raise skein.SkeinError("edits cannot add or remove comments")
    for old, new in zip(before, after):
        old_fixed = {k: v for k, v in old.to_dict().items() if k not in {"body", "resolution"}}
        new_fixed = {k: v for k, v in new.to_dict().items() if k not in {"body", "resolution"}}
        if old_fixed != new_fixed:
            raise skein.SkeinError("edits cannot change comment order, IDs, anchors or provenance")
    available = set(anchors)
    for added in after[len(before):]:
        if (added.state != "anchored" or added.rebased_from is not None
                or added.orphan_reason is not None or added.anchor not in available):
            raise skein.SkeinError("new comments must name an exact packet anchor without provenance")
    changed = sum(old != new for old, new in zip(before, after)) + len(after) - len(before)
    if changed:
        # Catch intervening changes during validation. Like the existing editing CLI,
        # this is a one-writer workflow, not a cross-process transaction protocol.
        if _read(packet / "comments.json") != original:
            raise skein.SkeinError("comments.json changed during validation; nothing applied")
        if any(_read(packet / name) != raw for name, raw in snapshots.items()):
            raise skein.SkeinError("packet changed during validation; nothing applied")
        skein._atomic_comments(packet, after)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    page = commands.add_parser("page", help="create a new, self-contained HTML editor")
    page.add_argument("comments", type=Path)
    page.add_argument("output", type=Path, help="new HTML file; existing files are refused")
    compose = commands.add_parser("compose", help="create a packet-bound editor that can add comments")
    compose.add_argument("packet", type=Path)
    compose.add_argument("output", type=Path, help="new HTML file; existing files are refused")
    apply = commands.add_parser("apply", help="validate and atomically apply downloaded edits")
    apply.add_argument("packet", type=Path)
    apply.add_argument("edits", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command in {"page", "compose"}:
            result = (render_editor(_read(args.comments)) if args.command == "page"
                      else render_composer(args.packet))
            with args.output.open("x", encoding="utf-8", newline="\n") as stream:
                stream.write(result)
            print(f"Created {args.output}")
        else:
            changed = apply_edits(args.packet, args.edits)
            print(f"Applied edits to {changed} comment(s).")
    except (OSError, UnicodeError, skein.SkeinError) as exc:
        print(f"comment-editor: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
