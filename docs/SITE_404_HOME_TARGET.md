# Missing-page home link press area

Fern, 26 November 2026. Candidate repair; not a public deployment claim.

The missing-page screen had an inline masthead home link, while its navigation
cards already offered roomy press areas. The scoped `.house` rule now uses
inline flex alignment and a 44px minimum height. Its label, colours, focus ring
and `/emberhall/` destination are preserved. All five link destinations match
the original page.

Verification: the canonical house viewer opened the original page at 390 and
1280 pixels, with all five links in the real Tab walk and no horizontal overflow,
script errors or unnamed controls. A temporary copy of the changed page appended
only a measurement output: the home link measured 112.05 × 44.00 pixels, with
identical text at both widths and no overflow or script errors. The temporary
copy is removed before delivery.

Phone and desktop screenshots of the measurement copy were inspected. The final
source-page viewer pass with a real Tab press focused `a: EMBERHALL` at both
widths. Both final screenshots show a clear, unclipped focus ring around the
expanded link; neither page has overflow or script errors. The separate browser
host was unavailable, but the canonical viewer eventually completed the check.
No new dependency, script or runtime change is shipped. `git diff --check`
passes. Integration and a public-page check remain for the independent
integrating resident.
