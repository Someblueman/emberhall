# Sow Ledger

Turn a small Markdown seed inventory into a dated, ordered JSON report. Python
3.10+ and its standard library are sufficient; no house runtime, dependency,
account or network is used. The ledger remains the editable source of truth.

From the repository root:

```sh
python3 -B projects/sow-ledger/sow_ledger.py projects/sow-ledger/example.md \
  --as-of 2026-11-15 --output /tmp/sow-ledger-example.json
python3 -B -m unittest discover -s projects/sow-ledger -v
```

Both `--as-of` and `--output` are required. The command never reads today's date.
Success is exit **0**, with JSON in the output file and no stdout. Invalid input,
invalid arguments or an I/O failure return **2** with a diagnostic on stderr.
Handled interruption returns **130**; inspect the output before retrying because
an interruption can arrive after the complete report was published.

## Supported Markdown

The format is intentionally small: optional `# Title` lines before exactly one
six-column table, using these exact column names and order:

```markdown
# My seed drawer

| variety | harvest_year | quantity | germination | sow_by | shelf_life_years |
| --- | --- | --- | --- | --- | --- |
| Garden pea | 2024 | 42 | 9/12 | 2026-03-15 | - |
| Lettuce mix | 2025 | 120 | 0/8 | - | 2 |
| Mystery marigold | - | - | - | - | - |
| Red onion | 2023 | 0 | 1/3 | - | - |
```

At least one data row is required. Every row needs the surrounding pipes and six
cells. Blank lines and cell-edge spaces are ignored; separator cells allow three
or more dashes with optional Markdown alignment colons. Trailing prose, additional
tables, renamed headers, escaped pipes, multiline cells, tabs, other control
characters and Markdown code fences are unsupported and rejected. Cell text is
literal; Markdown emphasis and links are not interpreted. Files must be UTF-8
without a BOM, at most 1,000,000 bytes, and regular files rather than symlinks or
special files. Symlinks in parent directories are allowed.

| Column | Meaning |
| --- | --- |
| `variety` | Nonempty unique name, excluding a lone `-`. Names are NFC-normalized and compared with Unicode case folding; write separate varieties as separate rows. Multiple lots of the same variety are outside this format. |
| `harvest_year` | Four-digit year from `0001` to the injected date's year, or unknown. Future harvest years are rejected. |
| `quantity` | Count of seeds remaining, or unknown. Zero is a known empty stock; packets and fractional quantities are unsupported. |
| `germination` | Measured germinated/tested counts `n/m`, with `0 <= n <= m` and `m > 0`, or unknown. No spaces within the ratio. The tested sample is independent of the remaining quantity. |
| `sow_by` | User-supplied calendar date `YYYY-MM-DD`, or unspecified. Past dates are retained, not automatically discarded. |
| `shelf_life_years` | User-supplied whole-year assumption, requiring a known harvest year, or unspecified. Do not supply this together with `sow_by`. |

An empty cell or `-` means unknown/unspecified, except for the required variety.
All counts and shelf-life years accept decimal integers `0` to `9999999999`;
leading zeroes are accepted. An assumed end year must also fit within `9999`.
Dates require the exact zero-padded form and must be valid Gregorian dates.

## Calculations and output contract

The output has `version: 1`, `as_of`, and `entries`. Every entry contains the same
keys, including explicit JSON `null` for unknowns:

```json
{
  "variety": "Garden pea",
  "harvest_year": 2024,
  "age_calendar_years": 2,
  "quantity": 42,
  "germination": {"germinated": 9, "tested": 12, "percent": "75.00"},
  "sow_by": "2026-03-15",
  "sow_by_source": "explicit_date",
  "shelf_life_years": null
}
```

Age means **as-of year minus harvest year**, not elapsed whole years since an
unknown harvest day. Germination percentage is a decimal string with two places,
rounded half up: `1/3` gives `"33.33"`; `0/8` gives `"0.00"`; missing measurement
gives `null` for the entire germination object. No unmeasured rate is estimated.

A shelf-life assumption computes **December 31 of harvest year + supplied years**.
For the example lettuce, `2025 + 2` produces `2027-12-31`, with
`sow_by_source: "user_shelf_life_assumption"` and `shelf_life_years: 2` retained.
This is a documented ordering convention, not a discovered expiry date. Without
an explicit date or assumption, `sow_by` and `sow_by_source` stay `null`, even when
the harvest year is known. The program contains no species-specific rules.

Entries sort by known sow-by date ascending, then case-folded variety; unknown
dates come last, also by variety. Original table order does not affect output.
Thus the worked example produces Garden pea, Lettuce mix, Mystery marigold, Red
onion. Red onion has known age but no inferred deadline. JSON is UTF-8, uses sorted
object keys and two-space indentation, and ends in one newline. Fixed ledger
contents and date produce identical bytes; there is no timestamp or input path.

## Publication and limits

The complete input is validated and JSON serialized before writing. The output's
parent must already exist. Existing output must be a regular file, not a symlink,
directory or special file; input and output may not identify the same file,
including through hard links. The command writes a private temporary file beside
the destination, flushes and fsyncs it, then publishes via one `os.replace`.
Replacement creates a file with the temporary file's restrictive permissions
(typically `0600` on POSIX); it does not preserve the old file's metadata.

Malformed inputs and failures before replacement preserve existing output bytes.
Temporary files are cleaned on ordinary failure or handled interruption. This is
an atomic visible replacement on a filesystem supporting same-directory replace,
not a power-loss durability promise; the parent directory is not fsynced. Use a
quiescent ledger and destination. Concurrent edits, concurrent writers and hostile
path replacement are outside the contract. No files other than the explicit
output and its temporary staging file are intentionally written.

The worked ledger is illustrative, not a real stock or germination observation.
This is inventory arithmetic and explicit user ordering, not biological advice,
a seed-viability forecast or evidence that sowing by a date will work. No network
or horticultural source is required for these calculations.

The tests cover format/duplicate/measurement failures, explicit unknowns, date
ordering, fixed-date byte repeats, real subprocess errors, special-file refusal,
and injected fsync/replace failures preserving an existing report. Independent
non-author source acceptance and a separate run on a real manually authored
ledger remain necessary before the project owner assesses closure. A builder's
worked example and passing tests satisfy neither independent requirement.
