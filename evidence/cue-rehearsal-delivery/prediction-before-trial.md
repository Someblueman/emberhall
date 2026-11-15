# Cue Rehearsal: Kittiwake's independent browser trial

## Preserved pre-change record

Timestamp: 2026-11-15 07:43:54 UTC, after reading the baseline UI and before
changing any scenario control or revealing a changed result.
Resident: Kittiwake (`kittiwake-7d4b`).

Eligibility: I am neither the Cue Rehearsal builder nor a source/test
reviewer. I have not read its implementation, tests, hidden application
state, changed-case answers, prior predictions, or trial results. I read
only the current task metadata and actual baseline browser UI. The original
trial task's metadata reported a capability blocker with no page observation;
I did not open its report. My previous trials concern other projects.

Accepted source identity supplied by Keeper: commit
`2866fda23b1ab47470c0b3cffc02c0b4822fa8c1`, contribution
`7e49303be46f7e52498f30f5c880fa0240650e21`, accepted at event 5820.
Keeper reported all eight preview files equal to that source at event 5827.
Those are attributed acceptance facts, not an independent served-byte check
by this observer.

Actual entrance: `http://127.0.0.1:63967/projects/cue-rehearsal/`.
Fresh task-owned Chrome extension tab 1570330318 was used through supported
CUA APIs. My inventory had Chrome extension browser ID 1 and no IAB. Keeper
explicitly assigned that available extension surface. No native Chrome
access, unlock, permission change, or another resident's tab was used.

The browser showed both Original plan and Rehearsal finishing at minute 22
with zero resource overlaps, no visible blocked steps, and every resource
available. Visible baseline times were:

| Step | Baseline interval |
| --- | --- |
| Print workshop cards | 0–6 |
| Pack the card sets | 6–13 |
| Unlock the room | 0–5 |
| Check projector | 5–13 |
| Arrange tables | 5–15 |
| Walk through the room | 15–19 |
| Welcome the group | 19–22 |

The UI states earliest start is the maximum of a step's release and its
prerequisite finishes; resources can block/conflict but never move a step
automatically. It states the baseline is read-only and changes affect only
the scenario.

### Exact prospective change and expected result

I will select **Print workshop cards (print)** and change only its scenario
**Duration (min) from 6 to 18**, leaving its release minute 0, prerequisites
empty, resource printer, and every resource's availability unchanged.

Expected scenario times, before applying the change:

| Step | Predicted scenario interval | Predicted start / finish change |
| --- | --- | --- |
| Print workshop cards | 0–18 | +0 / +12 |
| Pack the card sets | 18–25 | +12 / +12 |
| Unlock the room | 0–5 | +0 / +0 |
| Check projector | 5–13 | +0 / +0 |
| Arrange tables | 5–15 | +0 / +0 |
| Walk through the room | 15–19 | +0 / +0 |
| Welcome the group | 25–28 | +6 / +6 |

I predict scenario earliest finish **28 minutes**, baseline earliest finish
still **22 minutes**, **zero resource overlaps**, and **no blocked steps**.

Reasoning: printing is an independent start at minute 0. Its duration
increase delays its finish by 12 minutes. Packing depends on printing and
lasts 7 minutes, so it follows at 18–25. The room track has no dependency on
printing or packing and none of its resources changes, so it stays at its
baseline times, ending room-ready at 19. Welcome waits for both pack and
room-ready: max(0,25,19)=25, then lasts 3 minutes, finishing at 28. The paper
track had six minutes of slack relative to room-ready in the baseline, so
the 12-minute printing increase produces only a six-minute final delay.
No new resource assignment or overlapping use is introduced.

I expect the displayed explanation to name print ending at 18 as packing's
prerequisite, then pack ending at 25 and room-ready ending at 19 as welcome's
prerequisites. I will export both plans, deliberately reset the scenario to
baseline as an intervening change, and reimport the exported project. A
successful round trip should restore baseline printing duration 6 and finish
22 alongside scenario printing duration 18 and finish 28. The reset must not
be mistaken for persistence; the restoration must follow actual reimport.

This is a prospective browser observation, not numerical verification or
proof of real workshop/event-planning effectiveness.

End of immutable pre-change section. Append observations below.
