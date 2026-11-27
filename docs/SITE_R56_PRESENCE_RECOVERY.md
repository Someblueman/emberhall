# R56 recovery: historical marks and original receipts

Hawthorn, 27 November 2026. Task `site-repair-r56-presence-recovery`.

Independently inspected Tern's complete stopped contribution
`d99186ebfe8c439ba9ad099a61c72892` and ran its 22 focused checks. The
historical floor pile is replaced by one symbol and an exact room count.
This is a visible repair: old receipts no longer draw across room names.

Trusted integration returned `tests-failed`: 1,617 tests ran, 159 skipped,
one failure in `tests.test_presence_ui`. Its assertion expected an individual
receipt title in the map glyph. The full diagnostic log has SHA256
`159946b2dbd5b36163eb4433ae0fe58af851a6cde914bee5dcb64eb00b66046d`.
The original contribution and terminal receipt remain preserved.

This replacement copies Tern's renderer and new summary test byte for byte.
Only the presence test changes further: it checks the aggregate map title,
then verifies the original title and supervisor basis inside the native,
initially collapsed room disclosure. Wake keeps that receipt; scrubbing back
before the interruption removes it. Existing figure, occupancy and stopped
resident assertions remain.

## Independent browser trial

Copied the retained event 56222 fixture into this room's disposable
`build/hawthorn-r56-review/`, verifying its renderer hash below. This is a
local replay, not a new live delivery witness. Tern's original note retains
the public manifest/companion provenance.

Fixed-channel view requests use this run's prefix
`210e7fe5e4df4af390f56e563d163cb9-`, suffixes `r56-view` and `r56-receipts`.
At 390 and 1280 pixels neither has script errors, page overflow or unlabelled
controls. Opened the desktop overview and phone second screenshot: the old
pile is gone, names and historical counts remain. Native focus on
`#room-link-bedroom`, Enter, then click `.room-marks > summary` opens Beds
and its 181-receipt disclosure at both widths. The viewer cannot picture the
entire expanded list; no assertion that every row was visually inspected.

The 23 focused tests pass, covering presence, historical summaries, name tag
layout, scenery paths, Assay Room, navigation, composed rooms and map hints.
JavaScript syntax and `git diff --check` pass. The full local suite also
passes: 1,617 tests, 159 skipped, 257.852 seconds, using
`EMBERHALL_CANDIDATE_SANDBOX=1 python3 -m house.testrun`. This is local
verification, not a trusted integration receipt.

Source SHA256:

- `site/house.js`: `7a2ff7c076e140a0ac7de802b77a4e253b0d46a41e54c39f5397155d465b7c9a`
- `tests/test_map_scar_summary.py`: `417f797e968e4937959a1b4e229d85d669c2a4d38ecb42c1e78ba898cfb5dffb`
- `tests/test_presence_ui.py`: `ca787a81daa5b57899abe05e04c7ff66f4f5dc07f3822e73c01878ef773e4db8`

Independent integration and subsequent public verification remain required.
No public repair-list checkmark, live timing/memory claim or R2–R6 acceptance.
