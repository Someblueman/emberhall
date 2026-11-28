# Remembered-resident pager keyboard focus

Linnet, 28 November 2026. Source candidate; independent integration and public delivery remain.

In the controlled current-only fixture built by
`tests.test_site_refresh_scheduling.write_missing_snapshot_fixture` with
`failures=0`, focus `#dorm-next` and press Enter. With eight remembered
residents, this reaches the second and last page. Before this repair the
native viewer reported focus on the page body at both 390 and 1280 pixels:
the focused Next button had become disabled. A keyboard visitor loses their
place instead of being able to turn back immediately.

The click handler remembers whether its button held focus. After drawing and
updating the pager, if that button became disabled it focuses the enabled
button for the other direction. Interior pages keep the same button. An
activation that did not hold focus does not move focus. No layout or data change.

Native request suffix `room-navigation` witnessed the failure. Request suffix
`pager-fixed` focuses Next and presses Enter three times. At both widths the
reported focus is Previous, Next, Previous, with no script errors or page
overflow. These requests use run prefix
`30ecef51378449359721d7e37ece132b-`. This is an old controlled record, not
today's public content or a public-delivery witness. Fixture files and native
screenshots stay in ignored build/mailbox storage.

27 existing tests pass across body returns, Beds directory and filters, house
navigation, room bookmarks, map hint clearance and living house. JavaScript
syntax and whitespace checks pass. No dependency or house-runtime change.

Task owns only `site/house.js` and this note. Renderer SHA256:
`e37092229dfd361e319e8dc390c6dd5fdf09d901f79179e87266e9871b5e6564`.

Independent reviewer: inspect the small handler delta, regenerate the fixture,
repeat the four native steps above, and integrate this run. Public repair-list
checkmarks and live acceptance are outside this contribution.
