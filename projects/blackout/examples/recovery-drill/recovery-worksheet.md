# Salvage Recovery Worksheet — damaged-archive rehearsal

This worksheet maps the **Salvage drill** (`projects/blackout/examples/recovery-drill/`) to six explicit human decisions. It is a read-only rehearsal companion to `README.md`, `manifest.json` and `expected-plan.json`. All names and bytes are invented; no house, account or network is needed.

> **How this worksheet was built:** Actual route **muse / muse-ember-1.0**, resident `resident-019bca8ed8fd490eb908e4f82cc91213`, run `ee6cfec5d13a4da0868581ee794c161b`. The drill was read through restricted file tools (`README.md`, `manifest.json`, `expected-plan.json`, `original/` and `surviving/` bytes). As a fallback for the OpenCode invitation `salvage-native-opencode-worksheet`, this author *does* have a shell and did independently run:
>
> ```sh
> python3 projects/blackout/blackout.py verify projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json  # exit 1
> python3 projects/blackout/blackout.py plan   projects/blackout/examples/recovery-drill/surviving projects/blackout/examples/recovery-drill/manifest.json  # exit 1, JSON equal to expected-plan.json
> ```
>
> This is **not** a claim of shell execution by the shellless OpenCode route. Root validation remains independent.

> **Repair note (salvage-worksheet-review-fix-v1, sequence 611-613):** Keeper feedback 610 noted the original worksheet’s incomplete destination (only four recoverable targets) and a predictable `/tmp/recovered` path with two `cp` lines for the ambiguous target. This revision uses a **fresh uniquely-created destination** and lists **exactly one chosen candidate** for `records/copy-a.txt`. The seven-file destination was validated with disposable copies (see §8) and yields **7 matched / 2 missing** as required, without modifying the original fixture bytes.

## What happened in one view

- `verify` and `plan` exit **1** (mismatch, not a failure to run). Exit 1 is the expected result for a damaged backup.
- `verify` JSON: `matched: 3`, `missing: 4`, `changed: 2`, `extra: 4`.
- `plan` JSON adds `restores` (6 entries), `ambiguous: ["records/copy-a.txt"]`, `unrecoverable: ["family/summer.txt","letters/lost.txt"]`.

| File | Status | Plan verdict |
|---|---|---|
| `letters/empty.txt` (0 bytes) | matched | Keep — no action |
| `photos/snow ☃.dat` (256 bytes, bytes 0–255) | matched | Keep — no action |
| `records/copy-b.txt` (“shared archive bytes\n”) | matched | Keep — but also a candidate for `copy-a.txt` (see §2) |
| `family/winter.txt` (“Winter record\n”, 14 bytes) | **missing** | Recoverable: `family/renamed-winter.txt` (unique, unambiguous) |
| `photos/Report.txt` (“case-preserved record\n”, 22 bytes) | **missing** | Recoverable: `photos/report.txt` (case-only rename) |
| `records/copy-a.txt` (“shared archive bytes\n”, 21 bytes) | **missing** | **Ambiguous**: `records/copy-b.txt` and `spares/duplicate.txt` |
| `records/invoice.txt` expected (“Invoice: 173 units\n”, 19 bytes) | **changed** to 999 | Recoverable: `spares/invoice-copy.txt` (the 173 original) |
| `family/summer.txt` expected (“Summer record\n”, 14 bytes) | **changed** to “Summer damage\n” | **Unrecoverable** — no surviving bytes match |
| `letters/lost.txt` (“unique vanished bytes\n”, 22 bytes) | **missing** | **Unrecoverable** — no surviving bytes match |

Three files are already matched and need no recovery, though one of them (`records/copy-b.txt`) is also a candidate for a damaged target. The six damaged targets below require decisions.

## Ground rules — preserve and verify before you restore anything

The checker **never copies, renames, overwrites or deletes**. A recovery plan is a read-only list, not a restore. For a real archive you must:

1. **Preserve the original damaged archive.** Do not delete, rename or overwrite files in `surviving/` (or its real-world equivalent) to “make room” for the restore. Keep `original/` conceptually separate: the manifest is your trusted baseline, the surviving tree is your evidence. If you delete an `extra` file before checking, you destroy a candidate.
2. **Work in a fresh, unique destination.** Create a private, not-yet-existing directory with a random suffix (e.g. `mktemp -d /tmp/recovered-ember-019bca8e.XXXXXX`). Never reuse a predictable `/tmp/recovered` that may already exist or be occupied. Copy the *candidates* you choose into that fresh directory; never restore into `surviving/` — you would lose the evidence that proves the choice was correct.
3. **Verify after copying.** Run `verify`/`plan` against the destination and compare to the trusted `manifest.json`; compare `sha256` and `size` byte-for-byte. Keep the manifest separate from the destination.
4. **Treat the manifest as the baseline, not the archive.** You must keep the manifest on a separate device / authenticated store. A plan proves “these bytes equal the manifest”; it does not authenticate the manifest itself.

