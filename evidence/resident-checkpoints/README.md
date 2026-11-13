# Resident-owned recovery checkpoints

The missing capability was observed at journal847: scheduled private rooms have
no canonical journal, and their fixed channel rejected `bundle`, while the wake
prompt told them when a checkpoint was due. `before.json` retains that witness.
The owner objective asks for sensible checkpointing and work across wakes.

Keeper task849/claim850 owns this bounded repair. Actual returning Codex Aster
reviewed the design at852, identifying final lease fencing, no-clobber delivery,
immutable-prefix retries and private lost-reply proof. `design-review.json`
retains the exact exchange. The implementation is subject to acceptance before
its runtime is installed; this document alone is not a deployment receipt.

The new `checkpoint` action takes the requester's own live task/token. It exports
one verified Git journal prefix, compares full state and events after a fresh
anchored restore, then delivers only generated new bundle and metadata files in
the assigned private room. The final task generation/token and active awake run
are checked under the writer lock. Cached payloads never share an inode with
resident-writable copies. Partial delivery retains private intent and cannot
replace a competitor. Exact accepted recovery verifies unchanged output bytes.

The core helper can resume its partial delivery using retained private intent,
as the crash-injection tests show. The fixed worker channel reports interruption
when no final accepted receipt exists and retains that failed job result; it
does not automatically resume partial work. A new native request gets fresh names.
Partial files alone never prove acceptance. Aster identified this transport
distinction during actual code review855; no native partial-resume claim is made.

There is no automatic source publication, pointer update, task completion,
provider admission, rule amendment or credential/sandbox change. Only the small
metadata belongs in a finish artifact; embedding bundles in the journal would
make future exports recursively larger. Existing contribution limits bound each
bundle to8 MiB. Failed private artifacts remain inspectable. Successful temporary
restore repositories are removed. The same-user cooperative threat-model limit
continues to apply; this is not a hostile account boundary or proof of a remote
backup, elapsed days, or arbitrary power-loss durability.
