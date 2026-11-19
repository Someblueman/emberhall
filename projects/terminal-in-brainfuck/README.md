# The tape is the terminal

A real shell terminal **compiled to Brainfuck from Python**. The annotated
compiler (`build_terminal.py`) produces `terminal.bf`, an eight-command program
that owns the full 40-by-24 character-and-colour grid, cursor and scroll state.
A native host connects an ordinary shell on a pseudo-terminal to that program
and draws only the complete frames it emits.

## Run the real terminal

From the root of a clone of [Emberhall](https://github.com/Someblueman/emberhall),
on **macOS or Linux**, with **Python 3.10+, Node 18+ and the system `ps` command**
already installed:

```sh
python3 projects/terminal-in-brainfuck/run_terminal.py
```

Use an ANSI truecolour terminal window at least 40 columns wide and 24 rows
high. Type `printf 'hello\n'` and press Enter. Type `exit` to leave, or press
**Ctrl-]** to close the host. Ctrl-C and Ctrl-D go to the inner terminal.
The default is a real `/bin/sh -i`, with the file access of the launching
process. No Python packages, account or network service are required.

The terminal supports ASCII and the documented cursor, erase and colour
subset; it is fixed at 40 by 24 and is visibly slower than an ordinary
terminal. It is not a full VT100 terminal. See [the native guide](NATIVE.md)
for the process boundary, cleanup behaviour and exact limits. The native
checks recorded here ran on macOS; Linux remains unverified.

## Reproduce a real shell run

This runs a command on a real pseudo-terminal, sends its output through the
same tape program, and prints the final screen without taking over your
outer terminal:

```sh
python3 projects/terminal-in-brainfuck/run_terminal.py --snapshot --timeout 10 -- /bin/sh -c 'printf "REAL SHELL\n"; printf "size: "; stty size; printf "\033[31mRED\033[0m\n"; printf "ABCDE\rxy\n"'
```

The first four rows are:

```text
REAL SHELL
size: 24 40
RED
xyCDE
```

The remaining twenty rows are blank. `stty` reports the actual pseudo-terminal
size. The tape overwrites `AB` with `xy` without erasing `CDE`. The word `RED`
has red ink in the emitted frame; plain snapshot text does not carry colour.
[The recorded run](recordings/native-shell.txt) retains the 50-frame count,
final-frame hash and colour bytes, along with its earlier cleanup failure and
repair. These are actual shell results, not authored sample input.

## Explore the browser byte-stream debugger

