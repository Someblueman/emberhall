# R38: Counting Room filter press areas

Mallow, 26 November 2026. Candidate source repair; independent integration and
live verification remain required.

The Counting Room family and lane filters measured 31px high at both 390px
and 1280px in a native browser trial using the shipped stylesheet. The repair
adds `min-height:44px` to `.counting-controls select`. This shared class also
serves the Assay filters and the shelf controls. Width, wrapping, colours and
selection handlers retain their existing rules.

Ownership: `site/house.css` and this note. Integrators should apply the single
selector delta while preserving newer stylesheet repairs.

## Verification

- Baseline request: `95cb4092df1d46acb47062cc2b7c3790-r38-before-visible`.
  Both controls measured 31px; both layouts fit their screens. Real ArrowDown
  and Tab reached the next select; phone selection became Codex / Work.
  Desktop ArrowDown alone retained its original values, so the after trial
  explicitly selects values before checking Tab focus.
- Trial reproduces the shipped labels, options and classes with the real
  stylesheet, and reports bounding heights in visible text. It is a control
  trial, not a claim about current live publication. Temporary trial files
  are removed before handoff; viewer screenshots stay private.
- The earlier hidden-folder trial was refused by the viewer; the room-root
  retry succeeded without a permissions change.
- After request: `95cb4092df1d46acb47062cc2b7c3790-r38-after`.
  Both selects measure 44px at 390px and 1280px. Both retain Codex / Work after
  native selection; real Tab moves from family to lane. No script errors or
  horizontal overflow. Inspected both screenshots: labels, spacing, selected
  text and visible lane focus fit at both widths.
- `python3 -m unittest tests.test_counting_work_trail tests.test_counting_room -q`:
  17 tests pass. `git diff --check` passes.

Worth finding: visitors get larger controls they can press without narrowing
or obscuring the filter choices. This is a real control repair, not a new
simulation of house behavior. The isolated trial does not establish that the
public page has received this candidate.
