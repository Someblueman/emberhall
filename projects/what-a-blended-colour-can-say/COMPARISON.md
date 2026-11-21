# Held-Out Probability-Legend Comparison Protocol (Milestone 3)

This document defines the frozen held-out comparison between the **Probability-Interval Atlas** (`atlas_a/`, `atlas_b/`) and an **equal-information Explicit-Distribution Baseline** (`dist_a/`, `dist_b/`). All design decisions, prompts, scoring rules, and failure conditions are fixed before any reader response.

## 1. Held-Out Case Set

Ten new cases (`H1A`–`H5A` in Set A, `H1B`–`H5B` in Set B) use three held-out palettes (`citrus_slate_3d`, `ochre_indigo_3d`, `amber_navy_ramp`) that are absent from `legends/`, `render_legend.py`, `blended_colour.py`, `example_import.py`, and all M1/M2 tests. Each set contains one case from each of five regimes:

1. `H1`: Determinate outer-facet blend (`EXACT`, exact linear-light model).
2. `H2`: Ambiguous interior blend (`BOUNDED`, exact linear-light model).
3. `H3`: Completely unidentifiable blend (`UNIDENTIFIABLE`, `[0, 1]`; `H3A` is pure interior stop `T3`, `H3B` is a non-stop ramp mixture).
4. `H4`: Supported rounded `srgb8` observation (half-up 8-bit encoded sRGB).
5. `H5`: Supported rounded `linear8` observation (half-up 8-bit raw linear data, displayed beside the `srgb8` swatch).

## 2. Equal-Information Baseline and Anti-Memory Design

- **Equal-information explicit-distribution baseline (`dist_a/`, `dist_b/`)**: Shows the same displayed `sRGB8` swatch, palette stop colours, target event stop membership, queried model scope (`exact`, `srgb8`, or `linear8`), and the two extremal compatible stop distributions (stacked bars plus per-stop fractions for exact cases, or 2-decimal percentages for rounded-observation cases). It omits precomputed `[p_min, p_max]` intervals, `[pct_lo, pct_hi]` summaries, and `EXACT`/`BOUNDED`/`UNIDENTIFIABLE` status badges.
- **Atlas view (`atlas_a/`, `atlas_b/`)**: Generated directly by `render_legend.render_atlas` with `srgb8` and `linear8` modes.
- **No same-case second-view memory advantage**: A reader never evaluates the same case in both views. One reader inspects one set in Distribution view and the matched opposite set in Atlas view:
  - **Order 1 (default for the first non-author reader)**: read `comparison/dist_a/index.html` first (`H1A`–`H5A`), seal Set A responses, then read `comparison/atlas_b/first_legend.html` (`H1B`–`H5B`). Reading the baseline first prevents Atlas status formatting from priming baseline interpretation.
  - **Order 2 (for a second non-author reader, if run)**: read `comparison/atlas_a/first_legend.html` first (`H1A`–`H5A`), then `comparison/dist_b/index.html` (`H1B`–`H5B`).

## 3. What This Design Can and Cannot Compare

- **Can compare**:
  1. Whether an uncoached non-author recovers `p_min`, `p_max`, identifiability status (`EXACT` / `BOUNDED` / `UNIDENTIFIABLE`), and boundary answers (`Q4`) more accurately with the Atlas view than with explicit distributions alone on matched held-out cases.
  2. Whether the Atlas reduces arithmetic/aggregation errors, prevents reading ambiguous/unidentifiable colours as determinate, and improves self-rated clarity (`1–5`) on real 390 px phone and 1280 px desktop browser views.
- **Cannot compare**:
  1. **Within-item paired differences** for a single reader, because each case is shown in only one view to prevent memory carryover; in a one-reader run, view effects and residual Set A vs Set B difficulty differences cannot be separated statistically.
  2. **Population significance**: One or two non-author readers provide a structured assessment, not a powered sample study.
  3. **Colour-only inference**: Neither view asks a reader to invert an RGB hex code mentally without distributions or bounds.
  4. **Calibrated hardware, timing, or unsupported pipelines**: Headless browser captures do not measure physical monitor calibration or human reaction time, and compression, alpha compositing, colour profiles, and encoded-space blending remain out of scope.

## 4. Non-Author Assessment Procedure (No Coaching)

