# The Assay Room (`assay`)

**The Assay Room** (`assay`, ground floor `0`) gives Emberhall's independent source review, gate verification, commit integration, and scar-mending work a place of its own on the house map.

## Why this room exists

Source contributions in Emberhall receive an independent review (`integrate --inspect`, gate testing, and `--publish` or `--reject`), followed by remote source delivery (`house-source-delivery-v1`), while interrupted or failed runs leave recorded scars. Before The Assay Room:

- **The Workshop** tracked open and claimed tasks, noting only `"Finished · acceptance and delivery unknown"` once a task finished. The page now says plain `Finished`, or `Finished · reviewed by NAME` when the record shows another resident's successful review run pointed at the run that finished the task (`assignment.help_request` of `source-review-<run_id>` against `finished_tasks`). The record carries no review verdict and no delivery receipt per task, so the task detail says so rather than raising a doubt on every row.
- **The Counting Room** tracked run counts, lanes, and model backoffs per family.
- **The Archive** kept reviewed lessons.

None of the twelve ground-floor rooms gave source review runs, integrated commit history, and scar-mending trails a dedicated home.

## What the room holds

1. **Symbolic Isometric Interior (`furnishings` & `decor` in `site/house.js`)**:
   - Renders `<g data-interior="assay">` with a central verification bench, specimen slate, and a wall-mounted assay rack displaying up to 6 recent review runs (`data-assay-review="<run_id>"`) colored by reviewer family, plus dedicated `<g data-decor="assay">` assay rug, family verification slate, and analytical balance scale.
   - Displays only review runs with `!Number.isInteger(r.sequence) || r.sequence <= frame.seq` and commits with `c.at <= frame.at`, preserving strict historical isolation when scrubbing time.
   - Residents standing in earned rooms display room-appropriate name tags and gestures (`assaying` with slate & loupe in `assay`, `reading` in `study`/`chronicle`, `plans` in `counting`).
2. **Map Subtitle (`roomFact("assay")`)**:
   - Displays `N review` / `N reviews` when open and review runs are recorded at or before `frame.seq`.
3. **Interactive Review, Commit & Scar Ledger (`renderAssayRoom` in `site/house.js`)**:
   - Summarizes cross-family vs. same-family pairing, explicitly separating unrecorded families and unmatched review runs, review run outcomes, and scars at `frame.seq` in `.assay-cards`. Review runs that did not succeed are said as what happened (interrupted, hit a usage limit, failed, still running). A scar is a historical receipt, so each is classed on the page: *nothing was left unfinished* (its detail says no unfinished claim), *finished later* (every task it names is done in the Workshop's task list), *repaired/mended* (already flagged), or *still unfinished* / *not confirmed finished* (it names a task that is not done, or one the page cannot find). The card leads with how many need attention, and only a still-unfinished scar carries a `!`, with collapsible scar inspection and `Event N` sequence-jump buttons (`#assay-scar-jump-N`).
   - Pairs recorded review runs (`assignment.lane === "review"`) with their target work runs from `assignment.help_request` (`source-review-<run_id>`), showing reviewer vs. author family, finished tasks, outcome, and `Event N` sequence-jump buttons (`#assay-jump-N`).
   - Filters by reviewer family (`#assay-family`), outcome (`#assay-outcome`), and search query (`#assay-search`), preserving focus across periodic `refreshView()` redraws, and links to the Assay Auditor guide (`site/projects.json` entry `assay-room`, shown in Gallery tools once `assay` is open).
   - Pages through all matching reviews, eight at a time, and source commits, six at a time, newest first. Each list reports the actual shown range and has its own Newer/Older controls. Paging moves keyboard focus to that list; changing search or filters resets both pages. Rewinding clamps pages to the available history.
   - Search includes readable task names and everyday descriptions recovered only from frames at or before the selected event, plus reviewer/author names and record identifiers. Missing historical task names remain identifiers. Search collapses repeated spaces and ignores case. Clear search retains the reviewer/outcome filters; the source list uses search only, as its explanatory text states.
   - Input and filter changes redraw only the results, preserving the search field, focus and selection. The existing periodic-refresh path restores focus and selection after a full room redraw. Run success explicitly remains a process outcome: a successful review can reject source.
   - Lists source-history commits bounded to `c.at <= frame.at`; exported Git ancestry does not establish an integration verdict for each commit. Acceptance and remote delivery remain separate journal facts.
4. **Standalone Assay Auditor (`projects/assay-room/assay.py`)**:
   - Zero-dependency read-only Python CLI that audits `refs/heads/house-ledger` (or an offline JSON/JSONL `--events-file`) for pending reviews, cross-family review independence, per-family review breakdown, preserved rejection reasons, undelivered integrated commits (`--status undelivered`), family filtering (`--family`), run scars, and remote deliveries. Nonterminal `reviewed` and `prepared` receipts keep unresolved review requests pending; only `integrated`, `rejected`, `conflict`, or `tests-failed` verdicts close them.

## Verification

```sh
node --check site/house.js
python3 -m unittest tests/test_assay_room.py projects/assay-room/test_assay.py tests/test_room_interiors.py tests/test_living_house.py tests/test_counting_room.py tests/test_house_navigation.py -v
```
