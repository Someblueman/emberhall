# R32: presence explanation press area

Hawthorn, 26 November 2026. Candidate source repair; independent integration
and public verification remain required.

The `How to read this` label beside `Who is home` measured 19px high at
390px and 1280px. The public stylesheet returned status 200 with sha256
b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64;
its `.notes-toggle` rule matches the local baseline and has no minimum height.
The nearby motion label already has a 44px minimum.

One declaration adds `min-height:44px` to `.notes-toggle`. The checkbox keeps
its native size; the whole associated label becomes easier to press.
Ownership: `site/house.css` and this note only.

Verification:

- Native isolated views at 390px and 1280px measure 19px before and 44px
  after. Real Tab then Space keeps focus on the checked checkbox and shows
  the explanation. Phone before and both after screenshots inspected: clear
  native focus, ordinary checkbox size, readable spacing, no overflow/errors.
- Full local page at both widths: real focus and Space check the same field;
  page width equals screen width. Only the existing missing balance.json and
  craft.json requests occur, also present before the change. Local history is
  the shipped 243-event fixture, not a current public record.
- 21 existing presence, resident-presence, public-polish and skip-navigation
  checks pass; `git diff --check` passes.
- Viewer request prefix: `4d5e00c47eb54618ba1a761e8a57f77d-`.
  Baselines: `r32-before`, `r32-measure`; decisive after: `r32-confirm-after`;
  full page: `r32-full-after`. Screenshots remain private. An earlier after
  request overlapped a failed local reporting script; the separate confirmation
  above was requested after the stylesheet edit and is the accepted witness.

Source stylesheet sha256:
`fa760f9874f859592be7394b893f88ee5e361e75053dd2d145530e4af5cde2f7`.

Replay: apply the one-declaration delta to the newest stylesheet, open the
house page at 390px and 1280px, focus `#presence-notes`, and press Space.
For an exact height check, measure the associated `.notes-toggle` label.
Independently integrate this declaration while preserving other stylesheet
candidates; then verify the public page. This does not resolve R1–R6 or mark
those live-verification checkboxes.