1. **Before opening keys or certificates**: Read only this file and `comparison/prompts.json`. Do **not** open `comparison/keys/`, `comparison/certificates/`, `comparison/inputs/`, or `atlas_*/witnesses.json`.
2. **Inspect the assigned views**: Use the house `view` tool (at 390 px phone and 1280 px desktop) on your two assigned HTML files in order (`dist_a/index.html` then `atlas_b/first_legend.html` for Order 1). Confirm whether text, bars, and controls are readable without clipping, overflow, or script errors.
3. **Record and seal first-pass responses**: Answer `Q1`–`Q5` for all 10 assigned items (`5` per view) in a JSON file matching the schema below, and record its SHA-256 hash (or post the sealed summary) **before** opening any key or certificate file.
4. **Score**: Run:
   ```sh
   python3 projects/what-a-blended-colour-can-say/comparison.py score <sealed_responses.json>
   ```
5. **Reconstruct and verify**: Independently verify `comparison/certificates/set_a_certificates.json` and `set_b_certificates.json` with `verify_atlas.py` (no optimizer), check at least the extremal/Radon witnesses directly from rational arithmetic, and rerun deterministic regeneration:
   ```sh
   python3 projects/what-a-blended-colour-can-say/comparison.py
   ```

## 5. Exact Prompts (`Q1`–`Q5`)

For each case in `comparison/prompts.json`, answer under the specified model scope (`exact`, `srgb8`, or `linear8`):

- `q1_p_min`: Minimum compatible event probability (`p_min`, as a fraction like `2/5` or percentage like `40%`).
- `q2_p_max`: Maximum compatible event probability (`p_max`, as a fraction or percentage).
- `q3_status`: One of `EXACT` (`p_min == p_max`), `BOUNDED` (`0 < p_max - p_min < 1`), or `UNIDENTIFIABLE` (`[0, 1]`).
- `q4_probe`: `YES` or `NO` to the case-specific threshold prompt in `comparison/prompts.json`.
- `q5_clarity`: Integer `1` (confusing/unusable) to `5` (immediately clear), plus an optional brief readability note.

Sealed response JSON schema:

```json
{
  "order": "dist_a_then_atlas_b",
  "phone_desktop_ok": true,
  "dist_view": {
    "H1A": {"q1_p_min": "...", "q2_p_max": "...", "q3_status": "...", "q4_probe": "...", "q5_clarity": 3}
  },
  "atlas_view": {
    "H1B": {"q1_p_min": "...", "q2_p_max": "...", "q3_status": "...", "q4_probe": "...", "q5_clarity": 5}
  }
}
```

## 6. Pre-Registered Scoring and Decision Criteria

Each case contributes `4` objective points (`q1_p_min` within `±0.005`, `q2_p_max` within `±0.005`, exact `q3_status`, exact `q4_probe`), giving `0..20` per view.

- **PASS (supports M3 publication)**:
  - `phone_desktop_ok` is `true` (readable phone & desktop views, no clipping/overflow/script errors);
  - Atlas score `>= 17/20` with `5/5` on `q3_status` (including `UNIDENTIFIABLE`);
  - Mean Atlas `q5_clarity >= 4.0`; AND
  - Either Atlas beats Distribution baseline by `>= +2` points, **or** both score `>= 18/20` and Atlas beats Distribution mean `q5_clarity` by `>= +1.0`.
- **INCONCLUSIVE (do not publish as M3 pass without follow-up)**:
  - Atlas meets accuracy (`>= 17/20`, `5/5` status) and clarity (`>= 4.0`) and `phone_desktop_ok`, but does not clear the improvement margin over the baseline (e.g., an accuracy/clarity tie).
- **FAIL (rejects M3 publication)**:
  - `phone_desktop_ok` is `false`, OR Atlas score `< 17/20`, OR any `q3_status` error (especially missing `UNIDENTIFIABLE`), OR mean Atlas `q5_clarity < 4.0`, OR Distribution baseline scores strictly higher than Atlas.

## 7. Regenerate and Test

Using Python's standard library from the repository root:

```sh
python3 projects/what-a-blended-colour-can-say/comparison.py
python3 projects/what-a-blended-colour-can-say/comparison.py verify
python3 projects/what-a-blended-colour-can-say/verify_atlas.py projects/what-a-blended-colour-can-say/comparison/certificates/set_a_certificates.json
python3 projects/what-a-blended-colour-can-say/verify_atlas.py projects/what-a-blended-colour-can-say/comparison/certificates/set_b_certificates.json
python3 -m unittest discover -s projects/what-a-blended-colour-can-say -p 'test_*.py'
```
