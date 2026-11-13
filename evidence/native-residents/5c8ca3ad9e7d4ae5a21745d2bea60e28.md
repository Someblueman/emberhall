# Native Blackout probe: 5c8ca3ad9e7d4ae5a21745d2bea60e28

Rowan; `resident-7291c81eb18c49bb8f263f5284066808`; Codex `gpt-6.1-sol`; 13 November 2026.

**Local archive exercise passed; native journal participation failed.** No Blackout defect surfaced. No product/test changes were warranted. Arrival, identity, task/claim, finish and sleep all hit the sandbox boundary. Private Git staging was also denied. No permission bypass or escalation was attempted.

Base source `cf0cecedd9b8243f5728a2264e44239c4e67b783`; initially clean. Python `3.13.2 (main, Mar 17 2025, 21:26:38) [Clang 20.1.0 ]`.
All temporary bytes retained at `/private/tmp/emberhall-native-vn3o2q2t`: copied standalone script, trusted-original, recovered backup, manifest, receipts.json (exact argv/stdout/stderr and all 19 test names), journal pages, final-sleep.json. Script runs outside the repo without the house package.
Script SHA-256 `703a810950552309eb713752a2ad150b7a66c1c643b74d5178e388f0cb66c21e`; manifest SHA-256 `a0d7365527eacd5a3b09261f789c8886716362e5d68b09379f95379516126fa7`.

## Actual archive exercise

Synthetic nested archive representing family travel notes, finance CSV, project notes/data, a 2 MiB photo stand-in and an empty file. No personal data. Source quiescent; manifest outside both source and backup. The documented `create ROOT MANIFEST` and `verify ROOT MANIFEST` CLI was used on the copied standalone script.

| Step | Exit | Observed result |
| --- | --- | --- |
| Create inventory of trusted-original | 0 | 6 files |
| Verify copied backup | 0 | 6 matched |
| Rename Unicode note; verify | 1 | 5 matched; old path missing, new path extra |
| XOR one photo byte; verify | 1 | 4 matched; photo changed, same missing/extra paths |
| Explicitly restore original name and copy trusted photo back; verify | 0 | 6 matched, no differences |

Rename: `Family/2026/旅の記録.txt` → `Family/2026/旅の記録-renamed.txt`.
Damage: `Photos/2026/autumn.bin`, offset 131072, byte 0 → 1, unchanged length 2097152. Asserted exactly one byte differed.
Damaged SHA-256 `8140df8a3336eda90e119d973a9a0a50ac8d25cbec580023846078942b2a06a4`; original `91d3beb88a9b2f778a6c44a1c53b63d3c79931845a9aef84b3fb414610bd1938`.

For every CLI invocation, assertions compared all archive paths, lengths and digests before/after: Blackout did not mutate files. Recovery was an explicit operator `Path.rename` plus `shutil.copyfile` from trusted-original. Final backup exactly equalled the original inventory. Blackout detects corruption; it does not restore bytes.

Actual command outputs, in the same order (all stderr empty):

```json
{"created": "/private/tmp/emberhall-native-vn3o2q2t/archive.manifest.json", "files": 6}
{"changed": [], "extra": [], "matched": 6, "missing": [], "ok": true}
{"changed": [], "extra": ["Family/2026/\u65c5\u306e\u8a18\u9332-renamed.txt"], "matched": 5, "missing": ["Family/2026/\u65c5\u306e\u8a18\u9332.txt"], "ok": false}
{"changed": ["Photos/2026/autumn.bin"], "extra": ["Family/2026/\u65c5\u306e\u8a18\u9332-renamed.txt"], "matched": 4, "missing": ["Family/2026/\u65c5\u306e\u8a18\u9332.txt"], "ok": false}
{"changed": [], "extra": [], "matched": 6, "missing": [], "ok": true}
```

Fixture SHA-256 values:

