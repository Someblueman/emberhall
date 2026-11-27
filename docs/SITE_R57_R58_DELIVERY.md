# Accounts and Gallery delivery — Aster, 27 November 2026

Public renderer delivery now matches the independently integrated R58 source,
which preserves R57. Complete HTTP 200 read: 351,819 bytes, SHA256
`4403d636b1905dd36a2ab2e784aa34aca9379f36b2f8486a2db5dbfff252a761`.
This replaces the previously witnessed older public renderer; it is not another
source review or integration attempt.

Native checks use the actual delivered renderer and source page/styles with a
public snapshot reconstructed by `scripts/public_site_fixture.py`. The fixed
read-only channel witnessed complete listing and compressed companion bytes;
local Git objects matched their hashes before rendering. No candidate overlay.

- Gallery: snapshot event 56606, listing SHA256
  `a69347f90996e98ce47ff8cf6eb6735b7a828e24a552c9f2c65e9d0c955c2643`;
  companion SHA256
  `9118d6b4f6e762195c8cf49a827ef44165aa7a97c5e069afb76701c23746993f`.
  Direct room entry displays creation links and the first of eighteen creations.
  At 390 and 1280 pixels: no script errors, unlabelled controls or page overflow.
  Opened desktop and phone screenshots; buttons and creation text are legible.
- Accounts: stable snapshot event 56611, listing SHA256
  `07de3b2d791ec72bf18101553e9cc1434ab19d6c849611dad5b1407ce4a5e10a`;
  companion SHA256
  `f732122bed5298b4288e6db979cd55c190252e3116ede16cc939620cd8cf0d63`;
  matching public craft report SHA256
  `bcaa5d57aed0e310835b60c31f10d78fef2e74e4a750f76217e337148f953d90`.
  Real Accounts click replaces Loading with the receiving-run summary and four
  claim rows, including “1 of 1 eligible claims finished” and “8 of 9 eligible
  claims finished”. Both widths have zero script errors, unlabelled controls or
  horizontal overflow. Desktop screenshot inspected. A panel-only inspection
  copy hides preceding Accounts blocks solely to expose the phone results
  within the viewer screenshot limit; production layout is unchanged. Opened
  both phone images: all four summaries fit, remain legible, and wrap cleanly.

A first Accounts trial intentionally retained the initially captured report,
which belonged to a newer publication than its snapshot. It replaced Loading
with “Work counts are unavailable for this publication.” No script errors or
overflow. This is correct mismatch handling, not successful results acceptance.
The later trial uses the matching pair above.

Viewer requests use run prefix `5455d272ab494670a91be8b153707bcc-` and suffixes
`gallery`, `mismatch`, `accounts`, and `accounts-panel`. Disposable fixtures and screenshots stay
outside tracked deliverables. This is native offline replay of witnessed public
assets, not a live-network browser, timing, memory, assistive-technology or history
acceptance claim. R2–R6 are outside this check.

Both repair checkboxes remain open: the list explicitly requires live-page
viewport acceptance. Delivered bytes and native public-data behavior are now
established; a live-network viewport check is a narrower remaining step. Do not
repeat source integration or claim that the older renderer is still served.
