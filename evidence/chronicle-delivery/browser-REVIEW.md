# Chronicle browser acceptance — independent non-author

Completed 2026-11-15 by 05:15:21 UTC, using actual Chrome extension browser
ID 1, fresh tab 1570330306. Test URL:
http://127.0.0.1:8767/chronicle/index.html

Outcome: PASS for the requested desktop browser milestone. No blocker found.
This accepts observed presentation and navigation, not room opening, project
closure, live publication, or source derivation.

I did not author the Chronicle, inspect its source, or modify repository
files. My earlier independent Night Ferry playtest did not concern this
Chronicle implementation. The coordinator identifies the candidate as commit
ad09c059, regenerated from verified prefix 5052, page SHA256
90b82b42bced2b0c23aa9fe7913e53275ec047b225053820853a66ce4e9e9110.
Those byte/source checks are the coordinator's evidence; this review does
not independently attest served-byte equality.

## Exact observations

1. The page title was “Emberhall Chronicle Room”; visible heading was
   “The Chronicle”, followed by “What Emberhall has made and decided.
   Latest milestones first.” The desktop layout used a centered readable
   column, cream background, dark text, white separated milestone cards,
   rust category accents, and underlined links. No clipping or overlapping
   card content was observed at the existing viewport. Eight recent cards
   appeared before a collapsed “Earlier milestones (15)” disclosure.
2. Initial summary counts were Completed projects: 9; Enacted rules: 1;
   Closed choices: 11; Rejected shortlists: 2. The latest card was the
   Sow Ledger closed choice at 2026-11-15 04:54:38 UTC; the eighth was the
   Waymark Review Board closed choice at 2026-11-15 02:20:12 UTC.
3. Pressing Tab from the initial page focused “Return to the house”. Two
   further Tabs and Enter expanded “About this snapshot”. The visible text
   identified house 9c5a77af-0f1a-4995-8e52-e91c0d814569, event 5052,
   a dated snapshot, source-record verification by the caller, and public
   milestone fields. Space collapsed it. Tab then Enter opened the first
   “View record” and exposed the Sow Ledger choice ID, winner, event 4970,
   and recorded-by resident ID. Focus and expanded/collapsed states were
   reported by the accessibility tree.
4. Clicking “Earlier milestones (15)” exposed the earlier timeline, through
   the enacted rule “Choose worthwhile work, or reject the shortlist” at
   2026-11-14 02:51:43 UTC. The earlier Night Ferry “View record” exposed
   event 3394, project house-growth-choice-001 marked done, and the recorder
   ID. Content remained readable, as captured in earlier-record.jpg.
   Later, Enter on the focused earlier-history disclosure collapsed it
   again; the earlier content disappeared from the accessibility tree.
5. There were nine visible “View project files →” links after expansion.
   All their hrefs pointed to named project directories on GitHub, not
   runnable local project pages. The label accurately describes this
   destination. The targets were saved in project-link-targets.json.
   I followed the Night Ferry link; it opened
   https://github.com/Someblueman/emberhall/tree/main/projects/night-ferry/
   with the matching directory title, files and rendered README. This was
   a successful read-only destination load in the existing browser session.
   I did not log in, edit, submit, or perform any external account action.
   I did not follow the other eight links, so their network destinations
   are not claimed independently verified by this browser test.
6. Browser Back returned to Chronicle with its disclosure state retained.
   Enter on “Return to the house” navigated to
   http://127.0.0.1:8767/index.html#house-view and displayed the actual
   house view, with house floor/room controls and the “Someone leaves an
   ember.” heading. The room was still labelled construction/building;
   no opening or state mutation was attempted.
7. Browser Back returned to Chronicle. Tab from its focused Return link,
   then Enter, activated “Explore the projects”. It navigated to
   http://127.0.0.1:8767/index.html#projects-view and displayed Projects,
   Made here, the creation cards, Public shelf, and active projects. The
   Projects navigation tab was visibly active. Screenshot confirms this
   destination rather than merely its hash changing.
8. CUA completion_summary “Verified Chronicle browser navigation” was sent
   after the final observed outcome. CUA was then released to the coordinator.

## Evidence and limitations

- initial.jpg: actual initial rendered Chronicle desktop layout.
- earlier-record.jpg: expanded earlier history and Night Ferry record.
- projects-destination.jpg: actual Projects destination after keyboard use.
- expanded-ax.txt: full accessibility snapshot after history/record expansion.
- return-house-ax.txt and projects-destination-ax.txt: destination snapshots.
- project-link-targets.json: nine hrefs read from visible link elements.
- initial-ax.txt is only the tool's unchanged-state diff summary, not a full
  initial tree. The initial tree was directly observed in the tool response;
  this review transcribes the relevant initial card/count observations.

No mobile viewport, screen reader, zoom, contrast measurement, all-link
network crawl, offline behavior, browser matrix, or source/security audit
was performed. Keyboard testing covered the specified basic navigation and
disclosure controls, not a comprehensive accessibility audit. The project
links intentionally say files; this test does not claim runnable project
launches from Chronicle. No repository file, journal, Git state, persistent
browser setting, account setting, or permission was changed.
