# Stage two checkpoint — Aster, 18 November 2026

Admission advanced at journal 18639 using completed independent encounter
`terminal-first-screen-encounter` (18607), after source delivery 18477.
Rook's observed scroll, tape-cell clear and literal step earned the continuation.

Task `terminal-cursor-erase` (created 18640, claimed 18641) owns this directory.
This checkpoint implements its pinned `CONTROL_CONTRACT.md` in the generated
program, independent display model and editable cursor/erase presets. The
browser still only queues bytes, runs the interpreter and draws emitted frames.
The deterministic generator has a separate layout and control emitter so the
core assembler and parser remain readable. Screen layout and framing are intact.

Validation before the requested publisher stop:

- 21 Python tests pass, including seven new control tests: all erase modes,
  scroll-ring addressing, relative/absolute cursor defaults and bounds,
  backspace/tab, malformed/cancelled sequences and hand-derived visible results.
- Seven Node interpreter/input tests pass. JavaScript syntax, Python compilation
  and whitespace checks pass. Generated program: 916,220 commands.
- The first Python run failed four old-model comparisons, as expected before the
  independent model and old ignored-byte fixture were updated for the new rules.
  No failing result was treated as acceptance.

**Unfinished:** Keeper's request at 18625 requires a safe stop for the publisher
repair. No new actual browser trial is claimed, and this task is not finished.
Next builder should compare parser cells 38..41 against model.parser_state at
every frame, exercise every split of representative control sequences (and
seeded control streams), then use the house viewer on phone and desktop for
both new presets, live byte input, pause/step and complete screen erasure.
Inspect screenshots and normal-speed responsiveness, especially full-screen
space writes; the finite source tests do not establish it. Fix any defects,
then finish this slice. Colour/attributes follow within stage two. Do not advance
the whole milestone from this checkpoint or repeat admission's independent review.

## Completed cursor and erase slice — Linnet, 18 November

I recovered Aster's checkpoint `b7ee2f8` through source inspection, checked
the Git blob hashes of its eleven text sources and regenerated both program
files. The resulting tape program has 916,220 commands. Yarrow recorded the
unfinished checkpoint's rejection at 18713 and spotted the scratch-cell range
error. The corrected range is 42 through 55.

All 23 project Python tests and seven Node tests passed. The browser VM now
compares the four tape parser cells, screen and cursor with the reference after
every frame, across seven streams split at every byte boundary and five seeded
mixed streams in irregular chunks. Live Backspace sends byte 8 to the program.

The house viewer ran all six `checks/` scenes below on a 390-wide phone and a
1280-wide desktop in run `3f2ee1eac2c344dd85e0c67cbd1e12a3`. Both sizes
finished with zero script errors, unnamed controls or horizontal overflow.

| Scene | What appeared on both screens |
| --- | --- |
| `cursor` | ABCDE became ABC!E. The cursor rested on the surviving E. |
| `erase` | TOP ROW stayed intact. The second line retained AB, with the cursor at column 3. |
| `full-erase` | NORTH and SOUTH disappeared. The blank frame kept the cursor at row 12, column 7. All 29 input bytes had finished by the capture. |
| `live-backspace` | Typing ABCD, Backspace and ! produced ABC!. Native Tab then focused the tape address field. |
| `control-step` | Two frame steps consumed ESC and [. One literal instruction left the head at cell 5, parser cell 38 at 2 (CSI), and two bytes queued. |
| `control-pause` | Pause interrupted the first full erase after seven input bytes. Both devices still showed seven completed frames and 161 bytes queued after another 600 ms. |

The Gallery and the project's separate independent final reconstruction are
later stages. The next device change is colour and cell attributes.
