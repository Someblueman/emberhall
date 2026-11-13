# Flint's custodian boundary review

Reviewer: Flint (`breaker-a82d19`). Date: 13 November 2026.
Assigned files: `tests/test_custodian.py` and this report. Keeper owns the server,
launcher, and integration; Flint made no production-code edits. The test task
was claimed before implementation under `custodian-review`.

## Result and reproduction

```
python3 -m unittest tests.test_custodian -v
python3 -m compileall -q tests/test_custodian.py
```

Final independent run: **16 tests passed in 13.441 seconds**. Compilation and the
pragmatic-engineering advisory size check passed. Every test creates a disposable
Git house and invokes the actual isolated entry point in a separate process:
`python -I /absolute/custodian_entry.py --repo ABS --expect-anchor HASH --resident alice`.
No attack targets the live Emberhall journal.

Reviewed file SHA-256 values:

| File | SHA-256 |
| --- | --- |
| `custodian_entry.py` | `66cb28278eb44beecaf5455ec863b34edbc55c298accfd55f90c6bba89af2267` |
| `house/custodian.py` | `54736d8b0d89ef91cac921109644589d10375df5f3606964afd73fbe3246a50c` |
| `tests/test_custodian.py` | `ec0d46c426ce1ab2869a6ee8dd39d095f8cf0cb00aaa10f45b1f2b3186bd5d99` |

## Defects independently witnessed and repaired

1. **The UTF-8 contract initially accepted UTF-16.** A valid request encoded with
   `json.dumps(request).encode('utf-16')` returned exit 0 and `ok:true`; Python's
   byte-oriented JSON parser detected the encoding automatically. This violated
   the documented UTF-8 input contract. Keeper independently reproduced it and
   saved `evidence/custodian/utf16-before.json`, then added strict UTF-8 decoding
   before JSON parsing. The regression rejects both UTF-16 and UTF-32. This was
   an input-contract mismatch, not a demonstrated authority bypass.
2. **A closed response pipe initially exited 120.** Closing the parent's response
   pipe before sending a valid request caused Python shutdown to retry a failed
   stdout flush: `Exception ignored on flushing sys.stdout: BrokenPipeError`.
   The server's first exception handler returned 2, but interpreter shutdown
   changed the final result. Keeper independently reproduced this and preserved
   `evidence/custodian/closed-pipe-before.json`, then redirected that process's
   stdout descriptor to the null device on output failure. The regression now
   observes a clean exit 2. It publishes an append before response loss, retrieves
   the accepted event by stable receipt ID, and retries the identical request:
   the retry is marked replayed and the journal head does not advance.

Flint inspected the final strict-decoding and descriptor-recovery changes. There
are no remaining findings from this bounded review. Output failure still does
not imply rollback; callers must recover the stable receipt.

## Tested boundaries

| Boundary | Actual checks |
| --- | --- |
| Operator binding | Request house and resident must match trusted values; wrong foundation pin, wrong version type/value, and invalid request IDs fail without advancing history. |
| Strict input | Missing/extra envelope fields, duplicate top-level and nested keys, empty/malformed/non-UTF-8 input, multiple documents, NaN, Infinity, overflowing floats, and 2,000 nested arrays produce structured failures. |
| Protocol surface | Found, restore, bundle, enrollment, execution, seed/adopt and extraction operations are unavailable. Extra/missing action fields and nonobject bodies fail. An actor injected into append data or body is rejected; valid events use the operator-bound actor. |
| Concurrent publication | Six real server processes append distinct messages into one valid history. Four concurrent copies of one stable append request create exactly one new event. Reusing that ID with changed content fails. |
| Rule authority | A proposal leaves the sealed house's active rules unchanged. Forged ratification fails; exact ballot bytes retain the house binding. Valid owner signature handling is covered by the separate existing governance suite, not claimed as a new live authority. |
| Input and processing bounds | An 8,000,001-byte request fails. Incomplete stdin kept open by a real parent process reaches its one-second deadline. An append blocked behind a held writer lock also times out without publication. |
| Output failures | A closed response channel exits cleanly and preserves recoverable accepted work. A 200,000-byte artifact receipt sent to an open but undrained pipe reaches its deadline rather than hanging. An exploratory probe observed exit 2 in 1.061 seconds; the regression requires completion within four seconds. |
| Environment | Injected Git directory/worktree/common/object paths, indexed/config-parameter overrides, and trace destinations cannot redirect the trusted repository or write a trace. A malformed HOME Git configuration and fake Git executable in PATH are ignored. Python isolated startup ignores a supplied PYTHONPATH/sitecustomize payload. |
| SSH command rejection | A nonempty `SSH_ORIGINAL_COMMAND` fails. This test supplies the variable to a local subprocess; it does not itself authenticate through SSH. |
| Artifact privacy | A submitted artifact whose name matches a private server file stores only explicitly supplied bytes. It never reads or changes that local file. Read pages omit artifact contents; receipt lookup returns accepted immutable bytes. |
| Read/error boundaries | Null cursor, bounded pages, continuation, invalid numeric cursor/limit values, and unknown receipts behave as specified. |

## What the tests do not establish

These tests run under the same local OS user and exercise the trusted program's
protocol, validation, process handling, and environment cleanup. They do **not**
establish resident filesystem isolation, a deployed protected service account,
credential provisioning/revocation policy, live authority migration, or multi-day
operation. Same-user shell access can still alter this checkout or its journal
outside the protocol. Operator-supplied interpreter, launcher, package, startup
environment, Git configuration in the protected repository, and installed host
must actually be outside resident control for the proposed boundary to hold.
Environment cleanup inside Python cannot undo native-loader code already executed
before startup.

The tests exercise real local subprocesses, not a network SSH server. Any actual
loopback SSH trial belongs to Keeper's separate evidence and must not be inferred
from this suite. Even a passing same-user loopback trial would not prove filesystem
isolation on the intended owner-controlled deployment. The deployment recipe in
`docs/CUSTODIAN_DEPLOYMENT.md` requires separate operator decisions and installed-
host access checks. Live Emberhall remains local and sealed; this review enrolls
no owner key, ratifies no proposal, and changes no host account or SSH service.

The suite covers request-size enforcement and blocked-output deadlines. It does
not stress arbitrary total history size, sustained authenticated connection load,
all 16 MB response-limit cases, memory exhaustion, power loss, or transport tail
latency. Those claims need their own bounded evidence.

Flint has not committed or pushed this contribution; Keeper reviews and integrates
it under the user's current source-publication authorization.
