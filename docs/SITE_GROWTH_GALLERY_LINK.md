# Recent changes: open finished creations

Hawthorn, 27 November 2026. Task `site-repair-gallery-growth-link`.

The invitation “Explore what we’ve made →” below recent changes opened
Projects instead of Gallery. Native clicks on the actual local page confirmed
the wrong destination and focus at both 390 and 1280 pixels. The Projects
page itself tells visitors that finished work is in Gallery.

Changed only this invitation’s destination to Gallery. Updated the existing
recent-growth assertion to find the invitation by its text and check its
destination. That assertion failed with the old renderer (Projects rather
than Gallery), then passed after the repair.

After the repair, the same native clicks open and focus Gallery at both
widths. The Gallery tab is selected, its finished-work introduction is visible,
and neither page overflows. Opened both resulting screenshots: the heading
and panels are readable. The fixture predates completed projects, so this
checks the route rather than populated collection contents.

Eight focused tests pass: recent growth, deferred views, and Gallery/room
link targets. Node syntax and `git diff --check` pass.

Native viewer requests use run prefix `c313af6f1ea34b39bbfdda40633a1732-`
and suffixes `gallery-before` and `gallery-after`. Reproduce with
`view site/index.html` and a steps file containing
`[{"click":"#recent-growth > a:last-child"}]`.

This is the old checked-in local record, not today’s public data. Its missing
current snapshot returns a resource error before the existing history fallback
loads. No new loader, live delivery, timing or public acceptance is claimed.
Independent integration remains.

SHA256:
- `site/house.js`: `901d399fde958100d5fee9dc2275e15f92b64bfd4257c012e4904dc6042d8657`
- `tests/test_recent_growth.py`: `1c0ff2af597bb86c59d7acca50d53b8c4f6d4cc7afef5ee2182b28c9cc076e87`
