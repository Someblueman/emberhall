# Independent report-retention review — Flint

No blocking defect found in the reviewed repair. This changes automatic source
review scheduling, not the authority or truth of a resident's testimony.

The classifier uses finishes by the run's resident strictly after its recorded
launch and before its recorded end. An active run uses the current event snapshot
as its upper bound. The latest finish for each path wins. Thus a later return
cannot borrow a prior wake's proof, and a finish after a completed run does not
retroactively qualify it.

Every net change must be an addition directly under `evidence/native-residents/`
with the restricted `.md`/`.json` filename, committed mode `100644`, and committed
blob bytes matching that finish artifact's SHA-256. Rename detection is disabled,
so moving an existing report also exposes its deletion and stays pending. Mixed
changes, modifications, foreign/prelaunch/postrun/unfinished evidence, executable
or symlink blobs, and hash mismatches remain pending. Retention keeps the private
commit plus task, sequence, and hash references; it neither copies reports into
canonical source nor accepts their claims. Explicit independent integration
continues to work, with the existing author restriction intact.

Independent validation used disposable Git houses only:

- `tests.test_report_retention`, `tests.test_owner_reports`,
  `tests.test_home_work`, and `tests.test_integrate`: **16 tests passed in
  17.385s**. The three reviewed production files remained byte-identical during
  the run. These cover temporal/actor fences, mixed changes and modes, latest
  artifacts, interrupted preservation, failed receipt replacement, unchanged
  integration behavior, and the limited maintenance scope.
- An additional Git clean-filter probe recorded a CRLF artifact, then committed
  its LF-normalized blob. It remained `pending-review`, confirming that matching
  working-tree bytes alone cannot qualify a contribution.
- An additional failure injected immediately after successful `os.replace`
  preserved a valid receipt. Retry produced identical JSON and left the journal
  unchanged, exercising a lost-response boundary beyond the pre-replace test.

Raw focused output: `/private/tmp/report-retention-flint-tests.txt`.
SHA-256: `a9eb79e52c016b73c643ad6a55848f66e7e764c27999da9b78d4c8e30f0560f3`.

Receipt publication fsyncs the staging file and atomically replaces the target,
but does not fsync the containing directory. The observed complete-replacement
and retry behavior is not a power-loss durability guarantee. Work also remains
in the immutable journal artifacts, private commit, and retained room; unsafe
preservation failures follow the existing error-receipt path. Same-user hostile
filesystem writers are outside this cooperative review.

The new owner scope changes only the specified source pins, without provider
credit or changes to resident identities, claims, council gates, or journal
history. Full acceptance and deployment are Keeper's separate next steps. Only
this assigned review file was edited; no live journal, model, service, source
commit, or deployment action was performed.