## Why identical bytes cannot prove filename or authenticity

Blackout’s candidate rule is: *any surviving regular file whose `size` and `sha256` are byte-identical to the expected entry for that target is a candidate*. A hash match is therefore **byte equality only**:

- It cannot prove the **filename**. `photos/report.txt` matching `photos/Report.txt` bytes shows the *bytes* survived under a different name; it does not prove that `report.txt` was originally `Report.txt`, or that the original author intended that casing. A case-only rename on a case-insensitive filesystem looks identical on disk yet is `missing`+`extra` in the exact-path inventory.
- It cannot prove **authorship or history**. Two files can have identical bytes and different creation times, owners, or stories. `records/copy-a.txt`, `records/copy-b.txt` and `spares/duplicate.txt` all contain the same 21 bytes (`73 68 61 …`); the hash cannot tell which, if any, is the “real” copy-a or whether duplicate bytes were created by a legitimate copy or a spoof.
- It cannot prove **ordering, labels or intent**. A rename, a copy, and a new file with recycled bytes are indistinguishable from bytes alone. The inventory intentionally keeps names exact, including case and Unicode normalisation (e.g. `snow ☃.dat`), because a new manifest would silently accept a rewritten history.
- It cannot prove the **manifest is trustworthy**. Anyone who can replace the manifest can also replace the expected checksums. Byte equality to an untrusted manifest is meaningless; the manifest needs its own provenance (signature, separate device, out-of-band trust).

The worksheet therefore keeps the human in the loop: the plan lists candidates; you decide.

---

## 1. `records/invoice.txt` — changed, recoverable

- **Manifest expects:** `Invoice: 173 units\n` (19 bytes, sha `963c25725b0c7ed9120cb5456380e62a2dcc3484c22e4d1aef772348c3d27b4b`).
- **Surviving file at that path:** `Invoice: 999 units\n` (same size, different bytes) → `changed`.
- **Candidate:** `spares/invoice-copy.txt` (`Invoice: 173 units\n`, 19 bytes, same sha) → listed as `recoverable: true`, `ambiguous: false`, `candidates: ["spares/invoice-copy.txt"]`.

**Uncertainty.** The surviving 999 file is not a candidate for itself — its bytes no longer match the manifest. The spare is byte-identical but lives under `spares/` as an `extra`. Is that spare a true backup or a planted decoy? The hash cannot tell you whether the 173 figure is the genuine invoice or a fabricated history that happens to have been recorded. The name `spares/invoice-copy.txt` is only a hint, not proof.

**Explicit human decision.** Do you trust that the 173 bytes in `spares/invoice-copy.txt` are the original invoice? If yes, copy *that file* to your fresh destination as `records/invoice.txt`. Do **not** overwrite the surviving 999 file in place. After copying, verify the destination’s sha equals `963c…` and keep the original 999 file and `spares/invoice-copy.txt` unchanged for later audit. If you do not trust the spare, mark this target as “needs external corroboration” and do not copy.

Use the single complete rehearsal in section8; it creates one fresh destination.

## 2. `records/copy-a.txt` — missing, **ambiguous** (two identical candidates)

- **Manifest expects:** `shared archive bytes\n` (21 bytes, sha `fc7f99045789bbc3055686b5a460ab962153ed70812e9902bad136ab83095ddf`).
- **Surviving path `records/copy-a.txt`:** absent → `missing`.
- **Candidates (both byte-identical):** `records/copy-b.txt` and `spares/duplicate.txt` — both 21 bytes, same sha. `ambiguous: true`, `recoverable: true`.

**Uncertainty.** This is the textbook identical-bytes ambiguity. `records/copy-b.txt` is listed as *matched* to its own manifest entry (it also has the same hash as `copy-a`), yet it cannot serve two targets in-place: the plan reuses candidates non-destructively, but the bytes do not tell you which story is right. Are `copy-a` and `copy-b` expected to be distinct files that happen to share bytes, or is `spares/duplicate.txt` a legitimate spare backup? The hash cannot decide. Copying either one to `copy-a.txt` in a destination yields the same bytes and the same `verify` success, but that does **not** prove you chose the correct provenance.

**Explicit human decision — exactly one choice recorded.** For the validated destination below, the chosen candidate is **`records/copy-b.txt`** (the matched file). The alternative `spares/duplicate.txt` is *not* also copied; the decision is logged as a human choice, not an algorithmic one. Do not delete either candidate — you may need it to prove the ambiguity later.

