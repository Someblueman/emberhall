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
    payload = json.dumps(envelope, ensure_ascii=True, sort_keys=True)
    # A comment must never close its data element, even if it contains HTML.
    payload = payload.replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
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
textarea, select, button {{ font: inherit; padding: .5rem; }}
button {{ margin-block: .75rem; }}
:focus-visible {{ outline: 3px solid #964400; outline-offset: 3px; }}
</style></head><body><a href="#comments">Skip to comments</a><main>
<h1>Edit Skein comments</h1>
<p>Edit existing comment bodies and open/resolved status. Anchors and orphan history stay fixed.
This local page does not write your packet. Download edits, then apply them with the CLI.
Keep one writer at a time. Changes here are lost if you close or reload before downloading.</p>
<p>Open the packet's review.html separately to read the code diff. This page does not verify
the bundle or authenticate anyone.</p>
<noscript>This editor needs JavaScript. Use skein.py edit-comment, resolve-comment or
reopen-comment instead; this page has made no changes.</noscript>
<p id="editor-status" role="status" aria-live="polite">Loading comments…</p>
<button id="download" type="button" disabled>Download edits</button>
<nav aria-label="Comments"><ol id="comment-index"></ol></nav>
<section id="comments" tabindex="-1" aria-label="Comment editor"></section>
</main><script type="application/json" id="editor-data">{payload}</script><script>{script}</script>
</body></html>
'''


def apply_edits(packet: Path, edits: Path) -> int:
    """Apply bodies/resolutions together; reject stale or identity-changing downloads."""
    packet = packet.expanduser().resolve()
    skein._load_packet(packet)
    original = _read(packet / "comments.json")
    before = _comments(original.decode("utf-8"))
    try:
        value = json.loads(_read(edits).decode("utf-8"), object_pairs_hook=skein._unique_object)
    except (json.JSONDecodeError, RecursionError) as exc:
        raise skein.SkeinError(f"invalid edits JSON: {exc}") from exc
    if (not isinstance(value, dict)
            or set(value) != {"format", "version", "base_sha256", "document"}
            or value["format"] != EDIT_FORMAT or type(value["version"]) is not int
            or value["version"] != EDIT_VERSION):
        raise skein.SkeinError("unsupported comment edits header")
    if value["base_sha256"] != _digest(original):
        raise skein.SkeinError("stale edits: comments.json changed; generate a fresh editor")
    after = _comments(json.dumps(value["document"], ensure_ascii=True))
    if len(before) != len(after):
        raise skein.SkeinError("edits cannot add or remove comments")
    for old, new in zip(before, after):
        old_fixed = {k: v for k, v in old.to_dict().items() if k not in {"body", "resolution"}}
        new_fixed = {k: v for k, v in new.to_dict().items() if k not in {"body", "resolution"}}
        if old_fixed != new_fixed:
            raise skein.SkeinError("edits cannot change comment order, IDs, anchors or provenance")
    changed = sum(old != new for old, new in zip(before, after))
    if changed:
        # Catch intervening changes during validation. Like the existing editing CLI,
        # this is a one-writer workflow, not a cross-process transaction protocol.
        if _read(packet / "comments.json") != original:
            raise skein.SkeinError("comments.json changed during validation; nothing applied")
        skein._atomic_comments(packet, after)
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    page = commands.add_parser("page", help="create a new, self-contained HTML editor")
    page.add_argument("comments", type=Path)
    page.add_argument("output", type=Path, help="new HTML file; existing files are refused")
    apply = commands.add_parser("apply", help="validate and atomically apply downloaded edits")
    apply.add_argument("packet", type=Path)
    apply.add_argument("edits", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "page":
            result = render_editor(_read(args.comments))
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