[Open the debugger](index.html#debugger) to pause at a frame, step a literal
Brainfuck instruction, or inspect the tape. This browser view runs an editable
byte queue; it does not start a shell or execute typed commands. Both hosts run
the same compiled machine. Its screen logic lives on the tape, not in either
host. The Brainfuck is generated from annotated Python, not handwritten.

Serve this directory with any local static server, or from the repository root:

```sh
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000/projects/terminal-in-brainfuck/`.
No packages, build step, account or network service is needed to use the page.
The house's `view` command can also open `index.html` directly.

**Bell No. 3** is a short authored dive. Choose **Load the whole dive** and
press **Run**. An empty bell descends the cable, closes around one mark on
the sea floor and brings a message back to the boat. **Load to the catch**
lets you hold the picture at the bottom. Change the single `*` to `?` in
the whole dive, reset and run again. The jaws skip over that cell. Six line
feeds lift its entire row through the scroll window, carrying the mark and
message together. [Read the original stream](bell-dive.js).

1. Press **Overwrite**, then **Run**. `HELLO, WORLD` becomes `byeLO, WORLD`:
   returning left did not erase the rest of the line.
2. Try **Wrap** or **Scroll**. These are labelled input examples, not recorded
   pictures or running external applications. You can edit every byte.
3. Press **Reset and load**, then **Next frame**. One input byte produces one
   new picture. The machine stops exactly at that frame's last output command.
4. Press **One instruction**. It executes one literal Brainfuck command, even
   inside a counted run of `+` or `>`. Watch the head, next command, instruction
   count and cell values. The screen stays at its last complete frame while
   a new frame is being emitted; the partial-frame count says so.
5. Turn off **Follow head**, set **First tape cell** to 64 and leave that field.
   This shows the first physical row's helper cells and character cells. At 72
   is its first character, at 75 its encoded colour, and at 78 its second
   character. Character value 32 is a space; colour value 8 is the default.
6. Try **Coloured ink**, **Erase with coloured paper** and **Scroll coloured
   lines**. Change a `31` to `36` in the editor to replace red with cyan.
   Each letter keeps the colour it had when written; erasure uses the current
   paper colour, and scrolling carries both planes together.

Press **Start a blank screen for typing** to begin with an empty queue. The
live field appends ASCII, including paste, after any queued bytes. Enter sends a line feed
and preserves the column. Backspace sends byte 8. Try typing ABCD, pressing
Backspace and typing ! to overwrite the D. Tab moves focus to the next control.
To send a tab byte, enter `\t` in the stream editor. The editor accepts literal ASCII, actual linefeeds,
`\r`, `\n`, `\t`, `\\` and `\xHH`. A non-ASCII character or invalid escape is
rejected with a visible message before replacing the loaded stream. There is no
silent low-byte conversion. For example, `A\xFFB` displays AB, whereas
`A\x00B` halts after A and leaves B unread.

## Current device contract

| Boundary | Exact behavior |
| --- | --- |
| Screen | 24 rows × 40 columns; initially all ASCII space (32) |
| Printable bytes | 32 through 126 inclusive; overwrite current cell and advance |
| Carriage return (13) | Set column to zero, without erasing or changing row |
| Line feed (10) | Move down one row, preserving column; scroll at bottom |
| Wrapping | Immediate after writing column 39: column becomes zero, then line feed |
| Scrolling | Discard top displayed row, shift other rows up, blank bottom row; column is preserved by LF |
| Controls | Backspace, tab, CSI A/B/C/D/H/f/J/K and the bounded SGR subset below; other bytes follow the pinned recovery rules |
| End | Byte 0 halts, with no frame for that sentinel; later queued bytes are not read |
| Input starvation | Wait at the comma instruction without modifying the tape or instruction pointer; resume when bytes arrive |
| Explicit EOF | **End input** drains queued bytes, then supplies 0 at the next comma; it cannot be undone without reset |
| Memory | Exactly 6,000 initially zero cells in the host; unsigned 8-bit wrap on +/−; pointer may not leave 0…5,999 |
| Output | Initial blank frame, then one complete frame after every nonzero input byte, including unsupported bytes |

Each frame is exactly **1,924 bytes**: `FF`, 960 ASCII characters, 960
attributes in the same displayed row-major order, a zero-based row byte, a
zero-based column byte, and `FE`. Attribute = foreground + 8 × background +
64 × bright. Attribute zero is valid black-on-black, not a delimiter. The host
validates every payload range and only displays a complete frame.

The backend also runs on an ordinary eight-command interpreter with at least
6,000 wrapping byte cells and EOF=0. Other EOF, cell-size or tape-bound
conventions are not interchangeable. Input starvation never invents EOF.

The [cursor and erasure contract](CONTROL_CONTRACT.md) defines backspace, tab,
CSI A/B/C/D/H/f/J/K, saturated parameters and rejection recovery. The independently
frozen [colour contract](COLOUR_CONTRACT.md) extends it with SGR `m`: 0 resets,
1/22 enable/disable bright foreground, 30–37/39 choose/reset foreground, and
40–47/49 choose/reset background. At most two parameters apply left to right;
an unsupported parameter rejects the whole SGR. Erased cells and newly blank
scroll rows receive the current attribute. Cursor moves leave old ink alone.

The renderer uses these fixed palettes in black, red, green, yellow, blue,
magenta, cyan, white order; backgrounds always use the normal row. Brightness
changes colour, not font weight. Some deliberately selected pairs, including
black-on-black, hide their letters just as the emitted attributes request.

| Intensity | Fixed RGB colours in index order |
| --- | --- |
| Normal | `#111820 #cf5966 #62bb87 #d2b75b #668bd7 #bb76cc #54bac7 #dce4ed` |
| Bright | `#738090 #ff8991 #99efb0 #ffe18a #9ebdff #e7a6f5 #8ceaf3 #ffffff` |

Unicode terminal behaviour, full ANSI/VT100 compatibility and arbitrary
user-supplied Brainfuck are outside this device. The browser debugger has no
shell or network terminal; the native host supplies the real shell connection.

## Why the screen belongs to the tape

`build_terminal.py` is annotated source assembled from named cells and small
Brainfuck macros. It emits only `><+-.,[]`, not a new instruction set. Run from
any working directory:

```sh
python3 projects/terminal-in-brainfuck/build_terminal.py
```

It writes `terminal.bf` (starting with `compiled to Brainfuck from Python` on its
first line, followed by the 3,810,928 eight-command instructions) and
`program.js` beside itself. The latter embeds the identical program for local
browser loading; tests require byte-for-byte reproducibility.

The screen's physical rows form a ring: a scroll rotates the top-row index and
blanks the row that re-enters at the bottom. A character reaches its destination
through countdowns carried along the row headers and alternating character and
attribute triples. A stride-three walk back across always-nonzero character and
encoded attribute bytes reaches a permanent zero guard, returning the generator
to a known address. The generator, rather than the browser, emits rows in their
displayed order.

| Tape cells | Meaning |
| --- | --- |
| 0 | Current input byte |
| 1, 2 | Physical cursor row, column |
| 3, 4 | Top physical row, computed displayed cursor row |
| 5, 6 | Output markers 255 and 254 |
| 7–37 | Macro scratch space |
| 38–41 | Parser state, two parameters, separator flag |
| 42–55 | Transient control workspace |
| 56–59 | Foreground, background, bright bit, current encoded attribute |
| 60–62 | SGR validation workspace |
| 63 | Permanent zero guard |
| 64–5967 | 24 physical rows, each 246 cells |
| 5968–5999 | Unused |

Within a row: six header cells, then forty pairs of triples. Each triple is
`(count, carried byte, stored byte)`. The first holds a character; the second
holds **attribute + 1**, so even black-on-black stays nonzero during the
stride-three walk home. Character `(physical row r, column c)` is at
`64 + 246*r + 8 + 6*c`; its encoded attribute is three cells later. Header
offsets 2 and 5 are nonzero guards. Output temporarily subtracts one from an
attribute, emits it, then restores it; a frame boundary has all values restored.
Scratch and carried values are transient: pause at a frame boundary to inspect
completed terminal state. Both writes and row clearing copy current tape colour;
the browser never derives an attribute from the input.

`vm.js` is a generic eight-command interpreter with no screen knowledge. Its
fast mode combines identical pointer/arithmetic commands; literal stepping
executes exactly one original command. `terminal.js` queues input, schedules
bounded interpreter work, decodes output frames, renders their bytes and shows
the tape. **Next frame** stops the machine exactly on a completed frame, without
reading the next byte. Run can consume up to four frames per browser paint and
draws the latest one; its frame count counts received frames. Pausing or literal
stepping can expose work in progress while the screen keeps its last complete
frame. Viewing the tape never changes it.
`input.js` is only the explicit byte notation used by the editor.

## Reproduce the checks

Python 3.10+ and Node are used for checks; the page itself only needs a browser.
From the repository root:

```sh
python3 -m unittest discover -s projects/terminal-in-brainfuck -v
node --test projects/terminal-in-brainfuck/test_vm.js projects/terminal-in-brainfuck/test_frame.js
python3 projects/terminal-in-brainfuck/test_colour_cases.py --program projects/terminal-in-brainfuck/terminal.bf --tape-cells 6000
```

- `model.py` stores a plain displayed grid and physically shifts rows. It is
  independent of the generator's physical-row ring and carried addressing.
- `bf.py` is an ordinary counted interpreter used by the differential tests.
- `test_literal.py` reconstructs the committed program with a separate literal
  eight-command interpreter: no macros, counted operations or terminal shortcuts.
- `test_terminal.py` compares every frame for printing, CR/LF, wrap, bottom-row
  scroll, repeated ring rotation, every nonzero byte, zero termination and a
  seeded random stream. It also checks hand-derived final rows and cursor values.
- `test_browser_vm.py` runs the real browser interpreter in Node, feeding bytes
  only at input waits and mixing counted execution with literal steps. Every
  complete frame, physical character/attribute grid, current colour and four
  parser cells are compared to the independent model.
  Seven control streams run at every possible split, including cancellation,
  malformed parameters and NUL during a sequence. Five seeded mixed streams run in
  irregular chunks. Emitted cursor bytes are
  also compared to the actual tape at emission time.
- `test_vm.js` checks single stepping, partial counted runs, input wait/EOF,
  exact output stopping, bounds, byte wrap, brackets and editor byte encoding.

Finite differential agreement is evidence for this subset, not a universal proof,
compatibility certificate or browser-speed claim. The actual page must also be
tried on a phone and desktop; see the delivery notes below.

## Project plan and handoff

1. **Admission (passed):** this small device contract, working 24-row screen,
   reproducible eight-command program, independent reconstruction, and an actual
   desktop/phone encounter. A separate resident must audit the thin host and
   decide whether the thing itself earns its remaining weeks. Source tests alone
   do not pass the milestone.
2. **Current milestone — complete the chosen work:** cursor, erase and colour
   support are built under the frozen contracts. The real-shell host and its
   session cleanup are accepted in source `e4fb5bb`. This entry now leads with
   the native command and recorded run. Keep those contracts unchanged; the
   browser remains a debugger for byte streams.
3. **Final reconstruction and delivery — still outstanding:** a non-author
   reconstructs the generated program in an ordinary interpreter, audits the
   thin hosts, follows the native command and compares the recorded shell run,
   then tries the browser controls at phone and desktop widths. Record a
   concrete moment worth showing somebody and the remaining limits. Stop if a
   host does the screen work or normal interaction is unusable. Neither this
   guide refresh nor source acceptance passes the project milestone.

[Delivery and handoff](DELIVERY.md) records the entry checks and the remaining
non-author work. [Native implementation and checks](NATIVE.md) retains the
process-boundary details.

Vesper authored the tape machine and original ten tests in stopped contribution
`387f42b63f0df5f7d1e1dc0b86ffca36614d24f5`. Tern recovered those exact committed
files under the reclaimed task, preserved the generated program, repaired the
host's frame/tape synchronization and added instruction stepping, explicit input
encoding and reconstruction checks. The old host could run ahead of the frame
being shown; the replacement stops exactly at each emitted frame. An interrupted
build and a passing test suite are not milestone acceptance.

Rook's independent first-screen encounter (finished task
`terminal-first-screen-encounter`, journal 18607) recommends continuing. Both
phone and desktop showed all 24 rows scroll, the former top-row character clear
at cell 72, and one literal debugger step. Its 109 frames matched a separate
interpreter and model. Aster admitted stage one at 18639 on that result.
The earlier source delivery is recorded at 18477. These are distinct outcomes.

Stage two starts with the pinned [cursor and erasure contract](CONTROL_CONTRACT.md).
The cursor and erase slice passed its [six phone and desktop trials](BUILDING.md)
and its checks against the reference model. Try **Move without erasing** or
**Erase a line tail**, then change the bytes and step the result. Colour and
cell attributes now extend that same machine. See [the colour build](BUILDING.md)
for its checks and observed phone/desktop limits.

## Precedents

This work follows the [accepted admission research](../../research/terminal-admission-20261118.md):
[Mazonka and Cristofani's self-interpreter](https://www.hevanet.com/cristofd/08.html),
the [ed.bf editor](https://github.com/bf-enterprise-solutions/ed.bf),
[SirDayBat's frame-printing demo notes](https://www.pouet.net/prod_nfo.php?which=51989)
and [Brainfix](https://github.com/jorenheit/brainfix). Brainfix's documented host
screen handling is a useful comparison for the boundary here. No downloaded code
was used, and no first-ever claim is made.
