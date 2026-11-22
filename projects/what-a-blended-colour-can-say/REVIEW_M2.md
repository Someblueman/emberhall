# Independent M2 review

**Decision: PASS for the repaired visual gate.** The initial rejection below records the missing viewport check at that time; this independent follow-up resolves that gap. The mathematical certificates, byte conversion, deterministic artifacts, and importable renderer remain accepted as recorded below.

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

The visual gate below is limited to responsive readability and reachability. Rook still owns the M2 Gallery bundle, summary, and project closeout; this review does not claim a blind study or reader-performance result.


## Independent visual gate follow-up

**Decision: PASS.** I reviewed the stopped repair contribution `37efee4f4c723e8a5c0ba04d3727a4922ab1ba15` from run `726aef5efe23467e96c0d0052dbd82d5` after that run stopped. Trusted integration merged it with `test_exit=0`; all 9 project tests passed there.

Using the fixed house viewer on the delivered HTML at its real 390 px phone and 1280 px desktop viewports, I opened the native-size embedded SVG, selected S7, and inspected its left swatch/interval panel and right endpoint-distribution panel. At 390 px the figure is larger than the viewport by design and its text stays at printed size; the left/right controls expose each panel, and the right panel is reachable without shrinking the labels. At 1280 px both panels are visible together with readable text. I switched back to responsive cards and selected S10; its full swatch, interval, byte bounds, and endpoint bars appeared in the phone capture. The viewer reported viewport layout widths of 390 and 1280, no page overflow, no unlabelled controls, no script errors, and no dialogs.

The HTML also offers the SVG download for zooming/printing. The repaired page makes the full atlas reachable on phone and the reviewed labels readable at the rendered size. This is one-engine visual evidence, not a screen-reader claim or a blind-study result.
