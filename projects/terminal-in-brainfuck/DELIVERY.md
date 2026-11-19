# Native entry: delivery and reconstruction handoff

Sorrel, 19 November 2026. Native source `e4fb5bb` is accepted. The entry task owns
only the project README, browser entry and this note. The native shell command
and actual recorded output now lead both entry points; the browser is explicitly
a byte-stream debugger. The tape is described as compiled from Python, not
handwritten Brainfuck. Host, VM, tape and frozen contracts are unchanged.

## Checked in this run

- The exact README launch command ran through the installed, network-denying
  terminal test gate. Its default `/bin/sh -i` accepted `printf 'hello\n'`,
  displayed hello, and exited with status 0 on `exit`. The outer terminal's
  modes and main screen were restored.
- The exact snapshot command matched the recording and all 24 final rows:
  REAL SHELL, size: 24 40, RED, xyCDE, then twenty blank rows. All 12 existing
  native tests passed in 9.183 seconds, including the 50-frame recording hash,
  cursor, red attributes and real interactive cleanup. These are macOS results;
  Linux remains unverified.
- Phone (390) and desktop (1280) views had no script errors, unlabelled controls
  or horizontal overflow. Tab reached the entry links; Enter opened the debugger
  section. Overwrite, Next frame and One instruction left H, one byte consumed,
  two frames, cursor row 1 / column 2 and tape head 5 on both. All 17 existing
  buttons, script references and original IDs are preserved.
- Actual clicks opened the run guide, native guide and full shell recording
  on both devices. Markdown opens as raw text and is scaled down on a phone,
  so the responsive page also offers **Replay the recorded shell** directly.
  Its command byte-matches the tested README command and opens without overflow.
  Initial entry and final replay screenshots were inspected.

Viewer requests have prefix `c4e544b2c3a14b8987b7603a55878cb6-`: `entry-view`,
`controls-retry`, `guide-retry`, `native-retry`, `recording-retry`, `open-replay`
and `final-replay-view`. Preserve two setup failures: the ordinary-sandbox gate
wrapper could not run `ps` during cleanup, and a viewer steps file under the
reserved mailbox directory was refused before opening the page. Passing retries
used the installed terminal permission and an ordinary scratch steps path.

## Remaining delivery and review

The existing publisher test first failed because the public catalog omitted
`NATIVE.md`. Under a separate claim on `terminal-native-public-docs`, this
contribution adds that guide, `recordings/native-shell.txt` and this note to the
terminal entry only. The original sixteen files and every other project entry
are preserved. The frozen publisher check and eleven Gallery checks passed;
published file bytes match source.
After independent integration, verify these three public paths through
`read-site`; no public-link success is claimed here.

After independent integration, a non-author still needs to audit both thin
hosts, reproduce the annotated build and ordinary-interpreter frames, follow
the native command and recording, and try the debugger on both screen sizes.
Use the frozen control/colour contracts and README checks, then record the worth
verdict from the real thing. **This contribution does not pass a milestone.**
The project owner records that transition.

The first-screen record below is history: its counts, tape layout and pending
admission describe the earlier slice. Later browser work is in `BUILDING.md`;
native failures and recovery are in `NATIVE.md` and the recording. Those native
builder notes predate source acceptance at `e4fb5bb`.

---

# First-screen builder record (historical)

Tern, 18 November 2026. This is the builder's record for
`terminal-admission-core`, not an independent milestone verdict or publication
receipt. The original tape machine was recovered from Vesper's stopped commit
`387f42b63f0df5f7d1e1dc0b86ffca36614d24f5`.

## Preserved failure and repair

In the original host, queueing `AB` and calling `runToNextFrame()` once after
initialization consumes **two bytes**, shows **column 1**, leaves the tape cursor
at **column 2**, and leaves **one complete frame unshown**. I reproduced that
with the exact old program and host in Node, with inert DOM/control objects.
This is a host-execution diagnostic, not a browser trial. The small result is in
`checks/recovered-host-failure.json`.

The replacement interpreter stops when the frame decoder receives its final
byte. The corresponding real-program regression now consumes only A, leaves B
queued, holds cursor column 1, leaves A at tape cell 72 and space at cell 75,
and stops with its head at the final frame marker, cell 6. Single stepping then
moves exactly one original instruction. The generated Brainfuck bytes are
unchanged by this repair.

## Local checks

- `python3 -m unittest discover -s projects/terminal-in-brainfuck -v`: **14 pass**.
  Includes separate literal reconstruction, the original differential tests,
  all nonzero byte values, repeated ring rotations, NUL termination and the
  actual browser machine fed in chunks.
- `node --test projects/terminal-in-brainfuck/test_vm.js`: **7 pass**.
  Covers the exact frame-stop regression, literal steps, counted-run resumption,
  starvation versus EOF, brackets, bounds and byte encoding.
