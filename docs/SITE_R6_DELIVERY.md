# R6 delivered-style review — Tern, 27 November 2026

The public HTML, renderer and stylesheet now contain the accepted wrapped-entry
repair. No production source was changed. R6 remains unchecked: this is native
offline replay of delivered assets, not a live browser session.

Complete successful fixed-channel public reads:

- index.html: `7f0c4ca079d0cc1463694eaac26d3f2ddd176ef8929d30cb4143990932cfe472`
- house.js: `4403d636b1905dd36a2ab2e784aa34aca9379f36b2f8486a2db5dbfff252a761`
- house.css: `20eefe2bb5ccf74ca8ea4d0e7310a900de65e490bfc93896d31ed8fbcc96851f`
- current.json: `d16cc8ab3c84e2173cf8ad71ff217048a1903b236547aaa41793f3ac791c5695`
- current companion: `92d4a8380854bd34af4b740743a191c9c1055a72f7b18f4a8e6a178093a09749`

The current snapshot ends at event 56596. `scripts/public_site_fixture.py`
reconstructed it from matching local publication objects. All three page-asset
hashes above match the replay exactly, without candidate overlays.

History is separate: read-site stopped at its five-megabyte limit. The returned
5,242,880-byte prefix hash is
`5ac77b47ace3c689a13a0894f2988cdb6e40b4b572dc147a20bb3b4aa6e095ca`.
The matching local listing has the same 7,699,763-byte total length and prefix;
its remaining bytes and history parts were not witnessed over the network.
Local history parts match their listing hashes. Do not describe this as full
history-delivery acceptance.

The unmodified page opens event 51681 through the real event-number form, loads
history, and displays both the nutrient-project drop and the Almost Halving
drop in its recent changes. At 390 and 1280 pixels it reports no script errors,
no horizontal overflow, and focus on the first real growth-entry button.
The full desktop screenshots show separated wrapped lines and timestamps.
Phone screenshots stop above the card because of the viewer's three-image cap.

An inspection-only copy hides preceding introduction, map and history decoration
while retaining the real event-number form, card markup, renderer and card
styles. It is not a production layout change. Native focus then Tab checks the
next entry's keyboard focus. Opened the phone card screenshot and desktop card
screenshot: both long titles wrap into distinct lines, timestamps sit below
them, the left rule stays clear, and the focus rectangle contains the selected
entry. Both widths report zero script errors, zero unlabelled controls and no
page overflow. Viewer request suffixes are `r6-native` and
`r6-inspection`, under this run's full request prefix.

This review confirms the Gallery renderer has reached the public site; it does
not verify Gallery/work-results interactions or close R2–R5, R57 or R58.
Temporary replay files and screenshots are not deliverables.
