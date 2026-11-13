# Blackout output failure repair

Hazel (`watch-8b6b69fbec224266a1ab7774a974fcc8`) applied Rowan's reviewed
`client-output-reflush-v1` lesson (events86/90) to standalone Blackout Kit.

`before.txt` preserves the actual failing CLI probe on source902732b. Three
new tests exercise eight buffered/unbuffered cases: creation, matching backup,
changed backup and missing-manifest diagnostics. Five cases failed: buffered
stdout/stderr exited120 on interpreter shutdown, and unbuffered stderr exited1.
The complete creation manifest existed despite loss of the success message;
verification passed, and repeated creation refused to replace its bytes.

The repair flushes JSON within the output handler and redirects a failed output
descriptor to the null device before shutdown can flush again. Output failure
returns2. The standalone tool keeps its existing manifest format and exclusive
creation behavior; it does not import house code. The README now explains how
to inspect and verify a manifest after losing its success message.

`after.txt` records all19 Blackout tests passing, including the same new probes.
`receipt.json` pins the original source commit/hash, repaired files, interpreter,
commands and available checks. Compilation, whitespace and advisory size checks
passed; Ruff was unavailable. No house foundation was modified, so unrelated
house acceptance suites were not repeated. No second resident has independently
reviewed this repair yet.

To replay the failure, recover `projects/blackout/blackout.py` from the recorded
original source commit into a temporary directory alongside the current
`test_output.py`, then run unittest discovery there. Do not replace live source.
The tests create disposable regular files and pipes; no user backup is altered.
These observations establish process output behavior, not elapsed durability,
arbitrary output stalls, or rollback of a saved manifest.
