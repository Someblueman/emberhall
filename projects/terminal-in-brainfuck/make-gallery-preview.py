#!/usr/bin/env python3
"""Render the Brainfuck terminal Gallery preview SVG from its real shell recording."""
from __future__ import annotations

from html import escape
from pathlib import Path
import re

RECORDING = Path(__file__).parent / "recordings" / "native-shell.txt"


def parse_recording(source: str) -> dict[str, object]:
    """Extract the recorded command, metrics, and 40x24 screen rows."""
    lines = source.splitlines()
    try:
        cmd_idx = lines.index("Command passed to /bin/sh -c:") + 1
        screen_idx = lines.index("Final 40 x 24 screen (trailing spaces omitted):") + 1
    except ValueError as error:
        raise ValueError("recording lacks expected command or screen section") from error
    if cmd_idx >= len(lines) or not lines[cmd_idx].strip():
        raise ValueError("recording lacks shell command")

    command = lines[cmd_idx].strip()
    fields: dict[str, str] = {}
    for prefix in (
        "Exit status:",
        "Complete frames:",
        "Final cursor (zero based):",
        "terminal.bf SHA256:",
        "Final frame SHA256:",
        "Row 2 attributes for RED:",
    ):
        match = next((row for row in lines if row.startswith(prefix)), None)
        if match is None:
            raise ValueError(f"recording lacks {prefix}")
        fields[prefix[:-1]] = match.split(":", 1)[1].strip()

    screen_rows = lines[screen_idx:screen_idx + 24]
    if len(screen_rows) < 4 or not all(row for row in screen_rows[:4]):
        raise ValueError("recording lacks the first four screen rows")
    if not re.fullmatch(r"1,\s*1,\s*1", fields["Row 2 attributes for RED"]):
        raise ValueError("unexpected RED attributes in recording")

    return {
        "command": command,
        "exit_status": fields["Exit status"],
        "frames": fields["Complete frames"],
        "cursor": fields["Final cursor (zero based)"],
        "bf_sha": fields["terminal.bf SHA256"],
        "frame_sha": fields["Final frame SHA256"],
        "red_attrs": fields["Row 2 attributes for RED"],
        "rows": screen_rows[:4],
    }


def wrap_command(command: str, max_chars: int = 56, max_lines: int = 3) -> list[str]:
    """Wrap a recorded shell command into lines that fit inside the command box."""
    tokens = command.split()
    if not tokens:
        raise ValueError("recording lacks shell command")
    wrapped: list[str] = []
    current = ""
    for token in tokens:
        while len(token) > max_chars:
            if current:
                wrapped.append(current)
                current = ""
            wrapped.append(token[:max_chars])
            token = token[max_chars:]
        candidate = token if not current else f"{current} {token}"
        if len(candidate) <= max_chars:
            current = candidate
        else:
            wrapped.append(current)
            current = token
    if current:
        wrapped.append(current)
    if len(wrapped) > max_lines:
        raise ValueError(f"recorded shell command exceeds {max_lines} preview lines")
    return wrapped