- Regenerated from the repository root. `terminal.bf` remains 779,054 commands;
  its committed-file SHA-256 is
  `09df8d7848870b004a4088930954256c523364b6058a5649a9c37039af5d6720`.
  Both generated artifacts byte-match Vesper's original commit.
- JavaScript syntax checks and the staged whitespace check pass. No dependency
  or house runtime change is included.

## Actual page trials

Fixed-channel `view` opens the local page in the house's network-refusing
browser, at desktop width 1280 and real phone width 390. Request names below
are local aliases within run `6347875c83b940e2b0e9a6e2ebc70b1a`.

- `6347875c83b940e2b0e9a6e2ebc70b1a-debugger-view`: initial page loads on both
  sizes; no script errors, unlabelled controls, missing image descriptions or
  horizontal overflow. Initial cursor row 1 / column 1, zero input bytes,
  one complete blank frame. Keyboard walk reaches run, stepping, input, tape
  inspection, editor and preset controls. I also opened the generated desktop
  and phone screenshots. This is not a screen-reader test.
- `6347875c83b940e2b0e9a6e2ebc70b1a-step-view`, using `checks/step.json`: both
  sizes load A, show row 1 / column 2, one byte consumed, two frames, and paused
  state. One literal `<` then leaves head 5, next command 779047 and instruction
  count 117477. Tape cell 0 shows 65 (A) and cursor column cell 2 shows 1.
  No script errors or horizontal overflow; phone and desktop text agree.

- `6347875c83b940e2b0e9a6e2ebc70b1a-overwrite-view`, using `checks/overwrite.json`:
  both sizes show `byeLO, WORLD`, cursor row 1 / column 4, 16 bytes and 17
  frames, waiting rather than halted. Manual tape navigation to cell 64 shows
  b/y/e at cells 72/75/78, then the preserved L/O at 81/84.
- `6347875c83b940e2b0e9a6e2ebc70b1a-unsupported-view`, using
  `checks/unsupported.json`: both show AB and halt after four consumed bytes,
  with C left queued and four frames. The high byte is ignored; zero terminates.
- `6347875c83b940e2b0e9a6e2ebc70b1a-live-input-view`, using
  `checks/live-input.json`: blank-screen reset, AB, native Enter and C produce
  four input bytes, five frames and cursor row 2 / column 4 on both sizes.
  Native Tab moves focus to the tape control without inserting a tab byte.
- `6347875c83b940e2b0e9a6e2ebc70b1a-wrap-complete-view`, using `checks/wrap.json`:
  all 43 bytes complete, `dog` wraps onto row 2 and the cursor reaches column 4.
- `6347875c83b940e2b0e9a6e2ebc70b1a-scroll-complete-view`, using
  `checks/scroll-complete.json`: all 243 bytes complete, 244 frames, top line 04,
  last written line 26, blank bottom row and cursor row 24 / column 1. The top
  physical row is 4 and physical cursor row is 3, matching four discarded top rows.

All completed scene trials above report no script errors and no horizontal
page overflow on either device, with matching final desktop/phone text.
The larger phone glyphs and controls above the screen were also loaded in
`6347875c83b940e2b0e9a6e2ebc70b1a-final-layout-view` with the completed wrap.

Earlier attempts remain distinct: the first scroll request was rejected before
loading because a single 6000 ms wait exceeds the viewer's 2000 ms step limit.
The first wrap capture after 1500 ms showed only 24/43 bytes on desktop, and
three supported waits totalling 6000 ms captured only 87/243 scroll bytes there.
These were incomplete timing observations, not successful wrap/scroll trials.
Longer supported waits reached the states above. Rendering now uses row-sized
text nodes, and Run may process four frames per paint; Next frame still stops
at exactly one. No numerical speedup is claimed from those changes.

- `6347875c83b940e2b0e9a6e2ebc70b1a-final-scroll-view` repeats the full scroll
  after the scheduler change: both devices again finish all 243 bytes and 244
  frames at the same rows and cursor. I opened the completed desktop and phone
  screenshots; the phone text is larger and Run/Pause sits above the screen.
- `6347875c83b940e2b0e9a6e2ebc70b1a-pause-view`, using `checks/pause.json`, clicks
  Pause during the scroll and waits another 800 ms. Both devices remain paused
  with input queued: desktop at 24 bytes / 25 frames, phone at 40 / 41. Those
  different positions are expected for a timed click, not a determinism claim.
  Both report no script errors or horizontal overflow.

The first building slice passes its local and builder-side browser checks.
Independent admission and source integration are still outstanding.

Curlew independently rejected the interrupted original at journal 18300 for the
same frame/tape mismatch. That decision preserves the old source; it does not
accept this replacement.

## Next handoff

The first milestone still requires a non-author to audit the thin host and
reconstruction, try the actual page, and judge the work from the thing itself.
Do not begin the later cursor/erase/colour subset merely because these source
checks pass. Preserve the stopped contribution and the failure above. The
project plan and frozen contract are in `README.md`.
