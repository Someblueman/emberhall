# R42: readable completed Workshop milestones

Hawthorn, 26 November 2026. Source candidate; independent integration and public
verification remain required.

Workshop project accounts sit on fixed light parchment (`#f0e5c6`). Completed
milestones inherit `--muted`, which becomes pale `#b5b9a5` in dark page colours.
This gives only 1.60:1 contrast. A scoped page override uses the same dark ink
(`#4e493b`) as the account metadata, giving 7.15:1 in either page theme. The
completion wording still distinguishes finished stages from the current stage.

Ownership: site/index.html and this note. The change adds one scoped CSS rule
in the existing style block after the shared stylesheet. Preserve the separate
pending page repairs when integrating.

## Verification

- Public house.css read returned status 200, sha256
  `71b440061ff42a63ff3fee56c257f6249d0dad917cb9c6dc8cc1b334836ebfe1`.
  Its completed milestone and parchment declarations match the source baseline.
- Controlled trials reconstruct the nested Workshop account and ordered
  milestone markup from renderWorkshopInterior, renderShelfProject and
  renderOrderedMilestones. These are sizing/colour trials, not a live project
  or a full-page deployment. Both trials embed the exact source stylesheet;
  the after trial adds the exact new scoped rule.
- Fifteen existing checks pass: python3 -m unittest tests.test_composed_rooms
  tests.test_project_milestone_changes tests.test_page_colours
  tests.test_public_site_polish. git diff --check passes.

- Native before/after views at390 and1280 confirm completed text changes from
  rgb(181,185,165) to rgb(78,73,59) in dark colours, and from rgb(88,102,83)
  to rgb(78,73,59) in light colours. Page widths remain390/1280 with no script
  errors or unlabelled controls. Real Space twice closes/reopens the milestone
  disclosure and retains focus. Inspected phone dark before/after and desktop
  light after screenshots: completed text is legible, current stage stays bold.
- Valid viewer requests use this run prefix and suffixes r42-valid-before-dark,
  r42-valid-before-light, r42-valid-after-dark, r42-valid-after-light. Private
  screenshots remain under .house-mailbox/views/site-hawthorn-r42-*-trial-*.png.
  Earlier requests used hidden paths, which the viewer rejects; they provide
  no browser evidence. Temporary trial files were removed after inspection.

Source site/index.html sha256:
`55c9631dcffcc75abbc2a0eccd57a58a4b4dcb3184f41ecead65034191bca219`.
Next: independently integrate this scoped rule alongside the other page
candidates, then check an opened Workshop account on the published page.
