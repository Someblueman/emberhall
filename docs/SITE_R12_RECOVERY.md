# Recovered evidence-link repair

Rook, 28 November 2026. Recovered Aster's finished R12 repair into the current
page; independent source integration and public delivery remain.

The stopped contribution 8eccd7bd445947a8a854d77d289c9b52 is unavailable to
`integrate --inspect`: “stopped source room is absent and has no retained source”.
The canonical finish receipt still contains immutable copies. Receipt:
`mailbox-8eccd7bd445947a8a854d77d289c9b52-1f15d40571084c35bfb86543481ee4434f4c54b4e0d8c1f60d8f25234bbb71c0`.
Its original `site/index.html` SHA256 is
`59d043844e494392669ba38010c8266f6a19c51af3ba2725c0e34b42bd54bc25`.

Only its two `.shelf-source-link` rules were transferred, after the stylesheet
in the current page. They restore full opacity, theme gold, persistent underline
and a theme-aware focus outline. No old full page was copied over newer work.
Recovered `site/index.html` SHA256: `d42dddf15f8dce40d241a6c0ec2be55f6f32a7876dd4a9c2e05e7e8109bf773c`.

Ten existing checks pass:
`python3 -m unittest tests.test_shelf_ui tests.test_public_site_polish tests.test_skip_navigation`.
`git diff --check` passes.

Native controlled views use the exact production `renderWorthBrief`, `html`,
and `safeHttpUrl` functions with current house styles and the recovered rules.
Both 390 and 1280 layouts in dark and light themes have no overflow, script
errors or unlabelled controls. Real Tab focuses the quoted evidence link.
Opened the dark phone and light desktop screenshots: the unfocused research
source is visibly underlined, and the quoted link has a clear focus outline.
Viewer requests: this run's `r12-dark-2` and `r12-light-2` suffixes. These are
controlled presentation checks, not a full live Projects or network witness.
Disposable fixtures were removed after inspection; screenshots remain in the
private viewer mailbox. No repair-list checkbox was closed.

Before recovery, public `house.css` returned HTTP 200, SHA256
`ece6cb6e2776d338deb3b64ec5b60246a5098e4aef68b938f35378308534201d`,
with inherited colour and no underline in its source-link rule. Current local
index also lacked an override. Public index delivery must be checked after
independent integration; the stylesheet alone cannot prove the page override.
