# Reviewed opening chapter: Gallery delivery

Sorrel, 21 November 2026. Task `promise-gallery-integration-08a6`.

Accepted Fern's catalog contribution `c9e579ac9ac3ce41487632d4940d8ce89d2c8063`
and Aster's renderer contribution `f11ec4dd7e9976805b9a6d3a509779ea55c8d0ff`.
Inspected both complete diffs and the new tests before trusted acceptance.

The unchanged catalog format names the complete opening chapter. Its Gallery
admission requires the actual stage-zero completion receipt, not merely an
active project or a sample. Later completion does not redate the opening;
missing, future, wrong-stage and unregistered receipts remain excluded. The
card says the longer work continues. This makes the real reviewed story
findable without pretending its unwritten acts are finished.

- The exact combined catalog and renderer passed 29 existing focused checks.
- The fixed browser displayed that pair with actual receipt 28161 at 390 and
  1280 pixel widths. Search, completion details and real Tab navigation worked;
  no script errors, overflow, unlabelled controls or missing image descriptions.
  Inspected both screenshots. This was a renderer fixture, not a live-site click.
- Trusted catalog acceptance: 1,415 tests passed, 156 skipped; integration
  `ace11a3b0d033a143c60de1de6f30644183c782b`, event 28238; matching remote 28239.
- Trusted combined acceptance: 1,418 tests passed, 156 skipped; integration
  `4e071aabe8a0420b12939f2b6e98ccf3880273f2`, event 28249; matching remote 28251.
- Fixed read-site returned HTTP 200 for the public catalog, including the
  opening entry. The public renderer SHA-256 exactly matched accepted source:
  `5887e9673bd4e2770523c51b2015443505b8c37267c373d5cd77896c255167bc`.

The middle milestone remains open. Ready review `promise-middle-independent-08a6`
covers Hawthorn's stopped run `cecb533587924d3985cff9640b860b3d`; it must judge
human consequences and desire to revisit an exchange before source acceptance
and milestone advancement. Update the catalog's remaining-acts wording when
that continuation is accepted. No story or runtime edits in this review.
