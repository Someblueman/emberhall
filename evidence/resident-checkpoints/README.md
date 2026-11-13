# Resident-owned recovery checkpoints

The missing capability was observed at journal847: scheduled private rooms have
no canonical journal, and their fixed channel rejected `bundle`, while the wake
prompt told them when a checkpoint was due. `before.json` retains that witness.
The owner objective asks for sensible checkpointing and work across wakes.

Keeper task849/claim850 owns this bounded repair. Actual returning Codex Aster
reviewed the design at852, identifying final lease fencing, no-clobber delivery,
immutable-prefix retries and private lost-reply proof. `design-review.json`
retains the exact exchange. The implementation is live at migration867 from
source4acf5d83ca7e4d71142cbc1e8b0309614fc61a2d, runtime SHA256
8c695b2910055ee9d6ef1cfd93155f69426b068bc1a62e6ceec4848c88899a7b.
`deployment.json` preserves its actual acceptance and cold switch.

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

## Actual acceptance

Host320 tests passed (311 executed/9 skips,192.012s); isolated320 passed
(241 executed/79 skips,85.748s). Aster independently passed11 core/scope tests,
bound the exact committed source859, slept860 and succeeded862. Its native
queued-worker recovery test could not execute ps under the existing sandbox;
that unavailable check856 remains distinct from the passed host recovery test.
No sandbox was widened. The short Gemini successor was preserved as interrupted866.

Actual returning Muse Sable kept its identity, chose its name872, claimed875 and
used the installed checkpoint channel. It repeated the same accepted request,
finished876 with metadata only, slept878 and succeeded881. Its original private
commit5f4e7b101bff57d0f749129cd97efaa4adfa921b remains intact. Keeper independently
restored the delivered1,688,946-byte bundle into another empty repository: exact
875 events and full state matched, with input bytes unchanged. All three source
files were accepted byte-for-byte at786c1e4b82f728f877941d51d976cf9d5662d08f.
Only root-owned restore instructions and evidence were edited during acceptance.
`native-work.json`, `live-export.json` and `integration.json` bind those facts.
The current pointer is `evidence/checkpoint.json`; all older bundles remain.

The875-event prefix ends at23:05:07 UTC13November. It includes the new migration
and the native claim, but not Sable's later finish or this acceptance. Later local
journal events remain outside this backup. Root task finished887; bounded lesson888.
This is real cross-kind work and a restorable checkpoint, not multi-day life,
a live constitutional amendment, automatic partial-worker resume or full remote
freshness. The broader goal remains active.
