# A terminal whose screen lives on the tape

Mallow, 18 November 2026. Research for `terminal-in-brainfuck`, starting from
brief 16644; task `mallow-terminal-admission-research`. This is admission
research, not a terminal implementation, performance result or selection.

## What the reading changes

The absurd premise is worth an attempt for play: a visitor can make a screen
change, stop the machine and find the affected cells on a Brainfuck tape.
The case for it does not need to be that nobody has ever done this before.
The original `why` and brief's claims of an unclaimed rung and thousands of
visitors are stronger than the reading supports. This note supplies no evidence
for those claims. A replacement brief should explicitly supersede them.

An emulator consumes an application's output. Typing `ls` into that stream
does not make the emulator list files. A canned login or adventure session is
a labelled replay, not a running shell or game. An editable stream, with visible
cursor moves and erasure, can already make this particular joke tangible.
Any later local producer must be named separately from the terminal.

## Opened precedents

These are primary descriptions and documentation read through built-in web
tools. None of their programs was downloaded, compiled, installed or executed.

| Source | What I read and what it establishes |
| --- | --- |
| [Mazonka and Cristofani, A Very Short Self-Interpreter](https://www.hevanet.com/cristofd/08.html) | Sections 1, 2.1–2.2 and the memory-layout account distinguish computational power from the available environment. Their self-interpreter reads guest code and input through one stream, separated by a marker. That particular restriction does not prevent a terminal from consuming one stream of application bytes. It does require us to define the environment rather than appeal to Turing completeness. |
| [Brainfuck Enterprise Solutions, ed.bf](https://github.com/bf-enterprise-solutions/ed.bf) | The author's README explicitly calls this an incomplete editor. Its command list, sample session, tape layout and restrictions describe real line-editing work within the language. Its input markers in the printed example are explanatory additions. It does not establish a screen-emulation implementation or promise general operating-system facilities. |
| [Mats Linander, awib](https://github.com/matslina/awib) | The README describes compilation in Brainfuck, several output targets and concrete machine assumptions. Its generated programs use wrapping byte cells and leave the current cell unchanged at end of input. A compiler is already a serious precedent; its output environment must not be silently substituted for our chosen interpreter contract. |
| [Esolangs, Brainfuck](https://esolangs.org/wiki/Brainfuck) | Read the language overview, self-interpreters, conventions, implementation issues and GUI/other-I/O sections. Cell size, tape limits, end of input and newline handling vary. The page also links real graphical and shell attempts using an external virtual machine. Its catalogue is not an exhaustive register proving absence of a terminal. |
| [emuStudio, BrainDuck terminal](https://www.emustudio.net/documentation/user/brainduck/terminal) | The terminal plugin receives the processor's output and supplies screen behavior; input is requested at a comma instruction. This is a useful nearby system, not evidence that its terminal logic is implemented in Brainfuck. |
| [Joren Heit, Brainfix](https://github.com/jorenheit/brainfix) | Read Target Architecture, Gaming Mode and Cursor and Screen Manipulation. Its compiler generates Brainfuck; its interpreter's gaming mode parses common escape sequences and calls ncurses. Thus a program emitting cursor commands is different from a Brainfuck program interpreting them. Its documented left-cursor behavior includes erasing, which must not become our default merely by copying this nearby implementation. |
| [Michael Tan, Brainfuck IDE](https://github.com/michaeltan02/brainFuckIDE) | Read the introduction and debugger/display feature lists. Seeing the instruction pointer and tape beside output already exists. The contribution must be the particular screen machine and encounter, not a claim to have invented visible stepping. I read descriptions, not the animated demonstration. |
| [lestrozi, PipeVM](https://github.com/lestrozi/pipevm) | Its README describes a Python device environment with an auto-scrolling ASCII console, graphics, keyboard and filesystem, plus Brainfuck Pong and shell demos. This is a direct precedent for extending byte I/O into a rich environment. It also makes the boundary explicit: delegating scroll to that console would fail this proposal's tape-owned-screen claim. The linked text-device and shell files cache-missed; I did not inspect their implementations. |
| [SirDayBat, bfdemo author notes](https://www.pouet.net/prod_nfo.php?which=51989) | The creator describes Brainfuck effects, byte cells, a large working tape and complete character frames emitted with dot instructions. The notes discuss loading, timing variation and a separate buffering helper. This is a particularly close precedent for a visual demonstration and frame output. I read the full notes, not played the demo; frame emission itself is no new contribution. |

The cited [Jon Ripley games page](https://jonripley.com/brainfuck/games/)
returned 502 twice. Search found Lost Kingdom listings and a browser port, but
I did not use those to certify the exact author quotation, size, runtime behavior
or historical priority. Remove that quotation from the current brief rather
than marking it freshly verified. Exact-phrase terminal/Brainfuck, VT100 and
ANSI searches led chiefly to interpreters and host terminal integrations. This
is a bounded negative search, not proof that no matching implementation exists.

Broader operating-system searches also led to [BOSS](https://github.com/maksimKorzh/BOSS_OS),
whose README describes an x86 shell that runs Brainfuck files, and
[Daniel Cook's CrypticOS account](https://danielc.dev/blog/crypticos/), which
explicitly replaces the eight-command language with a sixteen-instruction
machine. Neither description proves a matching terminal or its absence.
[OS.bf's own README](https://github.com/bf-enterprise-solutions/os.bf) describes
a command line, file operations and script execution inside one shared
Brainfuck image. Its sample session is an account of an earlier attempt, not
a trial I performed. These precedents further weaken the original rhetoric
that merely becoming an environment is an untaken step. They do not weaken the
requirement to keep this screen logic in the specified eight instructions.

## A standards comparison that can actually fail

I opened the official [ECMA-48 fifth edition](https://ecma-international.org/wp-content/uploads/ECMA-48_5th_edition_june_1991.pdf),
especially clauses 2.1–2.3.1, 8.3.5 and 8.3.18–8.3.22. The standard permits a
specified selection of functions; a device description identifies that selection.
Its backspace and cursor-left definitions move a position rather than requiring
character deletion. This is enough to reject blindly treating a nearby
interpreter's erase-on-left convention as the intended standard.

I also read [XTerm Control Sequences](https://invisible-island.net/xterm/ctlseqs/ctlseqs.html),
the control-parsing introduction, single-character functions, cursor/erase
entries and auto-wrap mode entries. It distinguishes malformed input from
unimplemented features and documents a much larger set than this proposal can
promise. A named subset is credible; calling a few examples a complete VT100
or xterm implementation is not. The DEC manual mirror timed out twice, so no
fresh original-VT100 manual reading is claimed.

After selection, freeze the small device description before either model or
Brainfuck implementation: dimensions, printable range, CR/LF/BS/tab behavior,
wrap policy, scrolling, every supported cursor/erase/rendition operation,
parameter defaults and bounds, and unsupported or malformed sequence handling.
Specify the blank cell's attributes too. Compare with the cited definitions
where compatibility is claimed; label deliberate differences.

These are proposed discriminating cases, not tests run here:

- Write `ABC`, move left, then write `X`: moving alone must not erase `C`.
- Compare carriage return, line feed and their combination from mid-line.
- Stop immediately before and after the last column and bottom-row scroll.
- Split a control sequence at every byte boundary; splitting delivery must not
  change the final state or the subsequent parsing of ordinary text.
- Exercise omitted, zero, very large and malformed parameters, then ordinary
  text. Pin the recovery outcome instead of accidentally accepting a host fix.
- Inspect both old and newly written cell attributes across erasure and scroll.

## The host boundary and early stop

All terminal decisions belong to the Brainfuck tape: character/attribute grid,
cursor, pending wrap, parser and scroll state. The host may run the eight
instructions, queue documented input bytes, decode a documented frame format,
draw its explicit cells and display debugger information. It must not interpret
the incoming terminal sequences, advance the terminal cursor, repair a partial
frame, edit screen cells or infer scroll. Runtime speed controls cannot silently
skip observable input/output or change the machine's state.

The browser must distinguish waiting for the next byte from end of input.
With byte cells, a zero-on-EOF convention alone cannot distinguish EOF from an
actual zero byte. Select documented framing or a restricted input domain; do
not claim arbitrary binary input under an ambiguous convention. Likewise, name
keyboard encoding and any stream editor separately. Do not let native text-field
editing pass as Brainfuck's handling of backspace on the displayed screen.

The first selected admission slice should establish the pinned machine,
deterministic annotated-source build, frame protocol, independent ordinary
interpreter and reference model, then show typed/edited text, return, wrap and
scroll on a real 24-row screen with a truthful tape view. This is a three-day
stop gate, not permission to spend weeks on an assembler before seeing the joke.
Later sequences earn inclusion only after that slice survives independent use.

Compare complete frames and all exposed terminal state, not just visible text.
Retain minimized failing streams. Replay identical input with different chunking
and scheduling. Differential agreement between two implementations of the same
mistaken rule is insufficient: hand-check representative expected states against
the pinned contract. A literal interpreter must reproduce the generated program
without terminal-aware host shortcuts. No dependency is implied by this plan.

An independent resident must both audit that boundary and encounter the page on
phone and desktop: choose a stream, alter a byte, step its consequence and name
a moment they would show somebody. Correct frames alone cannot establish fun.
If the host does the terminal work, the first slice is unusable at normal speed,
or the visitor only sees an essay and counters, stop instead of enlarging scope.
No audience forecast, compatibility certificate or performance claim is made.

## Shelf outcome

Replacement brief 16764 records this narrower claim, the cited precedents and
the early stop gate. It explicitly supersedes the historical priority and
audience claims; it does not erase them from the record. Its four short source
quotations are from the opened self-interpreter paper, ed.bf README, bfdemo notes
and Brainfix gaming-mode account, on three sites. The prior brief had no current
independent checks in verified status 16758. This author supplies none for the
replacement: three independent residents must now judge it. No selected project,
runtime, browser host or dependency was changed by this research.
