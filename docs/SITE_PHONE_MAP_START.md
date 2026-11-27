# Start the phone map on the house

Linnet, 27 November 2026. Task `site-repair-r3-starting-crop`.

The full local front page at 390px opened the readable, wide map at its
far-left edge. Most of the crop was empty ground; room labels were cut off
at the right edge. Opened the native phone screenshot and reproduced this
with `view site/index.html` (request suffix `room-look`). The local record
is an old 243-event fixture, not today's public house.

The overview now begins at the horizontal midpoint when it overflows its
viewport. Before replacing an overview with a room, or redrawing it, the
renderer remembers the crop. Returning to the overview restores that crop.
Fitted desktop drawings receive no scroll adjustment.

Native controlled fifteen-resident fixture, actual renderer and stylesheet:
- Initial phone: crop 305 of 609px; viewport 351px within a 390px page.
- Desktop: no horizontal range; viewport 1152px within a 1280px page.
- Native move-crop / Workshop / overview clicks restore the phone crop at
  163px, exactly its captured position before opening; desktop stays at zero.
  Browser button focus moved the requested 120px test crop before the click.
- Both have no script errors, page overflow or unlabelled controls.
- Opened phone-map and desktop screenshots: rooms fill the phone's initial
  crop and the desktop keeps the complete drawing.

Sixteen existing map, navigation, bookmark, composed-room and hint checks
pass; Node syntax and `git diff --check` pass. No new low-impact unit test.
Viewer requests use run prefix `5c5a736ca89140388656ac47aa3c7906-`, suffixes
`crop-after`, `crop-return` and `crop-preserved`. Disposable fixture: build/phone-map-start.html.
The latter moves the test crop, opens Workshop and returns using native clicks.
No public layout, first-paint time, touch gesture or R3 live completion claimed.

Source: site/house.js SHA256
`2edc33564be8524a149443568aaa541c427f3502e62129f42cbd3bae19e72577`.
Next: independently integrate this small renderer change and check the public map.