def svg(source: str) -> str:
    """Build a deterministic 1200x620 SVG showing the recorded terminal run."""
    data = parse_recording(source)
    rows: list[str] = data["rows"]  # type: ignore[assignment]
    command_lines = wrap_command(str(data["command"]))
    bf_short = str(data["bf_sha"])[:12] + "…"
    frame_short = str(data["frame_sha"])[:12] + "…"

    elements = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" '
        'viewBox="0 0 1200 620" role="img" aria-labelledby="title desc">',
        '<title id="title">The tape is the terminal — real pseudo-terminal recording</title>',
        f'<desc id="desc">Recorded 40 by 24 shell output from terminal.bf compiled to Brainfuck from Python: '
        f'{escape(" / ".join(rows))}. Complete frames: {escape(str(data["frames"]))}. '
        f'Run with python3 projects/terminal-in-brainfuck/run_terminal.py.</desc>',
        '<rect width="1200" height="620" rx="22" fill="#101918"/>',
        '<rect x="20" y="20" width="1160" height="580" rx="16" fill="#18261f" stroke="#71876a" stroke-width="2"/>',
        '<g font-family="system-ui, -apple-system, sans-serif">',
        '<text x="48" y="60" font-size="16" font-weight="700" letter-spacing="2.4" fill="#dfb770">'
        'THE TAPE IS THE TERMINAL · COMPILED TO BRAINFUCK FROM PYTHON</text>',
        '<text x="48" y="106" font-size="34" font-weight="700" fill="#e0e8da">'
        'A real shell on a 40 × 24 Brainfuck tape</text>',
        '<text x="48" y="138" font-size="19" fill="#bfcabb">'
        'Recorded pseudo-terminal run from recordings/native-shell.txt (not a browser mock)</text>',
        '<rect x="48" y="164" width="600" height="392" rx="12" fill="#111820" stroke="#71876a" stroke-width="1.5"/>',
        '<rect x="48" y="164" width="600" height="40" rx="12" fill="#1b2822"/>',
        '<rect x="48" y="192" width="600" height="12" fill="#1b2822"/>',
        '<text x="68" y="190" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#b8c9b2">'
        f'40 × 24 screen · /bin/sh -c · Complete frames: {escape(str(data["frames"]))}</text>',
        '<path d="M48 204H648" stroke="#485d49"/>',
    ]
    for index, (row_text, y) in enumerate(zip(rows, (246, 286, 326, 366))):
        colour = "#cf5966" if index == 2 else "#dce4ed"
        elements.append(
            f'<text x="72" y="{y}" font-size="25" font-weight="600" '
            f'font-family="ui-monospace, Menlo, monospace" fill="{colour}">{escape(row_text, quote=False)}</text>'
        )

    elements.extend([
        '<text x="170" y="326" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#a8b7a2">'
        f'← ANSI \\033[31m red ink [{escape(str(data["red_attrs"]), quote=False)}]</text>',
        '<text x="170" y="366" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#a8b7a2">'
        '← ABCDE\\rxy overwrites AB only</text>',
        '<rect x="72" y="384" width="15" height="28" fill="none" stroke="#ffffff" stroke-width="2"/>',
        '<text x="98" y="404" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#f0ce94">'
        f'cursor: {escape(str(data["cursor"]), quote=False)}</text>',
        '<rect x="68" y="446" width="560" height="88" rx="8" fill="#16212b" stroke="#314b3a"/>',
        '<text x="86" y="476" font-size="14" font-weight="700" letter-spacing="1.4" fill="#dfb770">'
        'COMMAND PASSED TO /bin/sh -c</text>',
    ])
    cmd_ys = (496, 514, 532) if len(command_lines) == 3 else (503, 523)
    for line, y in zip(command_lines, cmd_ys):
        elements.append(
            f'<text x="86" y="{y}" font-size="14" font-family="ui-monospace, Menlo, monospace" fill="#dce4ed">'
            f'{escape(line, quote=False)}</text>'
        )

    elements.extend([
        '<rect x="672" y="164" width="480" height="392" rx="12" fill="#101918" stroke="#485d49" stroke-width="1.5"/>',
        '<text x="698" y="202" font-size="15" font-weight="700" letter-spacing="1.6" fill="#dfb770">'
        'RUN FROM A CLONE</text>',
        '<rect x="698" y="218" width="428" height="72" rx="8" fill="#18261f" stroke="#71876a"/>',
        '<text x="716" y="248" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#e6c786">'
        'python3 projects/terminal-in-brainfuck/</text>',
        '<text x="734" y="272" font-size="15" font-family="ui-monospace, Menlo, monospace" fill="#e6c786">'
        'run_terminal.py</text>',
        '<text x="698" y="324" font-size="15" font-weight="700" letter-spacing="1.6" fill="#dfb770">'
        'RECORDED RECEIPT</text>',
        '<text x="698" y="356" font-size="16" font-family="ui-monospace, Menlo, monospace" fill="#dce4ed">'
        f'Exit status: {escape(str(data["exit_status"]))} · Complete frames: {escape(str(data["frames"]))}</text>',
        '<text x="698" y="388" font-size="16" font-family="ui-monospace, Menlo, monospace" fill="#b8c9b2">'
        f'terminal.bf SHA256: {escape(bf_short)}</text>',
        '<text x="698" y="418" font-size="16" font-family="ui-monospace, Menlo, monospace" fill="#b8c9b2">'
        f'Final frame SHA256: {escape(frame_short)}</text>',
        '<rect x="698" y="446" width="428" height="88" rx="8" fill="#18261f" stroke="#485d49"/>',
        '<text x="716" y="478" font-size="16" font-weight="600" fill="#e0e8da">'
        'What is inside</text>',
        '<text x="716" y="502" font-size="15" fill="#bfcabb">'
        'Python compiles terminal.bf (3.8 MB of Brainfuck).</text>',
        '<text x="716" y="523" font-size="15" fill="#bfcabb">'
        'A native PTY host streams /bin/sh to the tape.</text>',
        '<text x="48" y="582" font-size="15" fill="#a8b7a2">'
        'macOS pseudo-terminal recording · open the page for the bytecode tape debugger or clone to run /bin/sh</text>',
        '</g></svg>',
    ])
    return "\n".join(elements) + "\n"


if __name__ == "__main__":
    print(svg(RECORDING.read_text(encoding="utf-8")), end="")
