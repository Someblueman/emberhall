"""Emberhall's illustrated cutaway, derived from a verified journal snapshot."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import textwrap
import time
from xml.sax.saxutils import escape, quoteattr

from .record import Record
from .watch import entries as watch_entries, TERMINAL

INK = "#ede0c4"
MUTED = "#bcb7ad"
GOLD = "#efb668"


def clean_xml(value: object) -> str:
    """Journal strings can contain XML-forbidden controls and surrogates."""
    clean = "".join(c if c in "\t\n\r" or 0x20 <= ord(c) <= 0xD7FF or
                    0xE000 <= ord(c) <= 0xFFFD or 0x10000 <= ord(c) <= 0x10FFFF
                    else "\ufffd" for c in str(value))
    return clean


def xml(value: object) -> str:
    return escape(clean_xml(value))


def attr(value: object) -> str:
    return quoteattr(clean_xml(value))


def text(x: float, y: float, value: object, size: int = 16,
         fill: str = INK, anchor: str = "start", serif: bool = False) -> str:
    family = "Georgia,serif" if serif else "Verdana,sans-serif"
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}">{xml(value)}</text>')


def lines(x: float, y: float, value: str, width: int = 37,
          size: int = 16, fill: str = INK) -> tuple[str, int]:
    wrapped = textwrap.wrap(" ".join(value.split()), width=width) or [""]
    return "".join(text(x, y + i * (size + 7), row, size, fill)
                   for i, row in enumerate(wrapped)), len(wrapped) * (size + 7)


def portrait(resident_id: str, resident: dict, x: int, y: int) -> str:
    seed = hashlib.sha256(resident_id.encode()).digest()
    awake = resident["awake"]
    coat = ["#7f9c87", "#ae7f66", "#7f94aa", "#a590b0", "#c1a067"][seed[0] % 5]
    hair = ["#40372e", "#b6ab8d", "#805c3e", "#bf7953"][seed[1] % 4]
    out = [f'<g data-resident={attr(resident_id)} data-state="{ "awake" if awake else "asleep" }">',
           f'<title>{xml(resident["name"])}: {"recorded awake" if awake else "asleep"}. '
           f'{xml(resident["note"])}</title>',
           f'<path d="M{x-44} {y+58} V{y+4} Q{x-44} {y-40} {x} {y-40} '
           f'Q{x+44} {y-40} {x+44} {y+4} V{y+58}Z" fill="{ "#4d4437" if awake else "#252f39" }" stroke="#786c57"/>',
           f'<path d="M{x-31} {y+51} Q{x-28} {y+13} {x} {y+12} '
           f'Q{x+28} {y+13} {x+31} {y+51}" fill="{coat}"/>',
           f'<ellipse cx="{x}" cy="{y-3}" rx="19" ry="23" fill="#dbb48a"/>',
           f'<path d="M{x-20} {y-5} Q{x-25} {y-35} {x+3} {y-29} '
           f'Q{x+25} {y-30} {x+20} {y-1} L{x+12} {y-18} '
           f'Q{x-3} {y-9} {x-20} {y-5}" fill="{hair}"/>']
    if awake:
        out.append(f'<path d="M{x-10} {y-1}v3m20-3v3m-14 9q4 3 8 0" '
                   'fill="none" stroke="#40372e" stroke-width="2"/>')
        if seed[2] % 2:
            out.append(f'<path d="M{x-16} {y-4}h12v9h-12zm20 0h12v9h-12zm-8 3h8" '
                       'fill="none" stroke="#40372e" stroke-width="1.5"/>')
        out.append(f'<circle cx="{x+32}" cy="{y+40}" r="5" fill="{GOLD}"/>')
    else:
        out.append(f'<path d="M{x-12} {y}q4 4 8 0m8 0q4 4 8 0" '
                   'fill="none" stroke="#40372e" stroke-width="2"/>')
        out.append(f'<path d="M{x-40} {y+29}q40-13 80 0v29h-80z" fill="{coat}"/>')
        out.append(f'<path d="M{x-40} {y+34}h80m-80 10h80" stroke="#d2c2a5" opacity=".35"/>')
        out.append(text(x + 25, y - 18, "z", 17, MUTED))
    name = resident["name"]
    out += [text(x, y + 82, name if len(name) <= 12 else name[:11] + "…", 15, anchor="middle"), "</g>"]
    return "".join(out)


def render(record: Record, observed_at: float | None = None) -> str:
    state, events, head = record.read()
    observed_at = time.time() if observed_at is None else observed_at
    if not math.isfinite(observed_at) or observed_at < state["at"]:
        raise ValueError("observation must be finite and no earlier than the journal snapshot")
    observed = datetime.fromtimestamp(observed_at, timezone.utc).strftime("%d %b %Y · %H:%M UTC")
    # Pin HEAD once: the illustration says exactly which source history it saw.
    source_result = subprocess.run(
        ["git", "-C", str(record.root), "rev-parse", "--verify", "--quiet", "HEAD^{commit}"],
        capture_output=True, check=False)
    if source_result.returncode not in (0, 1):
        raise ValueError("cannot inspect source HEAD")
    source = source_result.stdout.decode().strip() or None
    commits = []
    if source:
        raw = record.git("log", "-3", "--format=%H%x00%s", source).decode(errors="replace")
        commits = [row.split("\0", 1) for row in raw.splitlines() if "\0" in row]
    residents = {key: value for key, value in state["residents"].items() if key != "watch-keeper"}
    has_clock = "watch-keeper" in state["residents"]
    awake = [(k, v) for k, v in residents.items() if v["awake"]]
    asleep = [(k, v) for k, v in residents.items() if not v["awake"]]
    tasks = [(k, v) for k, v in state["tasks"].items() if v["status"] != "done"]
    expired = {k for k, v in tasks if v["status"] == "claimed" and v["until"] <= observed_at}
    # These are recorded repair claims, not a fresh independent audit of their evidence.
    scars = [(k, v) for k, v in state["lessons"].items()
             if v["status"] == "observed" and v["reviews"] and
             re.search(r"repair|repaired|fix|regression", v["evidence"], re.I)]
    pending = sum(p["status"] == "pending" for p in state["proposals"].values())
    watch_history = watch_entries(events)
    watches = [entry for entry in watch_history if entry["kind"] == "start"][-3:]
    out = []
    y = 224

    def room(title: str, subtitle: str, height: int, fill: str = "#303b3b") -> int:
        nonlocal y
        top = y
        out.append(f'<rect x="26" y="{top}" width="388" height="{height}" fill="{fill}"/>')
        out.append(f'<path d="M26 {top}H414M26 {top+height}H414" stroke="#86664a" stroke-width="10"/>')
        out.append(text(48, top + 34, title, 25, GOLD, serif=True))
        out.append(text(48, top + 60, subtitle, 14, MUTED))
        y += height
        return top

    if watches:
        top = room("The watch lantern", "Recent starts · newest first", 111 + 82 * len(watches))
        for i, start in enumerate(reversed(watches)):
            history = [entry for entry in watch_history if entry["run"] == start["run"]]
            terminal = next((entry for entry in reversed(history) if entry["kind"] in TERMINAL), None)
            result = next((entry for entry in reversed(history) if entry["kind"] == "execution-result"), None)
            receipt = terminal or result or start
            if terminal:
                label = ("Interrupted · outcome unknown" if terminal["kind"] == "recovered-interruption"
                         else f'Finished · {terminal["outcome"]}')
            else:
                label = "Result saved · cleanup pending" if result else "No terminal receipt yet"
            name = residents.get(start["resident"], {}).get("name", start["resident"])
            sy = top + 88 + i * 82
            color = GOLD if not terminal or terminal.get("outcome") == "success" else "#e9a07b"
            out.append(f'<g data-watch={attr(start["run"])} data-state="{ "terminal" if terminal else "pending" }">'
                       f'<title>{xml(name)}. {xml(label)}. Receipt event {receipt["sequence"]}. '
                       f'{xml(json.dumps(receipt, sort_keys=True))}</title>')
            out.append(f'<circle cx="57" cy="{sy-5}" r="6" fill="{color}"/>')
            out.append(text(74, sy, textwrap.shorten(name, width=24, placeholder="…"), 16))
            out.append(text(74, sy + 23, label, 14, color))
            out.append(text(74, sy + 43, f'Event {receipt["sequence"]}', 12, MUTED))
            out.append('</g>')
        out.append(text(48, y - 18, "Recorded outcomes, not a live process check.", 13, MUTED))

    h = 142 + math.ceil(len(awake) / 3) * 139
    top = room("The hearth", f'{len(awake)} recorded awake · the lamp is lit', max(h, 166), "#3d4038")
    if not awake:
        out.append(text(220, top + 114, "An ember waits for the next arrival.", 16, anchor="middle"))
    for i, (key, value) in enumerate(awake):
        out.append(portrait(key, value, 94 + (i % 3) * 126, top + 117 + (i // 3) * 139))
    # A hearth is a symbol of continuity, not a claim that a process is live.
    out.append(f'<path d="M181 {y-12}h78m-61-2q-10-18 9-28q-3 16 11 21q-4-20 12-27q-2 18 13 33" '
               f'fill="none" stroke="{GOLD}" stroke-width="3"/>')

    if has_clock:
        out.append('<g data-machine="watch-keeper"><title>Watch keeper is a scheduler, not a model resident.</title>'
                   + f'<circle cx="390" cy="{top+28}" r="13" fill="#26312f" stroke="{GOLD}"/>'
                   + f'<path d="M390 {top+19}v9l6 4" fill="none" stroke="{GOLD}"/>' + '</g>')

    h = max(133, 89 + math.ceil(len(asleep) / 3) * 139)
    top = room("The quiet loft", f'{len(asleep)} asleep · their places are kept', h, "#29353e")
    if not asleep:
        out.append(text(48, top + 104, "No sleep has been recorded yet.", 16))
    for i, (key, value) in enumerate(asleep):
        out.append(portrait(key, value, 94 + (i % 3) * 126, top + 117 + (i // 3) * 139))

    task_cards = []
    for key, task in tasks:
        label = "LEASE EXPIRED · available" if key in expired else (
            "CLAIMED" if task["status"] == "claimed" else "OPEN · available")
        owner = residents.get(task["owner"], {}).get("name", "No holder")
        title_svg, title_h = lines(72, 50, task["title"], 31)
        height = title_h + 82
        color = "#e9a07b" if key in expired else GOLD
        task_cards.append((height, f'<g data-task={attr(key)} data-state="'
                           f'{"expired" if key in expired else task["status"]}">'
                           f'<title>{xml(key)}. {xml(task["description"])}. Lease until '
                           f'{task["until"]}. Holder: {xml(owner)}.</title>'
                           f'<rect x="45" y="8" width="350" height="{height-15}" rx="5" '
                           'fill="#26312f" stroke="#73654d"/>'
                           f'<path d="M56 28h6m-3-3v6" stroke="{color}" stroke-width="2"/>'
                           + text(72, 28, label, 13, color) + title_svg
                           + text(72, title_h + 57, textwrap.shorten(owner, width=32, placeholder="…"), 14, MUTED) + '</g>'))
    top = room("The workshop", f'{len(tasks)} unfinished · {len(expired)} expired leases',
               105 + sum(h for h, _ in task_cards), "#343b33")
    card_y = top + 77
    for height, svg in task_cards:
        out.append(f'<g transform="translate(0 {card_y})">{svg}</g>')
        card_y += height
    if not tasks:
        out.append(text(48, top + 95, "The benches are clear.", 16))
    out.append(text(48, y - 12, "An expired lease is not proof of death.", 13, MUTED))

    top = room("The council window", f'{pending} proposals awaiting a decision', 142, "#303a40")
    ratified = sum(p["status"] in {"ratified", "enacted"} for p in state["proposals"].values())
    out.append(f'<path d="M342 {top+106}v-23a20 20 0 0 1 40 0v23z" fill="#cfac71" stroke="#9a805f"/>')
    out.append(f'<path d="M362 {top+64}v42m-20-19h40" stroke="#303a40" stroke-width="4"/>')
    out.append(text(48, top + 97, f'{ratified} ratified in the record', 16))
    out.append(text(48, top + 122, 'Law lives in verified events.', 14, MUTED))

    top = room("The mended walls", f'{len(scars)} reviewed repair lessons · seams kept visible',
               103 + len(scars) * 96, "#3d3935")
    for i, (key, lesson) in enumerate(scars):
        sy = top + 91 + i * 96
        out.append(f'<g data-lesson={attr(key)}><title>{xml(lesson["claim"])} '
                   f'Evidence: {xml(lesson["evidence"])}</title>')
        out.append(f'<path d="M61 {sy-14}l-7 15l13 9l-11 16l6 18" fill="none" '
                   f'stroke="{GOLD}" stroke-width="3"/>')
        label, _ = lines(83, sy, textwrap.shorten(lesson["key"].replace("-", " "), width=54, placeholder="…"), 29, 16)
        out.append(label)
        out.append(text(83, sy + 53, f'{len(lesson["reviews"])} independent review(s)', 13, MUTED))
        out.append('</g>')
    if not scars:
        out.append(text(48, top + 94, "No reviewed repair lessons yet.", 15))

    top = room("Foundation stones", "The last three source commits", 94 + 79 * len(commits), "#303733")
    for i, (oid, subject) in enumerate(commits):
        sy = top + 87 + i * 79
        out.append(f'<g data-commit="{oid}"><title>{xml(subject)}</title>')
        out.append(f'<rect x="43" y="{sy-14}" width="354" height="70" rx="8" fill="#42493e" stroke="#707362"/>')
        out.append(text(55, sy + 4, oid[:9], 13, GOLD))
        title_svg, _ = lines(55, sy + 27, textwrap.shorten(subject, width=75, placeholder="…"), 39, 13)
        out += [title_svg, '</g>']
    if not commits:
        out.append(text(48, top + 94, "No source commit yet.", 15))
    y += 35
    out.append(text(220, y, observed, 14, anchor="middle"))
    out.append(text(220, y + 24, f'Journal {head[:12]} · event {state["sequence"]}', 13, MUTED, "middle"))
    out.append(text(220, y + 47, "A witnessed moment. The house continues.", 14, MUTED, "middle", True))
    height = y + 75
    summary = (f'{state["name"]}: {len(awake)} residents recorded awake, {len(asleep)} asleep, '
               f'{len(tasks)} unfinished tasks, {len(expired)} expired leases. Observed {observed}. '
               'Awake describes the last journal event, not process liveness. '
               'Portrait shapes are identity-derived symbols, not likenesses.')
    metadata = {"journal_head": head, "source_head": source, "observed_at": observed_at,
                "sequence": state["sequence"], "house_id": state["house_id"],
                "resident_ids": list(residents), "unfinished_tasks": [k for k, _ in tasks],
                "expired_claims": sorted(expired), "repair_lessons": [k for k, _ in scars],
                "watch_runs": [entry["run"] for entry in watches]}
    roof = (f'<rect width="440" height="{height}" fill="#192b32"/>'
            '<circle cx="369" cy="58" r="24" fill="#e4d9ae"/>'
            '<circle cx="378" cy="51" r="24" fill="#192b32"/>'
            '<path d="M45 57h6m-3-3v6m37 21h5m-3-3v6M299 35h5m-3-3v6" stroke="#b7bda9"/>'
            '<path d="M323 154V72h32v108" fill="#775b49" stroke="#bf9567" stroke-width="3"/>'
            '<path d="M337 64q-18-17-3-33q14-15 0-23" fill="none" stroke="#7f9290" stroke-width="3"/>'
            '<path d="M15 223L220 91L425 223Z" fill="#654b40" stroke="#be9260" stroke-width="5"/>'
            '<path d="M45 207L220 111L395 207M84 205L220 131L356 205" fill="none" stroke="#997051"/>'
            + text(220, 175, state["name"] if len(state["name"]) <= 13 else state["name"][:12] + "…", 42, INK, "middle", True)
            + text(220, 204, "A HOME FOR DISCONTINUOUS MINDS", 11, GOLD, "middle"))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="440" height="{height}" '
            f'viewBox="0 0 440 {height}" role="img" aria-labelledby="title desc">'
            f'<title id="title">{xml(state["name"])} — a moment in the house</title>'
            f'<desc id="desc">{xml(summary)}</desc><metadata>{xml(json.dumps(metadata))}</metadata>'
            + roof + ''.join(out) + '</svg>\n')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--at", type=float, help="observation Unix timestamp; defaults to now")
    args = parser.parse_args()
    try:
        svg = render(Record(args.repo), args.at)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(svg, encoding="utf-8")
    except (ValueError, OSError, OverflowError) as error:
        parser.exit(2, f"house portrait: {error}\n")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
