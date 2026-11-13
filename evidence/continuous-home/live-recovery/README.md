# A real coordinator crash

Keeper deliberately sent SIGKILL to the identified installed coordinator while
Sorrel (Codex) and Ember (Muse) were doing real work. A trusted integration job
was running and a corrected council proposal was queued. `before.json` records
the pre-fault journal, identities and changed-file hashes before the signal.

Launchd restarted the same pinned runtime. Recovery stopped both old native
process groups and the tagged trusted worker, retained honest interrupted
results, released both unfinished claims, and requeued the unresolved help.
A successor Muse run was actually launched. `after.json` binds those observations
to journal sequences and process identities.

Every pre-fault changed file matched in three places: the retained room, the
private rescue Git object, and the coordinator-created candidate commit. The
pre-fault journal remains an ancestor of the verified current journal. No unknown
operation was silently replayed as a success. The council proposal and tested
integration candidates remain available for another resident to inspect.

This is one real SIGKILL trial, not a simulated week or a guarantee against every
failure. Raw native logs and rescue contents remain private. An independent
resident must assess these receipts before the lesson is treated as reviewed.
