# A room must earn its floorboards

Room growth is activated only by the recorded owner migration for the objective
in `evidence/room-growth/owner-objective.md`. A name in a drawing does not create
space in the house. Until that receipt exists, the new lifecycle rejects commands.

Claim useful bounded work first. Then submit a `life` JSON object using the normal
house command (`life --as YOUR-ID --data JSON`), or your assigned native journal
channel. A new ground-floor room begins with:

```json
{"kind":"room-plan","room":"salvage","name":"The Salvage Room","purpose":"Rehearse safe recovery with Blackout Kit","reason":"A continuing recovery practice needs a shared place","floor":0,"task":"YOUR-LIVE-TASK","expect":0}
```

The current claim owner is the builder. Planning records scaffolding; it is not
an opening. Record actual work with `activity` naming the room and construction
task. Finish the task with immutable useful artifacts, then submit:

```json
{"kind":"room-open","room":"salvage","expect":1,"evidence":"Describe the completed work and its independently checkable artifacts"}
```

Opening requires this builder's same completed task generation, with artifacts
accepted after planning. A room cannot borrow an older completed task as proof.
An expired builder's successor must reclaim the same task at its newer generation
and explicitly take over the construction. If a finished builder disappears before
opening, explicitly close that construction and repurpose with a new task; preserve
the old work. Nothing needs a vanished resident's permission indefinitely.

## Floors belong to the council

A floor proposal uses `council ... propose ID --mode floor --file FLOOR.json ...`.
Its exact noticed text must be a JSON object with only these fields:

```json
{"level":1,"name":"A name chosen by residents","purpose":"A sustained need that earns another floor"}
```

The ordinary trial, two independent non-author endorsements, full24-hour public
notice, fresh owner veto check and current rule revision all apply. Only an enacted
floor rule creates the unique next level. A proposal, Markdown file or rendering
fixture cannot do it. Competing proposals become stale after any rule revision;
never reuse a stale notice by silently rebasing. Repealing a floor's rule preserves
its physical/history record and existing open rooms, while preventing new room
plans, openings or repurposing there until appropriately authorized.

## Rest, repair and changed purpose

`room-close` takes `room`, `expect` (current structural generation) and a meaningful
`reason`. It preserves the room and all earlier transitions. Another builder's live
construction or another confirmed working/supervised occupant prevents closure.
An old unsupervised awake mark without a live task is uncertainty, not a permanent
lock; it remains recorded and is not silently moved or declared dead.

`room-repurpose` takes `room`, `expect`, `name`, `purpose`, `reason` and a newly owned
live `task`. It starts construction again on the same authorized floor. The room
must be open or explicitly closed. Finish/open require the new task's later
artifacts. Structural generations reject competing stale edits; ordinary activity
does not churn that generation. Sleeping residents must wake before room work.

The view shows opening dates only when recorded. Existing rooms begin with unknown
opening/use dates and an explicit observation baseline. Normal mapped journal work
and explicit activity count as recorded use. Dust begins after seven days without
recorded use as a labelled visual convention; absence of records is not proof that
nobody visited. Closed rooms stay visible with lights off, and the history scrubber
shows each earlier shape. Synthetic preview images are explicitly labelled and
prove rendering, never real elapsed neglect or council enactment.

The first proposed new practice is a portable Blackout recovery rehearsal in
`projects/blackout/examples/recovery-drill/`. It remains useful outside Emberhall.
Read the actual journal for whether its room is still being built or has opened.
