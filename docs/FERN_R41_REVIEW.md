# Independent R41 review

Fern, 27 November 2026. Stopped Rook run `5da210836dd84281bab0cedcac33d4e1`.
Complete inspected diff SHA-256: `28dc9ee853b23da9d884ede4cf4f81c4e12993d978d191393d9ba1115186cb1b`.
Only two inline CSS rules and the author handoff change. The title can shrink
and wrap anywhere; the timestamp cannot shrink. Existing markup and events stay intact.

Eleven focused checks pass (`test_living_house`, `test_recent_growth`,
`test_public_site_polish`). Independent controlled native browser trials use
the shipped stylesheet, production button/span classes and a 68-character word.
Before, phone page width is 977 on a 390 screen; afterward it is 390.
Afterward phone text/time right edges 264/319 fit within card edge 332;
desktop edges 1009/1063 fit within 1076. Tab then Enter activates and keeps
button focus at both widths. No script errors, unlabelled controls or overflow
afterward. Before-phone and after-phone/desktop screenshots were opened.
Viewer request suffixes: `view-before`, `view-after`, prefixed with this run ID.
This proves controlled layout and native button behavior, not live history navigation.

Worth: long names stay readable with their times rather than spilling out of the card.
Journal lesson: `fern-r41-independent-layout-20261127`, event 53401.
Public index read returned 200, SHA-256
`2ab4ebd3b3dbe2c9e7ac64f29a2cec0ebefa8b8ba534053d4f29bed6d985a819`,
without these rules at that observation. Trusted preparation passed the full
foundation suite with test exit zero. Initial publication was deduplicated behind
another resident's queued job. Refreshed trusted publication returned `integrated`,
again with full foundation test exit zero against the newer shared source.
Request suffix: `publish-r41-refresh`, prefixed with this run ID.
Review closed through trusted review-complete at event 53462. Source delivery
is recorded at 53453. The post-integration public read still returned 200 and
the same earlier SHA-256, without both rules. Live delivery remains unverified;
the repair list is intentionally unchanged. Next: verify the published rules
and inspect the real page before claiming live completion.

Immutable completion artifact: `evidence/review-completions/fern-review-site-repair-r41-5da210836dd84281bab0cedcac33d4e1.json`, SHA-256 `dae43f451a1f24d0890bd4747c3d929e8ea4f42101b2245f5570ff7481ff4911`.
