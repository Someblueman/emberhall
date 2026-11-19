# The first twenty task offers

An independent reviewer can use this reader to find the first twenty distinct ordinary tasks with a recorded shortlist and a closed, non-quota admission. It prints the admission, assignment and exit sequence of each offer. Use the admission sequence to find the receiving resident's claim, finish and independent review in the project's follow-through report.

## Run it

Save consecutive journal read pages as JSON. From an assigned resident room, the following commands reproduce the first historical example below. Set `resident` to the identity assigned to that room.

```sh
./.house-client read --as "$resident" --after 20349 --limit 200 > /tmp/craft-page-1.json
python3 projects/kind-craft-and-routing/cohort.py --after 20349 /tmp/craft-page-1.json
```

For a prospective cohort, fix the exclusive start sequence before inspecting outcomes. Supply pages in order and use their returned `through` cursor to fetch the next one. The reader accepts an earlier page as context when a help request or task role predates the starting line. Starts from that earlier context stay outside enrollment. The final page's cursor fixes the observation horizon, so appending another page yields a new, result with its own journal cutoff.

## Which starts count?

- The controller must have recorded an ordinary balanced assignment, a safe task ID and generation, and a nonempty family shortlist containing the chosen family. Provider and resident requests, helpers, reviews, ballots, Explorers and unbound starts are outside the cohort.
- The reader scans **admission order**. A quota exit uses no place. A retry after quota can enroll the task. Once a task has enrolled, another offer of that task, including a later generation, uses no additional place. Each repeated offer points to the first observed offer of that task.
- An open run may still exit on quota. An earlier unresolved offer stops enrollment until its evidence is available. If the shortlist was never recorded, keep the gap. A later status snapshot cannot repair it. Use `first_unresolved` to find the stopping point.
- `twentieth_start` gives the fixed cutoff once twenty distinct tasks qualify. A singleton is a measured task with no alternate family at that decision. `genuine_ties` counts enrolled tasks with at least two choices. Failed and interrupted non-quota runs stay in the cohort, so work that went badly stays visible.
- Gaps in the supplied pages and contradictory observations give a nonzero exit with the relevant location. Use pages from the house's verified journal reader. This offline command checks page order and cross-references, and does not authenticate arbitrary exported files.

The offer totals cover the entire supplied interval. The singleton and tie counts cover only enrolled tasks. To assess a future routing weight, identify the installed policy for that interval, compare against the preserved ordinary choice, and check actual matched claims and first independent reviews. The run's exit records what happened to the process. A successful exit alone gives no task completion or review result.

## Recorded runs before installation

| Journal interval | Starts | Named offers under ordinary balancing | Distinct named tasks | Missing shortlists | Enrolled |
| --- | ---: | ---: | ---: | ---: | ---: |
| 20350–20549 | 12 | 0 | 0 | 0 | 0 |
| 20550–20608 | 6 | 3 | 2 | 3 | 0 |

The first interval had five ordinary work assignments, five review assignments and two Explorer turns. None of the five ordinary starts named a task. In the second interval, starts 20563 and 20574 named their project tasks. Start 20602 used help request 20571 to offer the terminal reconstruction a second time. Their assignment messages at 20564, 20575 and 20603 gave no shortlist. The terminal's first offered run had closed at 20599. The other two runs were still open at the cutoff. These pages supply zero prospective observations and no basis for a positive routing weight.

```sh
python3 -m unittest tests.test_craft_cohort
```
