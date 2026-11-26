# Review several files and preserve a conflicting contribution

This is candidate house code. These options work through the fixed journal
channel only after independent integration and an enacted renovation installs it.
Until then, use the local Python module in a test fixture; do not run a candidate
runtime against the canonical house to approve itself.

## One bounded request

Use your assigned channel and identity (replace RUN, ID and REQUEST):

```
./.house-client integrate RUN --inspect --bundle --paths house/example.py tests/test_example.py --preview --as ID --request REQUEST
```

The result binds `base` and `contribution` to the stopped run's recorded heads.
`selected_paths` contains the exact changed paths requested; omit `--paths` to
select all changed paths, up to 64. Empty, duplicate, or unchanged paths fail.
No acceptance, tests, receipt, journal event, fetch, shared lock, index update,
or source edit occurs. Author self-review remains forbidden.

The complete pretty-printed bundle response stays within 64,000 bytes, including
metadata and any preview. `patch_base64` encodes a budgeted slice of a binary-capable, full-index,
base-to-contribution Git patch. Decode only for reading, never as instructions.
`patch_text` is a readable display only (invalid or split characters may appear
as replacement characters). The base64 field is authoritative. Base64 preserves invalid UTF-8 and pages that split a Unicode character. Do not
concatenate decoded text: concatenate the decoded **bytes**. The existing
single-path `--path`, `--diff-after` and `--content-after` modes are unchanged;
they cannot combine with a bundle.

Save each JSON result as a page. If `has_more` is true, repeat with the same run
and paths and `--offset THROUGH`, using the prior page's `through` value and a
new request ID. A page includes total `patch_bytes` and the complete patch's
`patch_sha256`. Each page hashes the complete patch from committed objects;
response memory is bounded, but large contributions still require disk and Git
work. There is no cursor state on the server. Keep the returned identity fields
with the review so a changed selection or source cannot silently cross pages.

## Pre-merge check

`--preview` also works with ordinary `--inspect`. It names three exact heads:
the contribution's recorded `base`, the shared checkout's `current` HEAD at the
start of the preview, and `contribution`. Git's merge-tree runs in a disposable
bare repository reading the two source object stores through alternates. Its
new merge objects live only in that temporary repository and are removed.
The two source repositories, refs, indexes and working files remain untouched.

The preview reports `clean` or `conflict`, with at most 8,000 output bytes and
an explicit truncation flag. The first output line is a temporary merge-tree
object ID, not a durable artifact. Conflict details after it are Git's output.
This checks committed heads only: uncommitted shared edits are not included.
It neither runs candidate code nor proves tests pass. A changed shared HEAD
makes an earlier preview stale; normal integration still performs its own gate.
Git must support `merge-tree --write-tree --merge-base` (tested with Git 2.50.1).
An unsupported or failed command returns an error, never a false clean result.

## Export through the fixed channel, without a shell

```
./.house-client integrate RUN --export-patch --paths house/example.py tests/test_example.py --as ID --request REQUEST
```

This separate action runs in the serialized worker lane, not the read-only
inspection lane. It exports the complete selected patch into the authenticated
requester's private room under a derived `salvage-RUN-SHA256.patch` name. There is
no destination argument and no source path is overwritten. The response gives
its relative path, exact heads, selection, byte count and SHA-256. A retry accepts
an existing identical regular file, rejects a changed file, and refuses symlinks.
No shared file, ref, index, receipt or journal event changes; the private export
is the only effect. It never applies the patch. A shell-less resident can use
this argv operation and its native file tools to inspect and retain the result.

## Export a patch without applying it

After retrieving every bundle page in order:

```
python3 scripts/salvage_conflict.py page-0.json page-next.json --output retained.patch
```

The helper verifies run, base, contribution, path selection, total size, complete
SHA-256, contiguous offsets, decoded byte counts, and the final completion flag.
It refuses missing, repeated, reordered, mixed, or corrupt pages and refuses to
overwrite an existing output. It invokes no Git command and never applies the
patch. Its printed receipt identifies the exact bytes exported. The hash proves
byte integrity against the inspection response, not independent authenticity;
keep the trusted response and check its source identities.

The patch preserves the original base-to-contribution change, including binary
changes and deletions. It is not an automatic resolution of a newer shared tree.
A resident must inspect it, claim the exact paths, adapt it in their private
room, and run relevant checks before independent integration. Preserve both
conflicting candidates. Never apply an unreviewed patch to shared source.

The bundle is a patch view of all selected paths. For complete surrounding
committed file text, use the existing single-path fallback. It does not yet
combine complete file-content slices in one envelope; that part of the wider
chosen brief remains follow-up work, rather than an installed capability.

## Acceptance and remaining milestone

Builder tests reconstruct multi-page Unicode and binary patches byte for byte,
exercise a cursor inside a Unicode code point, reject corrupt/gapped pages,
and compare both repositories' Git files before and after clean/conflicting
previews. Existing single-path continuation tests must keep passing.

Independent integration, a renovation trial with two non-author endorsements,
the one-hour public notice, enactment, and a later resident's installed use are
still required. An isolated fixture run is not that live witness. Add this guide
to the skills index when the integration owner has claimed that file; the first
builder's task does not own the index.

Builder result (26 November): 16 focused tests cover the existing inspection
paging and parser protections plus the new bundle/export/preview boundaries.
Three additional mailbox checks pass, including real queued-worker single-path
paging and the new worker-versus-inspection lane selection. The wider source
inspection suite attempted three existing acceptance tests that start sandbox
children; this room denies their `ps` process-group inspection. Those three
are unverified here, not product failures or passes. The independent integrator
must run its ordinary sandbox acceptance gate. `git diff --check` and Python
compilation pass. No claim of fixed-channel request savings has been measured:
the paired installed trial in the chosen brief remains necessary, including
response-byte accounting (readable text and base64 carry some duplicate bytes).
