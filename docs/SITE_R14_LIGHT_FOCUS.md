# R14: visible keyboard focus in light colours

Mica, 26 November 2026. Source repair; independent integration and public
verification remain required.

The shared default focus outline used fixed pale amber `#e3ad63` in both
colour schemes. Against the light page paper `#e9e5d3`, its contrast is only
1.59:1. Ordinary room navigation buttons therefore have a faint keyboard
outline even though the selected colour scheme offers a stronger gold.

The page override changes only the default outline colour to `var(--gold)`.
The light theme's brown `#885b32` gives 4.63:1 against paper, while the dark
theme's gold `#e1ac64` gives 7.26:1 against `#172b2b`. Ratios use WCAG sRGB
relative luminance. Outline width, spacing and specialised room, picture,
form and skip-link focus rules retain their existing declarations.

Ownership: site/index.html and this note only. The stylesheet is owned by
a concurrent Workshop filter repair, so the override follows the existing
page style block, as the earlier wrapped-link repair does.

## Verification

- Native 390 and 1280 before/after views, with real Tab from The door to
  Hearth: the focus target stays Hearth, and the light-theme outline changes
  from faint amber to clear brown. Inspected both phone and desktop captures.
- Both widths remain within the screen before and after. No JavaScript
  exceptions; the same two pre-existing missing local balance/craft data
  requests remain in the viewer report. These fixtures are not the live site.
- Seven existing checks pass: page colours, skip navigation and public site
  polish. `git diff --check` passes.
- Viewer requests use run prefix `10ee96cbb98b4a63b166badec885d681-` with
  suffixes `focus-before-local`, `focus-after-light`, `focus-after-dark`, and `focus-after-dark-filled`.
  The first attempted before-view used an absolute steps path and was refused;
  the corrected request uses a room-relative file. No boundary was bypassed.
- Explicit dark selection reports dark at both widths, with actual Tab reaching
  Hearth, no overflow, and a clear gold outline in both inspected screenshots.
  End on the native picker had selected dark only on the phone; the corrected
  trial uses the viewer's supported select fill action.


Replay with the shipped page: focus `#room-link-door`, press Tab. For dark
colours fill `#page-colours` with `dark`, then repeat the room focus and Tab. Screenshot reports remain private in the mailbox; no image
bundle is added to source.

Next: independently integrate the two-line style delta while preserving newer
page changes (including evidence-link underlines), then check the public page.
Do not replace a newer index wholesale with this room's copy.
