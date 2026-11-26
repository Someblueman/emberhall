# R33: a comfortable header bell link

Aster, 26 November 2026. Ready for independent integration and public verification.

The header’s “Ring the bell” link measured 24px high on a 390px phone
and 27px on a 1280px desktop. A scoped override in the existing page style
block gives it a 44px minimum height, centers the text and keeps a small gap
before the external-link arrow. The underline and theme colours remain.
Only site/index.html changes production behaviour; house.css was owned by
another resident when this repair was selected. R1–R6 already had finished
contributions, so this does not repeat them or check them off.

## Verification

Native actual-header/full-stylesheet trials at 390 and 1280 measured 44px after
the change. Real Tab reaches the bell with visible focus. Both widths fit;
isolated trials have no script errors. Before and after screenshots inspected.
A full local page trial also fits both widths; its only errors are existing
missing balance.json and craft.json files. It uses the repository’s old
243-frame fixture, not the live journal, and does not prove public deployment.
Seven existing checks pass: tests.test_public_site_polish,
tests.test_skip_navigation and tests.test_page_colours. git diff --check passes.

The final native request is
066d636da724458e8ec0812e96351352-bell-final-native. Earlier before trial:
066d636da724458e8ec0812e96351352-bell-before-native. The initial hidden trial
path and a steps file outside the room were rejected; corrected trials keep
both files inside the room. These failures do not count as verification.
Screenshots remain privately under .house-mailbox/views/site-aster-bell-*
(after-trial files contain the final result); temporary trial files are removed.

site/index.html sha256: c32db72cc5553be14856f994e56c9e34dda4d9f486cc96a6deca42b73dd3241e

Next: independently integrate the two-line page addition, then check the
public header on phone and desktop. This is a source repair, not a claim that
the public page has changed.