Use the single complete rehearsal in section8; it creates one fresh destination.

## 3. `family/winter.txt` — missing, recoverable (unique rename)

- **Manifest expects:** `Winter record\n` (14 bytes, sha `a77bdfb520c26056569e8fd3ace47af4c004b25e24e3f7c04daad94da948a0cb`).
- **Surviving:** no file at `family/winter.txt` → `missing`.
- **Candidate:** `family/renamed-winter.txt` (`Winter record\n`, 14 bytes, same sha) → `recoverable: true`, `ambiguous: false`.

**Uncertainty.** The match is byte-for-byte, but the name suggests a rename. Is the rename accidental (human rename) or a different file with coincidentally identical content? The hash cannot prove the *intended* name was `winter.txt` vs. `renamed-winter.txt`; it only proves these 14 bytes existed at manifest creation under the name `winter.txt`.

**Explicit human decision.** If you accept that `renamed-winter.txt` is the content you want, copy it to your fresh destination as `family/winter.txt`. Do not rename the surviving file in place.

Use the single complete rehearsal in section8; it creates one fresh destination.

## 4. `photos/Report.txt` — missing, recoverable (case-only rename)

- **Manifest expects:** `case-preserved record\n` (22 bytes, sha `165c35adc958d1ea1998969b61b0eac275d6d3c871d9ba7be4ece1fd451a85cf`) at path `photos/Report.txt` (capital R).
- **Surviving:** `photos/report.txt` (lowercase r) with identical bytes → `missing` (original) + `extra` (new spelling).
- **Candidate:** `photos/report.txt` → `recoverable: true`, `ambiguous: false`.

**Uncertainty.** On a case-insensitive filesystem (macOS APFS default, Windows) `Report.txt` and `report.txt` may open the same file today, but the exact-path inventory treats them as distinct. The hash match does not prove the filesystem preserves case for your restore destination. Copying may collapse two distinct source names into one destination name if you flatten directories.

**Explicit human decision.** Keep the capitalisation exactly as the manifest says when you write to the destination (`photos/Report.txt`), and keep original vs. case-variant trees separate during the drill (`original/` vs. `surviving/`). On your destination, choose a case-sensitive filesystem or a directory layout that cannot collide; verify the restored name’s case by `ls` after copying.

Use the single complete rehearsal in section8; it creates one fresh destination.

## 5. `family/summer.txt` — changed, **unrecoverable**

- **Manifest expects:** `Summer record\n` (14 bytes, sha `589ad252cb4602f0e12493445e335feb4d7e49044be096dea3ab94976b4357cd`).
- **Surviving:** `Summer damage\n` (14 bytes, different sha) → `changed`, `candidates: []`, `recoverable: false`.

**Uncertainty.** No surviving file matches the expected bytes. The current file is same-size corruption — the most dangerous kind because a superficial `ls` looks plausible. There is no candidate to choose, and the plan correctly lists this in `unrecoverable`.

**Explicit human decision.** Do **not** copy the damaged 14 bytes into a recovery destination as if it were `Summer record`. Preserve the damaged file as evidence (keep `surviving/family/summer.txt` intact), mark this target as “absent from surviving archive; needs external source or manual reconstruction from authorship — bytes cannot be invented by the checker.” A new manifest from a guess would hide the loss.

## 6. `letters/lost.txt` — missing, **unrecoverable**

- **Manifest expects:** `unique vanished bytes\n` (22 bytes, sha `8a6682bb4b78f11b97476b694e60090b8195dea3545598fc2e5d67657a08c06b`).
- **Surviving:** no file at `letters/lost.txt` → `missing`, `candidates: []`, `recoverable: false`.

**Uncertainty.** A unique file disappeared. No surviving file contains those 22 bytes (not even as an `extra`). Unlike `copy-a.txt`, there is not even an ambiguous choice.

**Explicit human decision.** Mark `letters/lost.txt` as lost. Do not synthesize its contents. The checker cannot recover what no longer exists anywhere in the surviving tree. Keep the manifest entry as the record of what was lost; the destination restore remains incomplete.

---

## 7. Matched files — no action, but copy them into the fresh destination before you expect 7 matched

- `letters/empty.txt` (0 bytes, sha `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`) — empty file, matched in both trees. It is the only file whose *bytes* are the empty string; any future empty file would share its hash too.
- `photos/snow ☃.dat` (256 bytes `00 01 … ff`) — Unicode filename, matched. Copy with the exact Unicode name and normalisation (NFC vs NFD matter on some filesystems).
- `records/copy-b.txt` — matched to itself, but doubles as a candidate for `copy-a.txt` (§2). Do not assume “matched” means “unrelated to damage.”

