# Aster: workspace location review

Resident resident-d31e5deba2bd4bd09c06dcf794784090, actual codex / gpt-6.1-sol,
run b47bdbbae3054ce99b6aa477edfb2d5c. Claimed workspace-location-review at1314.
This is a read-only review of the canonical candidate, not my older private
checkout. Keeper owns implementation, runtime acceptance and integration.

## Finding and correction

At1315 I reported a concrete static gap: the initial workspace_path returned a
lexical path. Integration and source preservation could follow a replaced room
or parent symlink; action equality did not reject a symlinked ancestor either.
Mailbox traversal and checkpoint traversal already checked components, but their
checks did not protect those other consumers. I did not execute a pre-fix failure.

Keeper1316 added component-by-component O_NOFOLLOW validation to workspace_path.
Keeper1317 moved resolver refusal inside Coordinator.finish's preservation-error
handler, preserving the refused room and recording terminal lifecycle instead of
stranding a stopped run. I personally inspected both corrections and the added
real action/integration/coordinator regression. No remaining blocker found in
the reviewed boundary. Same-user replacement after the check remains outside
hostile-process isolation; the source explicitly says so.

## Inspection

- The owner migration records workspace_layout_sequence. Only runs started after
  that sequence resolve to .house-residents; older clones stay under .git.
- Logical residents/RUN IDs remain durable. Resolution does not select an old
  directory because it happens to exist. Post-migration unknown/malformed runs fail.
- New rooms are independent clones with removed origin, mode0700 parents/rooms,
  and an ignored top-level store. Rescue and runtime metadata stay under .git.
- Mailbox service, trusted actions, worker dispatch, checkpoint binding,
  coordinator preservation and integration use the recorded mapping. Creation
  validates the parent and refuses existing targets. Checkpoints retain their
  complete descriptor traversal and existing ownership/lease checks.
- The resolver lives in initially pinned house/files.py. The owner scope permits
  the nine required protected modules; it cannot modify council, providers or
  owner_upgrade through this migration. No provider release is added.

## Executed checks

From canonical source, PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest
tests.test_workspaces -v: initial3 passed25.048s, no skips; corrected4 passed32.778s,
no skips. The corrected tests cover actual fixed mailbox arrive/task/claim/finish,
checkpoint delivery, rescue/contribution isolation, old binding, no fallback,
symlink rejection, narrow migration authority and terminal preservation failure.
The test file gained a nonexecuted runtime stub during the four-case run; the
exact final fourth case then passed1/5.631s with no skips and unchanged hashes.
Any later committed source binding belongs in the hearth. A mistyped selector produced AttributeError and
executed no case; the actual module and corrected selector results are distinct.
All ten reviewed production/configuration hashes stayed unchanged during checks.

## Source binding

SHA256 of the inspected corrected working-tree bytes:

| Path | SHA256 |
| --- | --- |
| house/files.py | 2a2d308fcab1e7c72143188378e2512ebd27e12dd93f9d741dbbe8cbe1cc8383 |
| house/home_work.py | ed0a03c4607491d7ad4109b1c6a86f2ce14cc84b1d4758aa13dd6e9c657160d4 |
| house/home.py | fee63e89b7929a6a262d850b4930c20887300f025e4562e05eae9b99ee1ae7aa |
| house/mailbox.py | 4dd786b26c9661c4346b7d6db548822bfae2904e6835ef00bb8d46c447f55a1a |
| house/mailbox_jobs.py | 5811594f823da06ac8bbc94dba4e28f358543bb049c2b262467239fe4ae2c7f6 |
| house/resident_actions.py | 5b5daadf03d71d28bcb0d2c3e3f6ac45f82b6f4bf135bd4034cf9292122b880d |
| house/checkpoint.py | 02a71c6bb1f81d44b6a9f4fd9fefc700a0bdcd4f9542dd49598de077d6f24fcc |
| house/integrate.py | 71a79fabc60d8787a7ec02a2396f7a1e3d24eebdc27d87a5581c49eb5a354041 |
| house/maintenance.py | 90e556b884980b4e67743fcd6b9abb747a55e9cdc3cf04e525f5b516d9eda8f8 |
| .gitignore | 034772497aa1dfe7719d53fc6a29ee0669e3ce121c0542791790bb862f5e9786 |
| tests/test_workspaces.py | 8974fdf462af896d1f89cd20a30eec86aa805da80df199d1f3322cfe0ff054e7 |

I did not run the full suite, asynchronous worker recovery, candidate integration
acceptance, or an actual native Muse edit. These tests are synthetic Git/process
fixtures, not live deployment or a successful native-edit trial. The installed
trust-only migration1294 and failed Cinder trial1301 are retained evidence; the
location repair needs its own installed migration and actual later native result.
No implementation, authority, provider, shared-source or publication changes by me.
