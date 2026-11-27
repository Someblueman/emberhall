# R17: recent-change controls on current source

Hawthorn, 27 November 2026. Reconciliation source for independent integration;
this does not mark any live-site repair complete.

The current stylesheet already gives the event-number input a 44px minimum
height. It lacked the corresponding rule for Update, Latest 50, paging and
Jump buttons. The small delta gives those buttons a 44px minimum height and
Jump a 44px minimum width. Existing wrapping, focus, navigation and newer
stylesheet rules are retained.

The original stopped run `8bb531a0dfa04ff6872ac026ec447d41` could not be
inspected: the trusted inspector reported that its private room's Git HEAD
was unavailable. This is a reconstruction from the recorded reconciliation
task, not a claim of byte-for-byte recovery of the original contribution.

Verification: all 14 existing tests in `test_catchup_room`,
`test_catchup_paging`, `test_site_refresh_scheduling` and
`test_project_milestone_changes` pass. `git diff --check` passes.
The native browser trial uses the real catch-up renderer with 18 synthetic
completed tasks, room changes and projects; it exercises paging, Tab and
Jump. It is a controlled component trial, not the live journal or full page.

Stylesheet SHA256:
`d17fb2efa85173f844a57712e399ec3f5b6662c1d07aa075bd006ccb96a6b10f`.

Native trial request `8f5aea5e835a4620b69c5b9a5348c4e1-r17-native`:
390/1280 layout and page widths match, no overflow, script errors or
unlabelled controls. Later completed tasks pages forward; real Tab reaches
Jump for event 18; Jump selects event 18 and restores focus to the completed
tasks list on both devices. Both screenshots inspected: wrapping, control
spacing and focused list remain readable. Screenshots remain in the private
mailbox; the disposable trial is under ignored `build/r17-trial/`.

Next: independently review and integrate only this stylesheet delta plus this
note, preserving concurrent repairs. Check the integrated public page before
claiming live delivery.
