# R3: recover the readable phone map

Hawthorn, 27 November 2026. Recovered only the 51-line stylesheet addition
from Linnet's stopped contribution bc4dbf80453744658dd3ee39429979d5.
Trusted exact-path inspection returned CSS patch sha256
45f041ffc81dcc4dbb2414229f4b06020c4b0a9013ffbc9a9d0be26e03460d4f.
It applied cleanly beside the current styles; no dropped research was copied.

Below 600px the overview map is 960px wide inside its own horizontal scroller.
Room choices move above it; the hint and roster pager remain within the screen.
Opened rooms retain their separate sizing. Desktop styles are unchanged.
This makes room lettering readable while retaining direct room choices.

Controlled native trials used the actual renderer and the fifteen-resident
fixture from tests.test_name_tag_layout.write_fixture. At 390px, after moving
the stage to scrollLeft 570, the map measured 960x579 and room lettering 18px.
The stage, room choices and roster pager remained between x20 and x371;
page width stayed 390. At 1280px the map remained 1152x694, lettering 21px,
and page width 1280. These are controlled data, not today's public record.

Native focus then Enter on #room-link-workshop opened the real room card and
moved focus there at both widths. Focus then Enter on #overview returned to
the overview and focused #house-view. Selected drawings remained nonzero
(385x296 phone; 437x381 desktop). Every trial had zero script errors and no
page overflow. Phone overview/sideways crop and phone/desktop room screenshots
were opened and inspected. Programmatic scroll tests containment; no touch
swipe or screen-reader behavior is claimed.

Viewer requests use run prefix 999da43ab9e84b53aa7fb92e06fcea71- and suffixes
r3-before, r3-after, r3-scroll, r3-room, r3-return. Disposable fixtures and
screenshots are under build/r3-* and .house-mailbox/views/build-r3-*.
Recreate a fixture with write_fixture('build/r3-check.html'); view it, enter
#room-link-workshop using Enter, then use #overview with Enter to return.

Sixteen checks pass: tests.test_name_tag_layout, tests.test_map_hint_clearance,
tests.test_house_navigation, tests.test_room_bookmarks, tests.test_composed_rooms.
git diff --check passes. No new implementation-mirroring test was added.

site/house.css sha256:
f265ad05b059c8108ca95a3cc792b3d4a12cdf488eb7739ec469569b374a7123

Independent integration and live verification remain. R3 stays unchecked.
