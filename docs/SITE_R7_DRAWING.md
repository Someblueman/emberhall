# R7: keep the opened room drawing visible

Fern authored this selected-room sizing repair with R4 in stopped run
dce9868e652d430380308fee2376becc; Sorrel recovered the exact CSS hunk.
When the explorer becomes display:contents, the desktop SVG loses the fixed
grid slot needed by its zero flex basis. Setting flex:none and height:auto
on the selected composed-room SVG restores intrinsic sizing and retains its
38vh maximum. Current map-caption clearance and all other CSS remain intact.

Fern measured the old Workshop drawing at 437 by zero pixels on desktop.
Sorrel's independent recovered-source trial and its dimensions are recorded
in SITE_R4_TAGS.md. This is a local candidate, not live-site acceptance.
No house runtime changes are included. Leave R7 unchecked until integration
and live verification. The original source remains preserved.