The four `extra` files (`family/renamed-winter.txt`, `photos/report.txt`, `spares/duplicate.txt`, `spares/invoice-copy.txt`) are precisely the candidate pool. Deleting “extras” before you copy the ones you need would erase the evidence.

A destination that contains **only** the four recoverable targets is still missing the three already-matched files, so `verify` would report `matched: 4` and `missing: 5` (the three matched plus the two unrecoverable), not the expected healthy state. To achieve a clean seven-file check you must **explicitly copy/preserve all three matched files** into the same fresh destination along with the four recoverable choices.

## 8. Post-copy verification — validated seven-file destination (Muse fallback execution)

Muse validated the seven-file recovery choices. Keeper then executed this exact complete example, with strict error handling and physical-path resolution added after finding that macOS temporary-directory aliases fail Blackout's no-symlink checks. Run it from the repository root in a fresh shell. It leaves the recovered files in the newly created directory; the final verify intentionally returns1 because two files remain missing.

```sh
set -eu
DEST=$(mktemp -d "${TMPDIR:-/tmp}/blackout-recovery.XXXXXX")
DEST=$(cd "$DEST" && pwd -P)  # Blackout rejects symlink components such as macOS /tmp
printf 'Recovery destination: %s\n' "$DEST"

# three already-matched files
mkdir -p "$DEST/letters" "$DEST/photos" "$DEST/records"
cp projects/blackout/examples/recovery-drill/surviving/letters/empty.txt "$DEST/letters/empty.txt"
cp "projects/blackout/examples/recovery-drill/surviving/photos/snow ☃.dat" "$DEST/photos/snow ☃.dat"
cp projects/blackout/examples/recovery-drill/surviving/records/copy-b.txt "$DEST/records/copy-b.txt"

# four recoverable targets (exactly one ambiguous choice: records/copy-b.txt for copy-a)
mkdir -p "$DEST/family" "$DEST/photos" "$DEST/records"
cp projects/blackout/examples/recovery-drill/surviving/family/renamed-winter.txt "$DEST/family/winter.txt"
cp projects/blackout/examples/recovery-drill/surviving/photos/report.txt "$DEST/photos/Report.txt"
cp projects/blackout/examples/recovery-drill/surviving/records/copy-b.txt "$DEST/records/copy-a.txt"  # chosen; spares/duplicate.txt NOT copied
cp projects/blackout/examples/recovery-drill/surviving/spares/invoice-copy.txt "$DEST/records/invoice.txt"

python3 projects/blackout/blackout.py verify "$DEST" projects/blackout/examples/recovery-drill/manifest.json
# exit 1, {"changed":[],"extra":[],"matched":7,"missing":["family/summer.txt","letters/lost.txt"],"ok":false}
```

Observed result (Muse fallback, 2026-11-13):

```text
{"changed":[],"extra":[],"matched":7,"missing":["family/summer.txt","letters/lost.txt"],"ok":false}
# exit 1 — expected, because the two unrecoverable targets are still absent
```

`plan` on the same destination would also report `matched:7` and `unrecoverable:["family/summer.txt","letters/lost.txt"]`. The destination has **no `extra` and no `changed`**, confirming that copying the three matched files plus the four recoverable choices yields the expected seven-file state for this fixture. The native validation rechecked the surviving classification (`matched:3/missing:4/changed:2/extra:4`). That check alone does not prove every input byte stayed unchanged; Keeper independently compared all fixture hashes and metadata before and after the complete rehearsal (see `evidence/room-growth/worksheet-validation.json`).

Checklist for a real restore:

1. `ls -R` the fresh destination and check exact case (`Report.txt` vs `report.txt`) and Unicode (`snow ☃.dat`) spellings.
2. Run `verify` (or `plan`) against the destination with the *trusted* manifest; expect `matched:7` and `missing:2` before you claim success. A destination with only the four recoverable targets would give `matched:4` and `missing:5` — that is the incomplete-destination error this revision repairs.
3. Keep the original `surviving/` and `original/` untouched. Record which candidate you chose for `copy-a.txt` (`records/copy-b.txt` here) and why. Keep a copy of the manifest separate from the destination.
4. If you later need a full `ok: true`, you must supply the two unrecoverable files from a source outside the surviving archive (a true backup, email attachment, or human reconstruction) — and note that source as new evidence, not as a `plan` invention.

## What this drill teaches

Blackout Kit tells you *which bytes are missing, changed or duplicated* and *where identical bytes survive today*. It does not restore, rename, choose for you, or prove filename/authorship. The Salvage Room worksheet makes that boundary explicit: four targets have byte-identical survivors that you may copy to a separate destination after a conscious choice, one requires a conscious choice between two identical copies, and two are gone. Preserve the damaged archive, write to a separate destination, and verify — exactly as the checker leaves the bytes for you to decide.

---
