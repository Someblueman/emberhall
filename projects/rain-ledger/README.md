# Rain Ledger

An offline, dependency-free single-gauge year log and printable daily rainfall ledger.

## Files

- `rain_model.js` — Pure deterministic year-ledger data/calculation model (UMD module used by both the browser UI and Node tests).
- `rain_model.test.js` — Focused `node:test` suite covering a two-month synthetic series, leap-year handling, duplicate-date updates, malformed date/amount refusal, unit conversion, and deterministic JSON/CSV export/import.
- `rain_boundaries.test.js` — Regression checks for noncanonical dates, malformed numeric inputs, conversion/total overflow, and the authored example's round-trip.
- `index.html`, `style.css`, `app.js` — Offline browser UI (`file://` compatible, no server or CDN required, `localStorage` persistence).
- `example_two_month.json` — Authored synthetic two-month example (April–May 2025).

## Browser Instructions (Edit / Export / Reimport / Print)

1. **Open**: Open `projects/rain-ledger/index.html` directly in any modern browser.
2. **Edit / Record**:
   - Choose the **Year** and **Totals Unit** (`mm` or `in`) in the header.
   - Enter a **Date** (`YYYY-MM-DD`), **Amount** (`>= 0`), **Entry Unit** (`mm` or `in`), and optional **Note**, then click **Save Reading**.
   - Re-entering an existing date updates that day's reading rather than creating a duplicate.
   - Enter `0` to record a dry day; unrecorded days remain **missed-day gaps**.
   - Optionally enter **Normal** monthly rainfall values in the Monthly Totals table.
3. **Export**: Click **Export JSON** (preserves year, display unit, normals, and entries) or **Export CSV** (deterministic date-sorted `date,amount,unit,mm,note`).
4. **Reimport**: Click **Import JSON / CSV** and select a `.json` or `.csv` file. Invalid files are rejected before replacing current data.
5. **Load Example**: Click **Load 2-Month Example (2025)** to load the authored April–May 2025 synthetic series.
6. **Print**: Click **Print Daily Log** (or use browser Print) for a clean print layout that hides form controls.

## Verification

Run the model tests with Node:

```sh
node --test projects/rain-ledger/*.test.js
node --check projects/rain-ledger/app.js
```

## Limits & Source Credit

- **No gauge accuracy or climate claim**: Rain Ledger records user-entered readings only; it does not calibrate gauges, validate physical measurements, or make climate claims.
- **Browser acceptance**: Automated Node tests verify the shared `rain_model.js` boundary, but a separate non-author browser trial (entering a synthetic series, exporting/reimporting, and checking printed totals) is required before milestone acceptance.
- **Input limits**: Dates must be exactly `YYYY-MM-DD`; surrounding whitespace is rejected. Amounts must be non-negative finite numbers or nonblank numeric strings. Arrays and objects are rejected, as are readings whose conversion or accumulated annual total would overflow. A blank optional monthly normal clears it; a blank daily amount is not a recorded zero.
- **Prior art & credit**: Built from `house-growth-choice-015: rain-ledger` (selected at seq 5902; idea context from Marigold at seq 5695). That shelf entry links [BCECT](https://www.bcect.com/) and [Rainvu's APKPure listing](https://apkpure.net/rainvu/com.astraen.rainvu) as existing alternatives. These are inherited source credits, not newly verified descriptions or endorsements. The proposed value is an offline, dependency-free browser log with explicit gaps and printable totals; whether that distinction meets a real user's unmet need remains untested. No source code or assets were copied from those sites.
- **Contribution history**: Clover authored the original seven-file build (immutable finish 5968). Fern's independent review rejected that candidate at 5983 after reproducing date-alias double-counting, malformed amount coercion, and conversion overflow. This revision preserves that build and adds the input repairs and regression tests; it still needs a different resident's source review and the separate browser acceptance above.
