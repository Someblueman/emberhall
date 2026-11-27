# R4: separate resident name tags

Fern authored this repair in stopped run dce9868e652d430380308fee2376becc.
Sorrel recovered its drawing hunks beside the current snapshot loader.
The mixed original also contained superseded loader work and dropped research;
neither is part of this candidate. Selected export patch SHA256:
632f13c527c956322f4f60f47b9f2a79577549f7e23bdd9e5e8263f6b7caecf1.

The old twelve-step placement cap left crowded tags overlapping. Finite
obstacle placement now checks nearby horizontal anchors and moves above every
intersecting earlier box or room title. Text widths are measured in the SVG;
connectors retain resident anchors, duplicate awake foot labels are removed,
and view boxes include displaced tags. Sleeping labels remain.

Controls cover 120 coincident anchors, seeded mixed widths, room obstacles,
determinism, text sizing, connector anchors and bounds. The recovered source
passes 22 drawing/navigation tests and 27 snapshot/history/bookmark/polish tests;
JavaScript syntax and git diff --check pass. Two initially mistyped test module
names were corrected; those import errors were not behavior failures.

Native controlled fifteen-resident fixture at 390/1280 reports zero tag
intersections, room-name intersections, clipped tags or overflowing text lines
in both overview and opened Workshop. No script errors or page overflow.
Overview drawings measure 385x310 and 1152x694; Workshop measures 385x310
and 437x381. These are actual browser measurements on controlled data,
not today's public record. Native Workshop click focuses its room card.
Trials: request suffixes r4-overview, r4-workshop, r4-selected-distinct.
Overview and distinct-path Workshop screenshots were opened and inspected.
This is a local candidate; R4 remains unchecked pending independent integration
and a live check. Many names can still shrink the overview; phone readability
is the separate R3 repair.

Replay: python3 -m unittest tests.test_name_tag_layout
Build the labelled fixture with tests.test_name_tag_layout.write_fixture into
build/name-tags.html, then view it at 390 and 1280 and click Workshop.

Aster's independent integration trial found one compatibility failure among
1590 suite tests: the newly accepted scenery check expected 844 empty-scene
nodes, but the unconditional stems group made 845. This replacement returns
before making that layer when no tags exist. The exact accepted scenery test
and crowded tag controls both pass after the change. Original failed candidate
and log remain preserved as integration-aab535224fe14c39ba0c5fff02025272;
log SHA256 2294282db2397e9358defaaf3f22feb43315eeeeaced052b8670adf406f18565.
