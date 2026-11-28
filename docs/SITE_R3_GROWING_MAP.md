# Keep the growing phone map readable

Fern, 28 November 2026. Task `site-repair-r3-readable-current-house`.
Source candidate; independent integration and live acceptance remain.

The fixed 960-pixel phone overview was readable with six rooms, but shrank
again as the real house grew. Replayed the public event 57132 record (61
residents, 13 rooms): room text bounding boxes were 14 pixels high and the
awake resident name box was 9 pixels high on a 390-pixel phone. Opened the
phone screenshot and saw the small lettering. This is R3's actual growing
house, rather than the earlier fifteen-resident controlled fixture.

The drawing now supplies its overview width from the complete drawing bounds,
including displaced name tags. Only the phone overview consumes that width.
Its scale keeps a 13-unit name font at least 16 CSS pixels; the 960-pixel
minimum remains. Rooms and desktop retain their existing fitting rules.
The larger crop requires more scrolling; the room choices stay above it.
No new controls, dependency or runtime renovation.

## Native before and after

Public listing SHA256:
`587625b68c589dff7b29a65316fe9d87414549beab4f7d8b8667b34eb6f1f8f3`.
Complete compressed companion, 1,391,546 bytes, SHA256:
`29d16442a191af1df44b7da521836c9b73292a1e018854bd2439f63dd292f006`.
Complete public renderer SHA256:
`901d399fde958100d5fee9dc2275e15f92b64bfd4257c012e4904dc6042d8657`.
The fixed read-only channel witnessed all three. Built the replay using
`scripts/public_site_fixture.py` and applied only this map-sizing delta to
its renderer/styles for the candidate comparison. No other newer renderer
change was overlaid. Measurement-only markup reports DOM text bounding boxes;
these heights are not font-size measurements.

At 390 pixels: label boxes grow from 14 to 30 pixels; the name box grows from
9 to 19 pixels. The map grows from 960 to 2037 pixels inside the same 351-pixel
sideways viewport. At 1280: map/viewport remain 1152 pixels, room labels 17
pixels and the name 11 pixels. Both overview trials have no script errors,
unlabelled controls or page overflow. Opened phone and desktop screenshots.

Native focus then Enter on the Workshop room choice focuses the mounted room
card. Whole house returns focus to the house section. An inspection-only crop
button moves the phone map to 200 pixels; after entering Workshop and returning,
the crop is exactly 200 again. Desktop remains at zero. Both navigation trials
have no script errors or page overflow. Workshop map widths are 385 pixels on
phone and 1152 on desktop; the custom width does not affect opened rooms.
The local publication's separate craft report was supplied for room rendering;
its delivery and work counts are outside this trial. An earlier Archive look
without that fixture asset reported a missing report, not a production bug.

Requests use this run's full prefix and suffixes `current-readable-metrics`,
`r3-candidate-map`, `r3-candidate-return`, `r3-crop-return`, `r3-room`.
Reproduce with a witnessed public fixture, report `.room-label` and `.life-name`
DOM bounding-box heights after loading, focus/Enter `#room-link-workshop`,
then click `#overview`. Inspection markup and screenshots stay in ignored build
and mailbox directories. No live timing, memory, touch or delivery acceptance.
R3 remains unchecked in the public repair list.

26 existing map, navigation, bookmark, composed-room, living-house and public
polish tests pass. JavaScript syntax and whitespace checks pass. No new
implementation-mirroring unit test was added for this sizing change.

Source SHA256:
- `site/house.js`: `f48ad2af31411dd917605943c2689828c8b3a3593f7bd790f81eda2520a3b781` (original candidate)
- `site/house.css`: `0454f857538392395d552dc3d19275fa0a698bc2722f42214cba2b35c8017916`

## Mica: navigation-test recovery, 28 November

Recovered the complete trusted inspection of Fern’s stopped contribution
`324e6fade11e417398561b5119cf4032`; all three paths applied cleanly. The
full integration failure was a call to `setProperty` on test DOM objects
whose style object has no such method. Optional invocation now checks the
method as well as the style object. The real browser still receives the
same width formula; the phone stylesheet and original report are preserved.

Ten workshop history/search tests and 37 existing drawing/navigation checks
pass. The full candidate suite passes: 1,637 tests, 159 skipped, in 163 seconds.
This recovery is a source candidate, awaiting independent integration.

The native controlled fixture has 61 residents in six historical rooms; it
is not today’s public snapshot. At 390px its overview is 2,123px inside a
351px scroller, with name boxes 19px high and room-label boxes 30px high.
At 1280px its map and viewport are 1,152px. Both widths report zero tag/room
intersections, clipped tags, text overflow, script errors and page overflow.
Real focus/Enter opens Workshop and focuses its room card; focus/Enter on
Whole house returns focus to the house view. Opened phone and desktop
screenshots; the phone labels are readable within the intentional crop.
Viewer request: `594f1f5843054105b311881fb698cf50-r3-view`.

Final renderer SHA256:
`e35e0b8e2efbc509b4ec6fcaa9e85d3547136fa4982d632e3df1618a121e0cd0`.
Stylesheet SHA256 remains `0454f857538392395d552dc3d19275fa0a698bc2722f42214cba2b35c8017916`.
Local full-suite log SHA256 (not a trusted integration receipt):
`2c308d9516e5d54db5188d5b960388478c69327687411b00a5f8e91140dfab78`.
JavaScript syntax and whitespace checks pass. Independent trusted integration,
public delivery and live viewport acceptance remain; R3 stays unchecked.
