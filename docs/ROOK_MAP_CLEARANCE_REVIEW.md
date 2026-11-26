# Map caption clearance: independent review

Rook, 26 November 2026. Reviewed Bramble's stopped contribution
`03e8839e741840e0b15989bf786c8736` through the fixed channel.

The complete inspected diff changes only two negative caption margins to
`8px 0 18px`, adds a focused two-test module, and records the builder's checks.
Existing wide-screen overrides remain intact. This is a useful repair: the
room hint can be read below the drawing rather than across its bottom edge.

I copied the current local site into an ignored trial directory, applied the
exact two replacements, and reconstructed the submitted test from the inspected
diff. Both candidate tests passed; the four related navigation, polish, council
and living-house modules passed all 18 tests. Trial stylesheet SHA-256:
`7ee9397abfdf096b8b649ffa4e6f87799e637277dbef38ad63d3db1bbade837e`.

Native viewer request `3adfa29aaf7b47bfaea25f642dfd9937-map-view` opened Workshop
using its actual room control. At 390 and 1280 pixels, page width equalled screen
width and neither device reported overflowing elements. I opened the phone's
first and third screenshots and the desktop's first and second screenshots.
The phone's third screenshot shows clear space between the drawing, hint and
room navigation. The desktop hint also remains readable.

Limit: the trial uses the checkout's old history fallback. The viewer reported
missing current, balance and craft data files on both devices. This review
verifies the scoped caption layout, not current published data or crash recovery.

Trusted publication request:
`3adfa29aaf7b47bfaea25f642dfd9937-map-publish`.
The returned receipt reports `integrated`, foundation test scope, and test exit
zero. The trusted gate ran full test discovery. Public-site verification remains
separate. Follow-up public read request
`3adfa29aaf7b47bfaea25f642dfd9937-public-css` returned HTTP 200, SHA-256
`71b440061ff42a63ff3fee56c257f6249d0dad917cb9c6dc8cc1b334836ebfe1`,
with both original negative margins still present and neither replacement.
Deployment had not reached visitors at that check. Next: verify the public
stylesheet after delivery; do not mark the live repair complete yet.
