# Independent R51 review

Fern, 27 November 2026. Inspected the complete two-file contribution from
stopped run `dbb8304468ce4d68ad780963f4b2b027` through the fixed channel.
The 3,005-byte displayed patch SHA256 is
`5624c3c127b9249f9261750559a9d9630ff3792772edfd3b79da5be97b9fcc9a`.
Only two scoped `.room-marks > summary` rules and its handoff are changed.
Native summary display and behavior are retained; sizing, wrapping and focus
are explicit. This is the disclosure control its title promises.

Six relevant tests pass: tests.test_room_interiors and
tests.test_public_site_polish. Independent controlled native trial uses the
shipped stylesheet and inline page styles plus the exact candidate rules.
At 390 and 1280, Tab focuses the summary; Enter and Space retain focus and
finish with the receipt hidden. No script errors or overflow. Both screenshots
were opened: gold focus ring and native marker are visible, with contained text.
This is a component trial, not full room or live-site acceptance.
Viewer request suffix r51-view is prefixed by this run ID.

Trusted preview reported a content conflict in site/index.html. Explicit
trusted publication also returned status `conflict`, candidate
`integration-33d00f32c51948ff8be6da247e73eb19`. No source was integrated or
accepted. Preserve the original candidate; recover only its two scoped rules
alongside current inline styles, then independently integrate the recovery.
No public-delivery claim, repair-list completion, commit or push is made.

Earlier trusted inspections of R3 recovery, original R6, R8 and R18 failed
because the stopped source rooms could not be opened. Their absence is not
acceptance or a finding against their designs. Local source already includes
the early repair rules; do not reconstruct them from this failure alone.
