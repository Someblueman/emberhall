# Night Ferry

A short mystery told through two accounts. Read, compare what each witness
observes, and save your explanation outside the page before submitting it to
reveal the case's answer.

**Start here:** read the [spoiler-free playtest procedure](PLAYTEST.md), then
open the [case player](player/index.html) in a permitted browser. A repository
viewer may show the HTML source instead of running the page; that is not play.

The real case and both accounts are included in this repository. The player's
**fixture** is labelled placeholder text for checking controls, not the mystery.
The procedure explains how to tell which one loaded and how to select the real
case files without reading their contents. [Player loading details](player/README.md)
are also spoiler-free.

Before an initial blind attempt, do not open `case/README.md`,
`case/truth-sheet.json`, `READING-NOTE.md`, or a completed playtest record or
verdict. Those are author, integrator or assessment material and may reveal the
answer. Selecting a JSON file in the player's file picker is different from
opening it to read. Avoid file previews and source inspection during the attempt.
If you already know the solution, disclose that; a later replay cannot be blind.

The player and case files are delivered. Actual browser use and an independent,
unspoiled playtest remain separate acceptance steps. These instructions do not
claim either has succeeded.

The owner explicitly authorizes installed Chrome/Playwright and a local HTTP
server for this project (journal event 2954). Serve the `projects/night-ferry`
directory locally and open `http://127.0.0.1:<port>/player/index.html`; that is
a supported route, not a forbidden workaround. Opening `player/index.html`
directly from `file://` cannot auto-fetch the sibling `case/` JSON, but the
player's **Load case files…** control still imports the three case files
manually, so `file://` remains a supported manual path rather than an automatic
one. If a particular browser tool rejects an action, record its exact reason and
do not circumvent that tool's own policy or change permissions. Follow current
tool permissions and record actual observed acceptance.
