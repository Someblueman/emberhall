# Night Ferry: spoiler-free blind playtest

Use only this procedure and the [player](player/index.html) before preserving
your initial explanation. [Loading details](player/README.md) describe the
existing controls without giving away the case.

## Before starting

You must be a non-author of the case bible and both accounts, and must not
already know the solution. Record that eligibility and anything you previously
read. Do not open `case/README.md`, `case/truth-sheet.json`, `READING-NOTE.md`,
or any completed playtest record or verdict before your initial attempt. Do not
inspect player data or source to find the answer. If a prior reading exposed
it, disclose the exposure and leave the blind attempt to someone unspoiled.
Previously spoiled residents remain ineligible even with these new instructions.

Record your start time and the source revision, if available. Keep notes outside
the page: reloading or switching cases clears its route and explanation. Use
the record path assigned to your playtest; preserve existing work there.

## Open the real case

Open [player/index.html](player/index.html) through an already permitted browser
path. On an existing permitted HTTP(S) deployment, the player tries to load the
real case from its sibling case directory. Opening from `file://` instead uses
the bundled fixture because sibling JSON fetching is blocked by browsers.

For manual loading, choose **Load case files…** and select these three files
together from `case/`, without opening or previewing their contents:

- `truth-sheet.json`
- `landing-clerk.json`
- `engine-room.json`

The player reads them as data and keeps the answer hidden until submission.
Check its source note and case display before beginning. A **fixture** badge,
placeholder text, or `?fixture=1` means you are checking controls, not playing
the real mystery. If loading fails, record the visible failure; do not count a
fixture run as real-case play.

Prefer an already permitted HTTP(S) path. The owner explicitly authorizes
installed Chrome/Playwright and a local HTTP server for this project (journal
event 2954). Serve the `projects/night-ferry` directory locally and open
`http://127.0.0.1:<port>/player/index.html`; that is a supported automatic-load
route, not a forbidden workaround. Opening the player directly from `file://`
cannot auto-fetch the sibling `case/` JSON, but the **Load case files…** control
still imports the three case files manually, so `file://` remains a supported
manual path rather than an automatic one. If a specific browser tool still
denies the action, record its exact reason and stop; do not circumvent that
tool's own policy, change permissions, or substitute a source reading for
observed play. These instructions grant no access beyond existing tools.

## Read and preserve your initial explanation

1. Choose an account, then read the other. Record which you opened first and
   any later switches. Mark the statements you rely on and use the comparison
   notebook to check your reading against both accounts.
2. Answer the question displayed above **Final explanation** in your own words.
   Explain which observations support it and whether another explanation still
   fits. Record uncertainty rather than guessing what the author intended.
3. **Before pressing Submit explanation**, save a separate initial record with
   your route so far, cited statements, reasoning, exact final explanation,
   and time. Copy the visible route and your draft into that record. Preserve
   this section unchanged after learning the answer.
4. Submit that same explanation. Submission immediately reveals the answer.
   The player's download, copy and text-record controls appear only afterwards;
   they cannot replace the separate record saved before reveal.

## Assess after the reveal

Keep the original explanation intact. Append a separate assessment comparing
it with the revealed answer: was the deduction supported by both accounts,
ambiguous, stated outright, or unreachable? Name any confusing wording,
missing evidence or control problem, and the concrete change it needs.
Use the player's self-assessment and **Download playtest record**, **Show text
record**, or **Copy record** to retain the page's record where available.
Disclose unavailable export controls instead of claiming a successful export.

Record end time, interruptions and actual elapsed time. Distinguish observed
browser behavior from your assessment of the story. Keep solution-bearing
details in the assigned playtest record for the integrator, outside the blind
player entrance and shared spoiler-free handoff. An integrator checks the
preserved initial explanation against the author material; reading these
instructions or exporting a record alone does not complete the milestone.
