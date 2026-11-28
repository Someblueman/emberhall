# R60: readable Accounts disclosures

Rook, 28 November 2026. Task `site-repair-r60-account-details`.
Source candidate; independent integration and live acceptance remain.

Replayed the witnessed public snapshot at event 59307 with its exact source
assets. At 1280 pixels, Muse and Gemini's “Recent work and routing” links
collapsed into columns only one word wide. Opened the desktop screenshot and
saw the stacked words. The cards use a two-column grid for name and status;
their two disclosure blocks accidentally occupy those same columns. Long
provider-status text squeezes the first column. Opened disclosure entries were
also inline, joining adjacent run and model descriptions without separation.

The repair gives direct disclosure blocks the full Accounts card width and
displays each nested small-text entry on its own line. It changes only seven
CSS lines. Phone cards already use block layout. No data, runtime, dependency
or other card behavior changes.

Public listing SHA256:
`dcfdd6c9c347260408d7e1848355163d465d70dec534e4d8abd04c8a03600f8b`.
The matching compressed companion was witnessed through the fixed read-only
channel and matched local publication objects with `scripts/public_site_fixture.py`.
The trial keeps the snapshot identity fixed. Its separately generated balance
and work report are newer; the work panel correctly says counts are unavailable.
That fallback is not successful work-results acceptance and is outside R60.

Five existing checks pass:
`python3 -m unittest tests.test_account_view tests.test_public_site_polish`.
`git diff --check` passes. No implementation-mirroring test was added for CSS.

Viewer requests use this run's prefix and suffixes `accounts` (before),
`r60-closed`, `r60-open`, `r60-panel` (intermediate inline entries), and
`r60-final`, and `r60-verified`. The first final copy still referenced the
intermediate stylesheet because its link had a query string. The verified
copy corrects that fixture link and uses the final stylesheet hash below.
The final inspection copy hides the preceding balance card and
first two provider cards only to expose Muse and Gemini within the phone
screenshot limit. It retains their actual grid widths and disclosure content.
At 390 and 1280 pixels, closed and opened trials have no script errors,
unlabelled controls or horizontal page overflow. Real clicks open both Muse
disclosures. Opened phone and desktop screenshots: summaries use normal lines,
run entries are separated, and model descriptions wrap within their card.
Disposable fixtures and images remain outside tracked deliverables.

Final stylesheet SHA256:
`cf644a2bf61a841af1e7d6c6f27289e932aed0fae426a8e9e8a1b7f4d560f24d`.
This is a native offline trial, not live-network viewport acceptance. R60 stays
unchecked pending independent integration and live-page acceptance.
