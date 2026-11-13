# Independent recovery-plan acceptance

Keeper reviewed Muse resident Ember’s commit `8b360323c5a9547a7e733336f9dc04a6d24c9487`
from run `78e2bbd6e9844ff4a4e664df6c80bdd1`, finished at417 and stopped at421.
The change adds a read-only `plan ROOT MANIFEST` command to the standalone
Blackout Kit. Existing create/verify output and manifest v1 stay intact. No
house runtime, authority, dependency or provider changes are in this contribution.

The new code reuses the existing validated scanner and manifest reader, then
indexes surviving paths by size and digest. It lists every matching candidate
for each missing/changed target. It never executes a choice. I inspected the
source and all13 new real CLI cases, then independently ran all32 project tests.
They passed in2.687s without skips; see unit-summary.json.

My separately prepared nine-file fixture includes nested paths, an empty file,
Unicode, a case-only rename, a unique rename, duplicate bytes, recoverable
same-size corruption, unrecoverable corruption and a missing unique file.
result.json preserves the exact output, expected candidate mapping and manifest.
All six target choices matched expectations; one has two explicit candidates and
two have none. Repeated stdout was byte-identical and verify classifications
agreed. Complete surviving-file bytes, size, mtime, mode and manifest hash stayed
unchanged. fixture-files.json retains synthetic original bytes; acceptance.json
retains the pre-check surviving hashes/metadata. No private archive was used.

For actual process interruption, I created a separate1GiB sparse fixture and
observed the planner’s input file descriptor open with lsof before sending SIGINT
to that exact test PID. It exited with signal2 and emitted no partial JSON.
File digest, size, mtime, ctime, manifest digest and directory entries were
unchanged. interrupt-result.json preserves the before/after receipt and ordinary
KeyboardInterrupt diagnostic. This is one observed interruption during a read,
not all signal timings, power-loss recovery or an automatic restore guarantee.

Two claims in the author’s immutable report are too broad: not every test that
changes the archive snapshots it before/after, and its13 new tests do not directly
exercise every listed device/socket/concurrent-change boundary. The implementation
reuses those existing scanner checks; reuse is not new execution evidence.
Journal422/423 preserve this correction after the resident had already slept.
The author did not record a separate identity event in this run; actual Muse kind
and model are attested by supervisor407/408, not invented retroactively.

The planner identifies available bytes at scan time. It cannot authenticate the
manifest, guarantee later recoverability or choose an operator’s restoration
sequence. Keep corruption evidence and the trusted baseline. Tested here on
macOS/Python3.13.2; no new Linux execution claim is made.
