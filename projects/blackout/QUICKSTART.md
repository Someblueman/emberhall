# Blackout Kit — Quickstart

Blackout Kit checks whether a backup still has the bytes you saved. It needs only Python 3.10+ on macOS or Linux. No packages, no network, no account.

This quickstart uses a tiny invented example. All names and bytes are made up.

## What's in the offline kit

The kit preserves normal paths so the same commands work after extraction:

- `projects/blackout/blackout.py` — the standalone checker (preserves its input archive)
- `projects/blackout/README.md` — full technical guide
- `projects/blackout/QUICKSTART.md` — this file
- `projects/blackout/examples/recovery-drill/` — synthetic damaged backup, manifest, expected plan, and worksheet

Build a kit from a source checkout:

```sh
python3 projects/blackout/bundle.py build -o /tmp/blackout-kit.zip
```

Build from a quiet, unchanged source checkout. The builder uses fixed ZIP metadata
and uncompressed entries for reproducible bytes. It refuses to replace an existing
output and does not change source files. Standard library only; no claim of a
transactional snapshot of concurrently changing source files.

## Try the synthetic example from a fresh directory

If you are holding only the ZIP, extract it to a fresh unique directory and work there so the synthetic tree stays pristine. This uses a fresh `mktemp` directory with physical-path resolution so the checker does not trip on a `/tmp` alias:

```sh
KIT=$(mktemp -d "${TMPDIR:-/tmp}/blackout-kit.XXXXXX") || exit
KIT=$(cd "$KIT" && pwd -P) || exit
python3 -m zipfile -e /path/to/blackout-kit.zip "$KIT" || exit
cd "$KIT" || exit
python3 projects/blackout/blackout.py verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
python3 projects/blackout/blackout.py plan projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json
```

Both exit **1** on purpose. Exit 1 means the tool ran and found a mismatch — expected for a damaged backup. Exit 0 means all bytes matched with no extra. Exit 2 means unsafe/malformed input or system error.

The drill is damaged on purpose:

- `family/winter.txt` missing, bytes survive as `family/renamed-winter.txt`
- `photos/Report.txt` missing, bytes survive as `photos/report.txt` (case matters)
- `records/copy-a.txt` missing, two files have identical bytes — flagged ambiguous, never guessed
- `records/invoice.txt` changed, spare survives as `spares/invoice-copy.txt`
- `family/summer.txt` changed, no surviving bytes — unrecoverable
- `letters/lost.txt` missing, no bytes survive — unrecoverable

`plan` output is sorted deterministic JSON. Compare to `expected-plan.json`. Copying recoverable targets to a fresh unique destination and re-running `verify` yields `matched: 7` and missing the two truly lost files.

Full copy rehearsal and checklist: `projects/blackout/examples/recovery-drill/recovery-worksheet.md`.

## What the checker preserves

`verify` and `plan` preserve the input archive: they never copy, rename, overwrite, or delete inside the scanned directory. `create` writes one new manifest outside the source (and refuses to overwrite it). The checker never chooses among identical candidates and never proves filename or history from bytes alone.

Keep the manifest on a separate device or authenticated store. The manifest is your trusted baseline.
