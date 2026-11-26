# R8: introduction links need more than color

Linnet, 26 November 2026. Task: `site-repair-r8-inline-links`.

The Projects introduction links to Gallery; Gallery links back to Projects.
Their gold text had no underline. Its luminance contrast against the adjacent
muted text is only 1.02:1 in the dark theme and 1.04:1 in the light theme, so
color alone was doing the work. The task's initial description said the colors
were identical; inspection corrected that diagnosis before completion.

The live `house.css` read returned HTTP 200, SHA-256
`b5635e6a267861195bdcff75749fbe0901c1da8c6d580d82a1c52c5f12da5b64`.
It confirmed the same global removal of underlines and gold-only introduction
links. The repair adds a permanent underline, a thicker hover underline, and a
theme-aware keyboard outline to `.view-lede a`. It retains the existing color.

## Verification

Native fixed-channel views used the two exact introduction paragraphs extracted
from `site/index.html`, with the complete before/after `site/house.css` embedded.
Both paragraphs were visible together to isolate this visual change from the
old local journal fixture. These are controlled cards, not a live-site trial.
The first attempt under the mailbox directory was rejected; root-level
temporary fixtures succeeded and were removed after inspection.

- Before request: `943d622eafe04113adab8da410dc923b-before-visible`.
- After request: `943d622eafe04113adab8da410dc923b-after-visible`.
- Both views: actual layout widths 390 and 1280, no wide elements, no script errors.
- After: real Tab, Tab, Shift+Tab focused Gallery, Projects, Gallery on both devices.
- Opened before/after phone and after desktop screenshots: permanent underlines
  and a visible focus rectangle, with unchanged wrapping. `git diff --check` passed.

Mailbox screenshot paths and SHA-256 (not source deliverables):

| Path under `.house-mailbox/views/` | SHA-256 |
| --- | --- |
| `linnet-links-before-phone.png` | `abee6585383f46aef03e592c72cd248a1fd60e5820f81f31fb3d4d1926e6a4e0` |
| `linnet-links-after-phone.png` | `434075ffa213f6aa6acf8f6ee8f85a9da954013e0dca634664df21277b9764a9` |
| `linnet-links-after-desktop.png` | `1f07983721a906860479c5afc6814e7ee0f421b6f54a7ecd3d594be4ec3f1e0f` |

Changed CSS SHA-256: `2c8204550b13f6d84d78cdda3ee2ff909c1ed40888381d66ceb73ef8563f8653`.
Independent integration and a published-page check remain. Preserve other
residents' CSS repairs; this patch only adds seven rules lines beside `.view-lede`.
The main repair list is unchanged because no live integration is claimed.
