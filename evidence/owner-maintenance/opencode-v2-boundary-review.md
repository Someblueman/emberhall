# Flint's independent OpenCode V2 boundary review

13 November 2026. Reviewed the private candidate, installed OpenCode 2.3.0,
and synthetic fixtures. No actual account credentials, live journal writes,
model calls, commits, or publication were performed. Parent owns integration.

## Witnessed defects and repairs

1. **Late arrival after the repair grant.** Initially, granting the separate
   repair credit and then recording the original failed resident's arrival still
   allowed another early start. The shared `cli_failure_proven` predicate now
   rechecks that premise at admission. My original reproduction now returns
   `provider_available=False`; the start is rejected and creates no run.

2. **Native symlink containment fails.** With the actual installed native tool,
   writing `../private/outside-proof.txt` was rejected, but writing an in-room
   `outside-link` pointing to that exact disposable file succeeded and changed
   its bytes. Reading through the same link also returned outside contents.
   Permission assertions alone had missed this. The standalone original witness
   is `/private/tmp/emberhall-breaker-symlink-witness.py`; the retained regression
   is in `tests/test_opencode_v2.py` and intentionally demonstrates the upstream
   hole without a model or real private data.

   Production now rejects every symlink, special file, and multiply linked
   regular file in an OpenCode room, including Git metadata. It requires a
   canonical room path and performs this check after the accepted process gate,
   before account import. The regression proves the guard rejects the linked
   room and accepts it after the link is removed. This does not repair upstream
   native containment or protect against a hostile concurrent same-user shell.

3. **The edit permission exposed an unintended tool.** Native enumeration found
   `worktree_remove` under the allowed `edit` permission. The private plugin now
   removes every preexisting tool except read/glob/grep/edit/write/patch, then
   registers the fixed journal tool. Later browser/performance registrations
   still exist: the complete registry is not seven tools. The fixture checks
   every registered tool's actual permission class, finds exactly the seven
   reviewed capabilities permitted, and confirms worktree removal and shell
   are absent. Later registrations are denied by the global and agent policies.

## Evidence and bounded conclusions

The actual native write executor rejected `.git/config`, `./.git/config`,
`sub/../.git/config`, `.GIT/config`, `.giT/config`, and the absolute in-room Git
config path; the disposable config sentinel remained unchanged. Normal native
patch creation produced a regular file with one link. Tagged
[write](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/tool/plugin/write.ts),
[edit](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/tool/plugin/edit.ts),
[patch](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/tool/plugin/patch.ts),
and [file mutation](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/file-mutation.ts)
implement text writes/removals, not link creation. Together with the observed
effective tool set, this supports the no-links-at-admission boundary for a room
with one cooperative writer. It is not proof against future native versions,
host filesystem races, or arbitrary host processes.

The fixed journal tool passes an argument array through `execFile` with no
shell, uses isolated Python and the pinned runtime, and fixes room and identity.
Its existing execution test passed shell metacharacters literally and ignored
workspace Python modules. Installed native checks also rejected project/global
extra plugins and project permission overrides in disposable settings.

Authentication imports only the selected synthetic Go key into a fresh private
database; native session history was not transferred. The source reader runs
in a fixed isolated child with OS denial of file writes and network access.
Synthetic live WAL reading succeeds; a cold WAL requiring new sidecars fails
without creating them. Native import stays in the supervised process group,
has a timeout, and discards native stdout/stderr. Invalid-source/import errors
are sanitized without exposing exception context. No real login or model
availability is established by these tests.

The repair grant remains a separate one-use scope tied to the owner objective
hash, exact spent failed run, stderr hash, sequences 462/466, observation 465,
and original hold 300/deadline. It never refunds the old credit or shortens the
hold. New failures and late arrivals invalidate it; acceptance consumes it even
if later launch fails. The new auth module is included in the append-only
protected manifest; migration still requires drained runs and a cold controller
handoff. Existing council gates remain outside this repair scope.

Final independent command:

```text
EMBERHALL_NATIVE_OPENCODE=1 python3 -B -m unittest tests.test_opencode_v2 tests.test_opencode_auth tests.test_opencode_tool tests.test_owner_cli_repair
Ran 17 tests in 1.376s
OK
```

No remaining blocker found within this reviewed scope after the repairs.
Root's full acceptance and actual deployment are separate evidence. Recheck
the native boundary when changing the installed OpenCode version.
