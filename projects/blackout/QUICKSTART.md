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

## Compare two saved inventories without a backup

`diff OLD_MANIFEST NEW_MANIFEST` answers "what changed between these two backup dates?" using two manifests you already saved. It reads no archive at all, so it works when neither disk is mounted. `OLD` is the baseline; `NEW` is the later inventory.

This recipe writes two small invented manifests to a fresh temporary directory and runs from the extracted kit root (or a source checkout root). No real archive, credential, or backup is touched. The records are in different orders on purpose to show that order does not matter.

```sh
D=$(mktemp -d "${TMPDIR:-/tmp}/blackout-diff.XXXXXX") || exit
D=$(cd "$D" && pwd -P) || exit

cat > "$D/old.manifest.json" <<'JSON'
{
  "format": "blackout-kit",
  "version": 1,
  "files": [
    {"path": "letters/kept.txt", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    {"path": "notes.txt", "size": 5, "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"},
    {"path": "photos/cat.jpg", "size": 1, "sha256": "ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb"},
    {"path": "records/invoice.txt", "size": 0, "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"}
  ]
}
JSON

cat > "$D/new.manifest.json" <<'JSON'
{
  "format": "blackout-kit",
  "version": 1,
  "files": [
    {"path": "photos/dog.jpg", "size": 5, "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"},
    {"path": "letters/kept.txt", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"},
    {"path": "notes.txt", "size": 5, "sha256": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"},
    {"path": "photos/cat.jpg", "size": 3, "sha256": "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"}
  ]
}
JSON

python3 projects/blackout/blackout.py diff "$D/old.manifest.json" "$D/new.manifest.json"
echo "exit: $?"
```

Expected output, with exit **1** because the inventories differ:

```json
{"changed": ["photos/cat.jpg"], "extra": ["photos/dog.jpg"], "matched": 2, "missing": ["records/invoice.txt"], "ok": false}
```

Two files are unchanged, `photos/cat.jpg` has a different recorded size and SHA-256, `records/invoice.txt` is absent from NEW, and `photos/dog.jpg` is new. Now compare a manifest with itself:

```sh
python3 projects/blackout/blackout.py diff "$D/old.manifest.json" "$D/old.manifest.json"
echo "exit: $?"
```

```json
{"changed": [], "extra": [], "matched": 4, "missing": [], "ok": true}
```

That is exit **0**. Reversing the arguments flips the direction: `diff "$D/new.manifest.json" "$D/old.manifest.json"` reports `photos/dog.jpg` as missing, `records/invoice.txt` as extra, and still reports `photos/cat.jpg` as changed.

`diff` compares recorded claims only. It does not verify either backup's current bytes, does not guess renames, and never changes a manifest or archive. Exit **2** means an unsafe or malformed manifest or a failed output stream; exit **130** means a handled interrupt. See `README.md` for the full boundary.

## What the checker preserves

`verify` and `plan` preserve the input archive: they never copy, rename, overwrite, or delete inside the scanned directory. `create` writes one new manifest outside the source (and refuses to overwrite it). `diff` reads two saved manifests and changes neither. The checker never chooses among identical candidates and never proves filename or history from bytes alone.

Keep the manifest on a separate device or authenticated store. The manifest is your trusted baseline.
