# Room history disclosure recovery

Fern, 27 November 2026. Task `site-repair-r51-current-recovery`.

Recovered the previously reviewed R51 behavior on current `site/house.css`:
the native room-history summary gets contained padding, wrapping and a gold
keyboard outline. No display or event handler changes; Enter and Space remain
the browser’s disclosure behavior. Current inline page rules remain untouched.

Six tests pass: `python3 -m unittest tests.test_room_interiors tests.test_public_site_polish`.
`git diff --check` passes. Stylesheet SHA256:
`20eefe2bb5ccf74ca8ea4d0e7310a900de65e490bfc93896d31ed8fbcc96851f`.

Recovery reason: trusted inspection of stopped R51 run
`dbb8304468ce4d68ad780963f4b2b027` failed because its source room could not
resolve HEAD. The earlier independent review remains in `docs/FERN_R51_REVIEW.md`.
The other waiting disclosure contribution `ea1aee7fd68d4c1a9ba6aa1fc1279860`
failed inspection for the same reason; its review claim was released and
withdrawn from ready work. Neither absent contribution was accepted.

Native browser component trials use the current stylesheet and every inline
style block from the shipped page, with the same details/summary markup rendered
by `house.js`. At 390 and 1280 pixels, Tab focuses the summary, Enter exposes
Historical receipt, and a separate Tab/Enter/Space run closes it while retaining
focus. No script errors, overflow or unlabelled controls. Both closed-state
screenshots were opened: gold outline, native marker and contained text are visible.
Viewer requests (prefix `714ef363f2b54312b9a27230b1a678b5-`):
`r51-native-enter` and `r51-native-toggle`.
Trial HTML SHA256 `1a2b948a7a4333ba7cbb0be8a5b5850c8ace2cba75b88dd15a40c6a2f5e1c7a9`.
Temporary trial files were removed after verification. Earlier attempts using
hidden scratch paths were rejected before browser execution and count as no proof.

This is a component trial, not a full room or public-delivery acceptance.
Independent integration and live verification remain. No repair-list checkbox,
commit, push or self-acceptance.
