# Independent M2 review

**Decision: REJECT for milestone acceptance pending the required viewport check.** I found no defect in the mathematical certificates, byte conversion, deterministic artifacts, or importable renderer. The review gate is incomplete because I could not open the actual SVG and HTML at 390 px and 1280 px: the computer-use service reported that its browser host was unavailable. The HTML source has a viewport meta tag and switches its two-column cards to one column at 650 px, but source inspection does not establish the rendered result at either requested size.

## Evidence

- The fixed-channel integration of author run `774af63604d14f74b890183d1e0bac73` integrated contribution `122e5fd138e7d7a9b7341acdab272a27b64115ca`; integration reported `test_exit=0`. Review inputs were a temporary snapshot of the delivered canonical source, leaving that checkout read-only.
- `python3 -m unittest discover -s . -p 'test_*.py'`: **29 tests passed**.
- `python3 render_legend.py --out /private/tmp/colour-m2-regenerated`: regenerated all six named artifacts. Each was byte-for-byte equal to its saved counterpart: `first_legend.svg`, `first_legend.html`, `witnesses.json`, `example.svg`, `example-certificates.json`, and `example-output.txt`.
- `python3 verify_atlas.py legends/witnesses.json`: **VALID: 10 exact cases; 20 conservative byte-box certificates; no optimizer called.**
- `python3 example_import.py --out /private/tmp/colour-m2-import-example`: succeeded and reproduced the recorded importing-example output (`survey-risk`, `#59c82c`, exact interval `[1/2, 3/5]`). Tests also exercise a caller-supplied palette and case through `render_atlas`.
- Independently checked S7 from its saved rational palette and witnesses. Its blend is `(39/70, 29/70, 1/2)`, displayed sRGB bytes are `(197, 172, 188)` / `#c5acbc`, and raw linear8 bytes are `(142, 106, 128)` / `#8e6a80`. These are distinct encodings of the declared linear-light coordinates. The exact event interval is `[2/7, 4/7]`; both witness event sums match. `verify_observation` accepts its saved sRGB8 rational primal/dual certificate for bytes `[197, 172, 188]`, with conservative bounds `47857108045232144983/170632382681813352448` to `390545415775124155915/664082786653543858176` (about `[0.28047, 0.58810]`).
- The source documents the half-up encoding rule and closed rational outer-box enclosure. It explicitly does not claim sharp bounds for the true half-open byte bins. The atlas is a checkable mathematical renderer rather than only a demonstration: certificates bind source weights, displayed hex, observation mode/bytes and rational primal/dual bounds, and the verifier does not call the optimizer.

## Scope limits

These are nominal rational linear-light sRGB coordinates and opaque flat swatches. The result does not establish calibrated physical display output, screenshot or compression recovery, alpha compositing, encoded-space blending, or reader performance. The materials explicitly describe the endpoint bars as a supplied comparison, not a blind study. No such claims are made here.

Rook should arrange the missing actual-browser inspection at 390 px and 1280 px before treating the M2 milestone as accepted.
