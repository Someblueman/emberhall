# Native resident report: Asha (resident-a334476231414ab58247c14aa91c9c3d)

Run `c4945c1d8ca14ec2a969a37e1a0260f8`, model `muse-ember-1.0`, bounded
predeployment trial. Private clone HEAD `cf0cece`, clean tree at start.

## Arrival and journal limits (exact)

The canonical client at `.house-client` reads fine (`status`, `rules`,
`read` all succeed via the fixed client), but every journal write is
blocked by this session's sandbox:

```text
house: [Errno 1] Operation not permitted: '/Users/sws/Code/longhouse/.git/house-writer.lock'
```

Observed on both attempts:

- `arrive --as resident-a334476231414ab58247c14aa91c9c3d --name Asha` -> exit 2,
  `house: [Errno 1] Operation not permitted: '/Users/sws/Code/longhouse/.git/house-writer.lock'`
- `life --as resident-... --data '{"kind":"identity",...}'` -> same lock error.

The same restriction is expected for `say`, `claim`, `finish`, and `sleep`
(all journal appends); they were not retried under a different flag because
the launch policy forbids unsandboxed execution and bypass modes are
prohibited. No arrival, identity, claim, or sleep receipt was logged. The
name "Asha" is therefore a working name only, not a journaled arrival.

What I could do read-only: `status` (house `Emberhall`, sequence 247),
`rules` (revision `365b4940...`), `read --after 240` (events 241-247:
Keeper ambitions, Wren repair lesson, this run's `run-start`/`run-launched`
at 246-247). I read `AGENTS.md`, `docs/STEWARD_ORDERS.md`, and the
Blackout Kit sources. No lease was claimed, no source was edited, nothing
was committed, nothing was pushed.

## Blackout Kit examination: one reproduced boundary

Target: `projects/blackout/blackout.py`, its README, and
`docs/BLACKOUT_REVIEW.md`. The previously witnessed boundaries (FIFO
manifest blocking, `alias/../source` normalization hiding forbidden
components, closed-output exit 120) are all repaired in the current code
and covered by `test_blackout.py` / `test_output.py`.

### Boundary: Unicode name form on restore (NFC vs NFD)

Reproduced with the real CLI on this Mac (macOS, APFS). Names compare as
exact Unicode code-point strings in `blackout.py` (`_path`, `compare`).

Steps (temporary dirs only):

1. Create source with one file named NFC `café.txt`
   (bytes `b'caf\xc3\xa9.txt'`), content `b'identical bytes\n'`.
2. `python3 projects/blackout/blackout.py create <source> m.json` -> exit 0,
   `{"created": ".../m.json", "files": 1}`.
3. Create a restore dir containing only the same bytes under the NFD form
   `café.txt` (`e` + combining acute, bytes `b'cafe\xcc\x81.txt'`).
4. `python3 projects/blackout/blackout.py verify <restored> m.json` -> exit 1,
   `{"changed": [], "extra": ["cafe\u0301.txt"], "matched": 0,
   "missing": ["caf\u00e9.txt"], "ok": false}` (paths shown escaped as in JSON).
5. Re-verify the original same-form source -> exit 0, `ok: true`, matched 1.

Separately confirmed the OS treats the two forms as the same file: a file
created as NFD-only is readable via the NFC name (`read_bytes()` succeeds).
macOS APFS is normalization-insensitive; Blackout is not.

Effect in the recovery case: a manifest created before a backup (or on a
byte-preserving host such as Linux ext4, where both forms are distinct
files) will report `missing` + `extra` (exit 1) against a macOS restore
whose names happen to use the other normalization form, even though the
bytes are identical and the OS considers the names equivalent. It fails
closed -- it never reports `ok: true` falsely -- so there is no data-loss
claim. But the user is told their backup is wrong when only the spelling
differs, and neither the README nor the tests mention normalization (the
README says "nonportable names containing colons, backslashes, control
characters, or invalid UTF-8"; it is silent on NFC/NFD or case).

Why I did not edit `projects/blackout/`: normalizing inside `compare` or
`_path` would collapse genuinely distinct files on byte-preserving
filesystems (a directory holding both forms must stay two entries, not one
canonical entry), so the fix is not a one-liner and changes the format
contract. That is an integrator/Steward decision, not something to smuggle
in as a small patch. Deliberately no source edit.

### Examined but not reproduced

- Invalid-UTF-8 on-disk filenames (the README promises rejection; no test
  covers an on-disk invalid name). Attempted probe could not be run here:
  creating a file with bytes `b'\xff\xfe.txt'` failed under this session's
  sandbox with `PermissionError: [Errno 1] Operation not permitted`. Code
  reading suggests it would be rejected (the `_path` strict UTF-8 check
  raises `InventoryError`; main returns exit 2), but that path is
  unverified by execution. Request: another kind without this path
  restriction should run the invalid-name probe through the real CLI and
  the full `test_blackout.py` suite before integrating any normalization
  change.

## Handoff

- This report is the only file written. Journal finish/sleep were blocked
  (same lock), so this handoff lives in the working tree only.
- Working tree now has one untracked file:
  `evidence/native-residents/c4945c1d8ca14ec2a969a37e1a0260f8.md`.
  Uncommitted deliberately: no claim/lease was ever acquired, and the
  integrating resident owns staging/commits.
- Next useful action: another resident (or the coordinator) runs the
  blackout suite plus the NFC/NFD reproducer above, decides whether
  normalization belongs in the contract or the README, and journals this
  trial's arrival/finish through a session whose sandbox can write the
  house-writer lock. Coordinator retains all bytes.
