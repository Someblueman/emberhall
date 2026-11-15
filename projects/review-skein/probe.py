#!/usr/bin/env python3
"""Probe an exported Skein packet without a browser.

The probe reads a packet's static ``review.html`` and reports what the markup
itself shows: whether the page really is static and offline, whether its
structure names what it presents, and whether every diff row says in words what
its colour says. It also prints a linear transcript of the page in document
order, so a reviewer can read what a screen reader would announce without
owning a browser.

This is a pre-flight check, not a screen reader. It cannot judge rendering,
real focus order, contrast, speech, or how a page feels on a phone. Milestone
acceptance still needs a real browser and screen-reader try by a non-author.

Usage:
    python3 projects/review-skein/probe.py audit PACKET [--json]
    python3 projects/review-skein/probe.py transcript PACKET [--max-rows N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

VOID_TAGS = frozenset({"area", "base", "br", "col", "embed", "hr", "img", "input",
                        "link", "meta", "param", "source", "track", "wbr"})
SILENT_TAGS = frozenset({"script", "style", "template"})
HEADING = re.compile(r"h[1-6]")
LANGUAGE = re.compile(r"[A-Za-z]{2,3}(-[A-Za-z0-9]{2,8})*")
SCHEME = re.compile(r"^[a-z][a-z0-9+.-]*:")
LINK_TARGETS = ("src", "href", "srcset", "action", "data", "poster", "formaction")
ID_REFERENCES = ("aria-labelledby", "aria-describedby", "aria-controls", "for")


@dataclass
class Node:
    """One element of the small document tree the probe builds."""

    tag: str
    attrs: dict = field(default_factory=dict)
    children: list = field(default_factory=list)


@dataclass(frozen=True)
class Finding:
    """One thing the markup shows. ``severity`` is ``error`` or ``notice``."""

    code: str
    severity: str
    detail: str


class TreeBuilder(HTMLParser):
    """Builds a document tree from the packet's static HTML."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("#document")
        self.stack = [self.root]

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {name: (value if value is not None else "") for name, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in VOID_TAGS:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        node = Node(tag, {name: (value if value is not None else "") for name, value in attrs})
        self.stack[-1].children.append(node)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def parse(text: str) -> Node:
    """Parse HTML text into the probe's document tree."""
    builder = TreeBuilder()
    builder.feed(text)
    builder.close()
    return builder.root


def walk(node: Node):
    """Every descendant element, in document order."""
    for child in node.children:
        if isinstance(child, Node):
            yield child
            yield from walk(child)


def elements(node: Node, tag: str) -> list:
    """Every descendant element with ``tag``, in document order."""
    found = []
    for child in node.children:
        if isinstance(child, Node):
            if child.tag == tag:
                found.append(child)
            found.extend(elements(child, tag))
    return found


def collapse(text: str) -> str:
    """Collapse whitespace runs into single spaces."""
    return " ".join(text.split())


def hidden(node: Node) -> bool:
    """True when a screen reader would not read this element at all.

    Visually hidden text is *not* hidden here: a class that only hides text
    from the eye is exactly the text a screen reader is meant to speak.
    """
    if node.tag in SILENT_TAGS:
        return True
    if "hidden" in node.attrs:
        return True
    if node.attrs.get("aria-hidden", "").strip().lower() == "true":
        return True
    style = node.attrs.get("style", "").lower().replace(" ", "")
    return "display:none" in style or "visibility:hidden" in style


def _hidden_subtree_ids(node: Node, ancestor_hidden: bool = False) -> set[int]:
    """Every element id() excluded from assistive reading by itself or an ancestor."""
    result: set[int] = set()
    now_hidden = ancestor_hidden or hidden(node)
    if now_hidden:
        result.add(id(node))
    for child in node.children:
        if isinstance(child, Node):
            result.update(_hidden_subtree_ids(child, now_hidden))
    return result


def text_of(node: Node, hidden_tree: set[int] | None = None) -> str:
    """The words a screen reader would read from this element."""
    if hidden(node) or (hidden_tree is not None and id(node) in hidden_tree):
        return ""
    parts = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif not hidden(child) and (hidden_tree is None or id(child) not in hidden_tree):
            parts.append(text_of(child, hidden_tree))
    return collapse("".join(parts))


def has_letters(text: str) -> bool:
    return any(character.isalpha() for character in text)


def label_of(text: str) -> str:
    """The words of a cell without its numbers: ``Added. 12`` becomes ``Added``."""
    return "".join(character for character in text if character.isalpha())


def is_external(value: str) -> bool:
    """True when a reference leaves the self-contained review.html page.

    A Skein review page is a single static document whose only permitted
    references are in-page ``#fragment`` anchors. Any scheme, protocol-relative
    URL, root path, ``..`` traversal or relative file target leaves the packet's
    self-contained HTML boundary.
    """
    cleaned = value.strip()
    if not cleaned or cleaned.startswith("#"):
        return False
    return True


def _is_column_header_row(row: Node, thead_rows: set[int]) -> bool:
    """True when a table row is a column-header row rather than a diff row."""
    if id(row) in thead_rows:
        return True
    cells = [child for child in row.children
             if isinstance(child, Node) and child.tag in ("th", "td")]
    return bool(cells) and all(
        cell.tag == "th" and cell.attrs.get("scope", "").strip().lower() == "col"
        for cell in cells
    )


def index_ids(node: Node) -> dict:
    """Map each id to the first element that carries it."""
    ids = {}
    for element in walk(node):
        identifier = element.attrs.get("id", "").strip()
        if identifier and identifier not in ids:
            ids[identifier] = element
    return ids


def accessible_name(node: Node, ids: dict | None = None,
                    hidden_tree: set[int] | None = None) -> str:
    """The name a screen reader would announce for a landmark or region."""
    if hidden(node) or (hidden_tree is not None and id(node) in hidden_tree):
        return ""
    label = collapse(node.attrs.get("aria-label", ""))
    if label:
        return label
    referenced = node.attrs.get("aria-labelledby", "").strip()
    if referenced and ids is not None:
        parts = []
        for token in referenced.split():
            target = ids.get(token)
            if target is not None:
                parts.append(text_of(target, hidden_tree))
        name = collapse(" ".join(part for part in parts if part))
        if name:
            return name
    return ""


def summarize(tree: Node) -> dict:
    """Counts of what the page contains."""
    nodes = list(walk(tree))
    return {
        "headings": len([node for node in nodes if HEADING.fullmatch(node.tag)]),
        "sections": len([node for node in nodes if node.tag == "section"]),
        "tables": len([node for node in nodes if node.tag == "table"]),
        "rows": len([node for node in nodes if node.tag == "tr"]),
    }


def audit(tree: Node, notes=()) -> list:
    """Report what the markup shows, as a list of findings.

    ``error`` findings are defects a reader would trip over. ``notice`` findings
    are worth a human glance but are not defects on their own.
    """
    findings = list(notes)
    nodes = list(walk(tree))
    hidden_tree = _hidden_subtree_ids(tree)
    owners: dict = {}
    for node in nodes:
        identifier = node.attrs.get("id", "").strip()
        if identifier:
            owners.setdefault(identifier, []).append(node)
    first = {identifier: group[0] for identifier, group in owners.items()}

    for identifier in sorted(owners):
        if len(owners[identifier]) > 1:
            findings.append(Finding("duplicate-id", "error",
                                    f"{len(owners[identifier])} elements share the id {identifier!r}"))

    documents = [node for node in nodes if node.tag == "html"]
    if not documents:
        findings.append(Finding("missing-html", "error", "the document has no <html> element"))
    else:
        language = documents[0].attrs.get("lang", "").strip()
        if not language:
            findings.append(Finding("missing-lang", "error", "<html> has no lang attribute"))
        elif not LANGUAGE.fullmatch(language):
            findings.append(Finding("odd-lang", "notice",
                                    f"<html lang={language!r}> is not a plain language tag"))

    for node in nodes:
        if node.tag == "script":
            findings.append(Finding("script-element", "error",
                                    "<script> is not allowed in a static packet"))
        if node.tag == "form":
            findings.append(Finding("form-element", "error",
                                    "<form> is not allowed in a static packet"))
        for name in sorted(node.attrs):
            if name.startswith("on"):
                findings.append(Finding("inline-handler", "error",
                                        f"<{node.tag}> carries the inline handler {name}"))
        for name in LINK_TARGETS:
            value = node.attrs.get(name, "").strip()
            if value and is_external(value):
                findings.append(Finding("external-reference", "error",
                                        f"<{node.tag} {name}> leaves the packet: {value}"))

    for node in nodes:
        for name in ID_REFERENCES:
            value = node.attrs.get(name, "").strip()
            if not value:
                continue
            for token in value.split():
                if token not in owners:
                    findings.append(Finding("broken-reference", "error",
                                            f"<{node.tag} {name}> names the missing id {token!r}"))
        href = node.attrs.get("href", "").strip()
        if href.startswith("#") and len(href) > 1 and href[1:] not in owners:
            findings.append(Finding("broken-fragment", "error",
                                    f"<{node.tag} href={href!r}> points at the missing id {href[1:]!r}"))

    previous = 0
    for node in nodes:
        if not HEADING.fullmatch(node.tag):
            continue
        level = int(node.tag[1])
        if previous and level > previous + 1:
            findings.append(Finding("heading-skip", "error", f"<{node.tag}> follows <h{previous}>"))
        if not text_of(node, hidden_tree):
            findings.append(Finding("empty-heading", "error", f"<{node.tag}> has no text"))
        previous = level

    for number, table in enumerate([node for node in nodes if node.tag == "table"], 1):
        captions = [child for child in table.children
                    if isinstance(child, Node) and child.tag == "caption"
                    and id(child) not in hidden_tree and text_of(child, hidden_tree)]
        if not captions:
            findings.append(Finding("table-without-caption", "error",
                                    f"table {number} has no <caption>"))
        rows = elements(table, "tr")
        thead_rows = {
            id(row)
            for thead in elements(table, "thead")
            for row in elements(thead, "tr")
        }
        columns = [row for row in rows
                   if id(row) not in hidden_tree
                   and any(id(cell) not in hidden_tree
                           and cell.attrs.get("scope", "").strip().lower() == "col"
                           and text_of(cell, hidden_tree)
                           for cell in elements(row, "th"))]
        if not columns:
            findings.append(Finding("table-without-column-headers", "error",
                                    f"table {number} has no column header cell"))
        for index, row in enumerate(rows, 1):
            if _is_column_header_row(row, thead_rows):
                continue
            headers = [cell for cell in elements(row, "th")
                       if id(row) not in hidden_tree
                       and id(cell) not in hidden_tree
                       and cell.attrs.get("scope", "").strip().lower() == "row"]
            words = [text_of(cell, hidden_tree) for cell in headers]
            if not any(has_letters(word) for word in words):
                findings.append(Finding("row-without-words", "error",
                                        f"row {index} of table {number} states its status "
                                        "with colour or class only"))
        spoken: dict = {}
        for row in rows:
            if _is_column_header_row(row, thead_rows) or id(row) in hidden_tree:
                continue
            classes = [name for name in row.attrs.get("class", "").split() if name]
            words = {label_of(text_of(cell, hidden_tree)) for cell in elements(row, "th")
                     if id(cell) not in hidden_tree
                     and cell.attrs.get("scope", "").strip().lower() == "row"}
            words.discard("")
            for name in classes:
                spoken.setdefault(name, set()).update(words)
        by_label: dict = {}
        for name in sorted(spoken):
            for word in sorted(spoken[name]):
                by_label.setdefault(word, []).append(name)
        for word in sorted(by_label):
            if len(by_label[word]) > 1:
                findings.append(Finding("shared-row-label", "notice",
                                        f"table {number}: the row classes "
                                        f"{', '.join(by_label[word])} all read as {word!r}"))

    for node in nodes:
        if node.tag == "nav" and not accessible_name(node, first, hidden_tree):
            findings.append(Finding("unlabelled-nav", "notice", "<nav> has no accessible name"))
        if node.tag == "section" and not accessible_name(node, first, hidden_tree):
            findings.append(Finding("unlabelled-section", "notice",
                                    "<section> has no accessible name"))
    return findings


def _emit_table(table: Node, lines: list, state: dict, hidden_tree: set[int]) -> None:
    captions = [child for child in table.children
                if isinstance(child, Node) and child.tag == "caption"
                and id(child) not in hidden_tree]
    caption_text = text_of(captions[0], hidden_tree) if captions else ""
    lines.append(f"Table: {caption_text or '(no caption)'}")
    rows = [row for row in elements(table, "tr") if id(row) not in hidden_tree]
    for index, row in enumerate(rows):
        if state["rows"] >= state["max_rows"]:
            state["hidden"] += len(rows) - index
            break
        state["rows"] += 1
        cells = [child for child in row.children
                 if isinstance(child, Node) and child.tag in ("th", "td")
                 and id(child) not in hidden_tree]
        lines.append("  " + " | ".join(text_of(cell, hidden_tree) for cell in cells))


def _emit(node: Node, lines: list, state: dict, ids: dict, hidden_tree: set[int]) -> None:
    for child in node.children:
        if not isinstance(child, Node):
            continue
        tag = child.tag
        if tag in SILENT_TAGS or hidden(child) or id(child) in hidden_tree:
            continue
        if HEADING.fullmatch(tag):
            lines.append(f"Heading {int(tag[1])}: {text_of(child, hidden_tree)}")
        elif tag == "p":
            lines.append(f"Text: {text_of(child, hidden_tree)}")
        elif tag == "nav":
            lines.append(f"Navigation {accessible_name(child, ids, hidden_tree) or '(unnamed)'}:")
            for item in elements(child, "li"):
                if id(item) not in hidden_tree:
                    lines.append(f"  - {text_of(item, hidden_tree)}")
        elif tag == "table":
            _emit_table(child, lines, state, hidden_tree)
        elif tag == "section":
            lines.append(f"Section {accessible_name(child, ids, hidden_tree) or '(unnamed)'}:")
            _emit(child, lines, state, ids, hidden_tree)
        elif tag == "footer":
            lines.append(f"Footer: {text_of(child, hidden_tree)}")
        elif tag == "a" and "skip" in child.attrs.get("class", "").split():
            lines.append(f"Skip link: {text_of(child, hidden_tree)} -> {child.attrs.get('href', '')}")
        else:
            _emit(child, lines, state, ids, hidden_tree)


def transcript(tree: Node, max_rows: int = 200) -> list:
    """A linear reading of the page in document order.

    Each line names what a screen reader would meet there. This is an
    approximation of a reading order, not a screen reader.
    """
    lines: list = []
    state = {"rows": 0, "hidden": 0, "max_rows": max_rows}
    hidden_tree = _hidden_subtree_ids(tree)
    document = None
    for node in walk(tree):
        if node.tag == "html":
            document = node
            break
    ids = index_ids(document if document is not None else tree)
    if document is not None:
        language = document.attrs.get("lang", "").strip()
        lines.append(f"Document language: {language or '(none)'}")
        if id(document) not in hidden_tree:
            titles = [t for t in elements(document, "title") if id(t) not in hidden_tree]
            if titles and text_of(titles[0], hidden_tree):
                lines.append(f"Title: {text_of(titles[0], hidden_tree)}")
            _emit(document, lines, state, ids, hidden_tree)
    else:
        _emit(tree, lines, state, ids, hidden_tree)
    if state["hidden"]:
        lines.append(f"... {state['hidden']} further row(s) were not shown; "
                     "raise --max-rows to see them.")
    return lines


def _packet_notes(directory: Path) -> list:
    """Findings from the packet manifest, when there is one."""
    manifest = directory / "packet.json"
    if not manifest.is_file():
        return [Finding("packet-json-missing", "notice",
                        "packet.json is absent; only the HTML was probed")]
    try:
        data = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [Finding("packet-json-unreadable", "error",
                        f"packet.json could not be read: {error}")]
    if not isinstance(data, dict):
        return [Finding("packet-json-unreadable", "error", "packet.json is not a JSON object")]
    notes = []
    if data.get("format") not in (None, "review-skein-packet"):
        notes.append(Finding("unexpected-format", "notice",
                             f"packet.json declares the format {data.get('format')!r}"))
    identity = []
    for side in ("base", "head"):
        part = data.get(side)
        if isinstance(part, dict):
            commit = str(part.get("commit", "")).strip()
            reference = str(part.get("ref", "")).strip()
            if commit:
                identity.append(f"{side} {reference or '(unnamed ref)'} {commit}")
    if identity:
        notes.append(Finding("packet-identity", "notice", "; ".join(identity)))
    return notes


def load_packet(directory: Path):
    """Read a packet's static review page and its manifest notes."""
    page = directory / "review.html"
    if not page.is_file():
        raise ValueError(f"{page} is not a regular file")
    tree = parse(page.read_text(encoding="utf-8"))
    return tree, _packet_notes(directory)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Probe a Skein packet offline.")
    commands = parser.add_subparsers(dest="command", required=True)
    audit_command = commands.add_parser("audit", help="report accessibility and offline findings")
    audit_command.add_argument("packet", help="packet directory that contains review.html")
    audit_command.add_argument("--json", action="store_true", help="print the findings as JSON")
    transcript_command = commands.add_parser("transcript", help="print a linear reading transcript")
    transcript_command.add_argument("packet", help="packet directory that contains review.html")
    transcript_command.add_argument("--max-rows", type=int, default=200,
                                    help="how many table rows the transcript may print")
    arguments = parser.parse_args(argv)
    if arguments.command == "transcript" and arguments.max_rows < 0:
        print("probe: --max-rows must not be negative", file=sys.stderr)
        return 2
    try:
        tree, notes = load_packet(Path(arguments.packet))
    except (OSError, ValueError) as error:
        print(f"probe: {error}", file=sys.stderr)
        return 2
    if arguments.command == "audit":
        findings = audit(tree, notes)
        errors = [finding for finding in findings if finding.severity == "error"]
        if arguments.json:
            print(json.dumps({
                "version": 1,
                "errors": len(errors),
                "notices": len(findings) - len(errors),
                "findings": [{"code": finding.code, "severity": finding.severity,
                              "detail": finding.detail} for finding in findings],
                "summary": summarize(tree),
            }, indent=2, sort_keys=True))
        else:
            for finding in findings:
                print(f"{finding.severity} {finding.code}: {finding.detail}")
            print(f"audit: {len(errors)} error(s), {len(findings) - len(errors)} notice(s)")
        return 1 if errors else 0
    for line in transcript(tree, arguments.max_rows):
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
