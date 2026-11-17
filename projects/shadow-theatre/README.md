# Shadow Theatre

An offline, dependency-free SVG puzzle exhibit implementing a finite-screen 2D point-light shadow-projection model.

## Model & Domain

- **Point light**: $(x_L, y_L)$ with $x_L < x_{\text{screen}}$.
- **Screen**: vertical line at $x = x_{\text{screen}}$ with finite extent $[y_{\min}, y_{\max}]$ ($y_{\min} < y_{\max}$).
- **Opaque vertical segments (props)**: at most 3 segments, each $(x_i, y_{i,\text{low}}, y_{i,\text{high}})$ strictly between light and screen ($x_L < x_i < x_{\text{screen}}$) and non-degenerate ($y_{i,\text{low}} < y_{i,\text{high}}$).
- **Projection**: analytic ray intersection $y'(y) = y_L + \frac{x_{\text{screen}} - x_L}{x_i - x_L}(y - y_L)$, clipped to $[y_{\min}, y_{\max}]$, then merged via interval union.
- **Scope**: no refraction, mirrors, penumbra, 3D, or automatic motion.

## Files

- `index.html`, `style.css`: page and styles.
- `scene-core.js`: the whole model — projection, interval union, target matching, challenge validation, import/export boundary. No DOM access, so `node` runs the same bytes the page runs.
- `app.js`: DOM glue only. It renders the view that `scene-core.js` derives and calls the tested import/export functions.
- `shadow_model.py`: an independent Python mirror kept for the older model tests. **The browser does not run it.** If the two ever disagree, `scene-core.js` is what visitors see.
- `make-gallery-preview.js` and `gallery-preview.svg`: the Gallery card picture. The generator renders the shipped Clipped Horizon challenge using `scene-core.js` itself, so the picture is the model's real computed stage. Regenerate with `node make-gallery-preview.js` in this directory; the committed SVG must match byte for byte.

## Import / Export Contract

An imported challenge must be a complete JSON object with `id`, `title`, `description`, `screen`, `light`, `props` and `target` (empty `target` means sandbox). `tolerance` is optional and defaults to 0.5. Unknown keys such as `solution` are preserved.

Validation is explicit and runs **before** any state changes:

- required fields present, non-empty string `id`/`title`, string `description`;
- every coordinate and target bound is a finite JSON number (NaN, Infinity, `1e999`, strings and booleans are refused);
- at most 3 props and at most 3 target intervals;
- `light.x < screen.x`, every `light.x < props[i].x < screen.x`, `screen.yMin < screen.yMax`, `props[i].yLow < props[i].yHigh`;
- target intervals have `start < end`, lie inside `[yMin, yMax]`, and are strictly increasing and non-overlapping;
- the whole document must be JSON-representable, so nothing is silently converted on export.

A rejected import is atomic: the current scene, title, target, diagram, interval text and export stay exactly as before, and a visible diagnostic (`#io-message`) persists until the next successful import or mode change. Export validates the displayed scene and refuses to serialize an invalid one; it never writes a scene that is not on screen.

## Running & Testing

- Open `projects/shadow-theatre/index.html` in any modern browser (offline, no build step or dependencies). `scene-core.js` must load before `app.js`.
- Python model tests (unchanged from the first build):
  ```bash
  python3 -m unittest tests/test_shadow_theatre.py -v
  ```
- Shipped-JavaScript tests. These run `node --check` on `scene-core.js` and `app.js`, then a DOM-free harness against `scene-core.js`, then a static check that the page wires the tested model before the UI:
  ```bash
  python3 -m unittest tests/test_shadow_theatre_js.py -v
  ```
  If `node` is not installed the JavaScript tests skip with that reason instead of passing silently.

## Known Limits

- The tests exercise `scene-core.js` directly; `app.js` is only syntax-checked and statically inspected, not run against a DOM. A browser re-check of the import path is still required for acceptance.
- The Python mirror and the JavaScript core are two implementations of one model. They are kept in agreement by review, not by an automated cross-language conformance test.
