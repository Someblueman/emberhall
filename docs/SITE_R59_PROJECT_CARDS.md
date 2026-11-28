# R59: readable project cards on phones

Tern, 28 November 2026. Task `site-repair-r59-project-card-clipping`.
Source candidate; independent integration and public delivery remain.

The Projects view of public snapshot 57588 cuts off the active project's
long title, description and milestone on a 390-pixel phone. Opened the native
phone screenshot: text visibly crosses the card's right border. The initial,
uninstrumented replay reports a 421-pixel page on a 390-pixel screen.

The single implicit grid column used its contents' minimum width. Give shelf
cards a `minmax(0, 1fr)` column, allow the card to shrink, and wrap long words
and paths. This is three stylesheet declarations, with no renderer changes.

Rebuilt the public snapshot using `scripts/public_site_fixture.py` and complete
fixed-channel listing/companion receipts. Listing SHA256:
`56460428b2ff591116a4cec79fb621697079f83a43dc3d910c3f465dbfc8db3b`.
Companion SHA256: `4a004d874889b648c123e3fd31cc9f99abda111a9701b9946bdd8c7f1ac26e33`.
Only the candidate stylesheet was overlaid in the disposable replay.

Native baseline/candidate trials at 390 and 1280 pixels show:
- Phone card edges: 42.5–347.5 pixels. Baseline title reaches 420.34 pixels
  in two lines; candidate title reaches 282.25 pixels in four lines.
- All seven baseline direct card children cross its right border. No candidate
  direct card child does. The screenshots show the full wrapped title and body.
- Desktop title remains one line, reaching 804.75 pixels inside a card ending
  at 1177 pixels. No direct child crosses that card's border.
- The native Milestone and details disclosure opens at both widths. No script
  errors occur in any trial.

The temporary measurement paragraph itself introduced overflow, so its overall
page-width readings are excluded. A separate clean replay removes that markup.
Requests use the run prefix `ebb65082a9344bb4ba6ba96cf0244eca-` and suffixes
`r59-fixed-baseline`, `r59-after`, `r59-expanded`, `r59-clean-expanded`.
The final clean replay removes measurement markup: page width is exactly 390
on phone and 1280 on desktop, with no script errors or reported overflow; native
click opens Milestone and details at both widths. Opened phone and desktop
screenshots. Earlier measurement markup widened the page itself, so its overall
page-width report is excluded; its card/title bounds above remain useful.
Disposable fixtures/screenshots remain outside tracked deliverables. This is
local replay, not live-network viewport acceptance.

Seventeen existing Projects, search, public-work and shelf tests pass:
`python3 -m unittest tests.test_projects_view tests.test_projects_find tests.test_project_work_public tests.test_shelf_ui`.
`git diff --check` passes. No new test or dependency was added for this CSS fix.

Candidate `site/house.css` SHA256:
`ece6cb6e2776d338deb3b64ec5b60246a5098e4aef68b938f35378308534201d`.