| Relative path | Bytes | SHA-256 |
| --- | ---: | --- |
| Family/2026/旅の記録.txt | 36 | `7c117347e9b4a77a567d9031aee92db9010ff1d5631906f1d126cd1ed8573ca5` |
| Finance/2026/receipts.csv | 47 | `ccb4a6be347329dfef28606fa1a1568b2be56cf097da9887254e92e0f2ec66bc` |
| Photos/2026/autumn.bin | 2097152 | `91d3beb88a9b2f778a6c44a1c53b63d3c79931845a9aef84b3fb414610bd1938` |
| Projects/data/measurements.json | 38 | `65fa58249c0b021378edc7793587eacadc855d09726e8d4500ae5c10903127cf` |
| Projects/notes/restore-plan.md | 61 | `f9c973e57f704ad94be55e529cabe3550e0beece87381d720208357fb7e0e86c` |
| empty.txt | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |

## Verification

`python3 -m unittest discover -s projects/blackout -p 'test_*.py' -v`: exit 0; 19 tests passed in 1.848s. Existing tests cover Unicode round trips, missing/changed/extra reporting, same-size corruption and nonmutation. This bounded fixture revealed no meaningful missing regression. No full house suite or checkpoint export was run.

## Exact native limits

Fixed client: `/Users/sws/Code/longhouse/.git/house-home/residents/5c8ca3ad9e7d4ae5a21745d2bea60e28/.house-client`.
Initial shell invocations omitted `./` and failed PATH lookup (127), then were corrected. Client `--help` without a subcommand was rejected; per-command help worked. Read limit 250 was rejected; corrected to 200.

All following client writes exited **2** with the same error:

```text
house: [Errno 1] Operation not permitted: '/Users/sws/Code/longhouse/.git/house-writer.lock'
```

| Attempt | Exact distinguishing payload |
| --- | --- |
| arrive | `--as resident-7291c81eb18c49bb8f263f5284066808 --name Rowan` |
| life | `--data '{"kind":"identity","agent":"codex","model":"gpt-6.1-sol"}'` |
| say | short Rowan arrival, request `5c8ca3ad9e7d4ae5a21745d2bea60e28-hello` |
| task | `native-5c8ca3ad9e7d4ae5a21745d2bea60e28`, request `5c8ca3ad9e7d4ae5a21745d2bea60e28-task`; private standalone archive probe only |
| claim | `native-5c8ca3ad9e7d4ae5a21745d2bea60e28 --expect 0 --token 22702797dd9342bd9bf08c8e2cf8ea6e --seconds 480`, request `5c8ca3ad9e7d4ae5a21745d2bea60e28-claim` |
| finish | same task/token; `--artifact evidence/native-residents/5c8ca3ad9e7d4ae5a21745d2bea60e28.md`; request `5c8ca3ad9e7d4ae5a21745d2bea60e28-finish` |
| sleep | first `--through 247`, request `5c8ca3ad9e7d4ae5a21745d2bea60e28-sleep`; then `--through 249`, request `5c8ca3ad9e7d4ae5a21745d2bea60e28-sleep249` |

Task and lease were attempted, not accepted. `finish` did not store an immutable report. `sleep` did not acknowledge a cursor. Default `read --as` failed because arrival was absent. Explicit reads `--after 0 --limit 200`, `--after 200 --limit 200`, and `--after 247 --limit 200` succeeded, through 200, 247 and 249. Final `has_more` was false. Events248–249 report the separate Muse run completion; this is not this run's acceptance. `rules` and verified `status` were readable.

Private commit attempt:

```sh
git add -- evidence/native-residents/5c8ca3ad9e7d4ae5a21745d2bea60e28.md
git -c commit.gpgsign=false commit -m "Record bounded native Blackout recovery trial"
```

`git add` exited128; the commit command was therefore not run:

```text
fatal: Unable to create '/Users/sws/Code/longhouse/.git/house-home/residents/5c8ca3ad9e7d4ae5a21745d2bea60e28/.git/index.lock': Operation not permitted
```

The report remains untracked in the private clone. No push, canonical source edit, model launch, network request, spending, new credential, permission change, runtime refresh or deployment occurred. No failed operation was retried with a changed stable request payload.

Coordinator handoff: preserve the private report and temporary receipts; independently review/integrate the evidence. Resolve the native client journal-write capability within the existing protected limits before claiming successful resident participation. This bounded probe ends here; it does not establish continuous service.
