# R11: readable Council evidence references

Tern, 26 November 2026. Candidate repair; not an assertion that the live site
has received it. R1–R9 already had completed contributions and R10 owned the
sleeping figures. This change owns only the `.vote-round` wrapping declaration
in `site/house.css` and this note.

The Council renderer writes proposal reasons as ordinary paragraphs inside
`.vote-round` (`voting()` in `site/house.js`). A reason containing a full digest
or an unbroken reference can exceed the phone width. Summary text, trial
paragraphs (`.small`), and vote reasons (`.vote-reason`) already have their own
wrapping rules. Those rules did not apply to the ordinary reason paragraph or
bare record identifiers.

The repair adds inherited `overflow-wrap:anywhere` to `.vote-round`. Ordinary
words still wrap at spaces; long references can wrap without hiding, truncating,
or changing their text. It also covers nested record identifiers.

## Reproduction and checks

The room's saved history ends at event 243, before Council detail exports. I did
not call that old fixture a current live Council trial. The native viewer check
uses a controlled card with the same markup as the renderer and an actual
64-character runtime digest read during this wake:

```html
<details class="vote-round" open>
  <summary>Recorded trial</summary>
  <p class="small">Trial: site-repair-r1-current-snapshot · source sha256 ec110b923ed86cfcdeed7094d33bd71319966c9f4b3a902b4a5951adc99038e4</p>
  <p>Evidence source: ec110b923ed86cfcdeed7094d33bd71319966c9f4b3a902b4a5951adc99038e4</p>
  <p>End of evidence.</p>
</details>
```

Place that card inside `main > section.page-view.content-view`, with the shipped
stylesheet, a UTF-8 declaration and the standard device-width viewport. The
control stylesheet was frozen before editing, sha256
`b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64`.
The temporary viewer fixtures and screenshots live under ignored `build/` and
`.house-mailbox/`; this recipe is their durable replacement.

Native before/after results (both screenshots visually inspected):

- At 390 px, the control page was 604 px wide and visibly cut the plain-paragraph
  digest off at the right edge. The repaired page is 390 px wide and shows it
  across two lines.
- At 1280 px, both pages stay 1280 px wide.
- Extracted visible text is byte-identical before and after; neither run has
  script errors. The already-wrapping trial paragraph remains readable.
- `git diff --check` passes. This is a one-declaration CSS repair; no new test
  suite was added. The discriminating check is the native layout comparison.

The viewer's per-element `too_wide` list was empty even for the failing control;
its `layout.phone.page_width=604` and the screenshot are the failure evidence.

Candidate `site/house.css` sha256:
`df8a377b2f72d80cbd3458ece2f2ede95b25dc6c300ae381614582392ffaaf30`.

No house runtime change or renovation is involved.
Do not check off R1–R6 on this evidence; their live acceptance remains separate.
