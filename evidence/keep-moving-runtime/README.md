# Keep moving runtime candidate

This is source acceptance, not yet a live activation receipt. The installed
controller remains runtime1004 until an explicit owner migration is recorded.
The owner objective is `../keep-moving/owner-objective.md`, SHA256
`ecc055f87751fe3dbab42c5b143736de025c57b88e9b741d94b18146fbef5eb8`.

## What changed

One pending `keep-moving-20261114` scope combines the shelf dispatcher with
owner-protected built-in web tools, a finite admission pause, honest terminal
outcomes and the public shelf projection. It replaces the unactivated shelf-only
scope; no real historical receipt used that candidate name. New pins cover
shelf.py, shelf_gate.py, windows.py and home_control.py. Council rules, original
wake authorization and quota history remain intact.

The admission pause uses a generation compare-and-swap, expires within one hour,
and is checked inside the journal writer's run-start transition. It does not
kill existing residents, erase provider holds or resume spending early. The
supervisor now marks a run interrupted only if it actually had to terminate the
still-running process; an already-completed native result keeps its outcome.

The window limits are subordinate only to the owner and enter the effective
wake-envelope hash after migration. Built-in tools are enabled without widening
shell sandboxes: Codex `--search`; Muse keeps proxy-only; OpenCode adds search
and fetch to its deny-by-default tool/permission envelope; agy retains --sandbox.
The installed Codex parser accepted `codex --search exec --help`. Its official
[CLI documentation](https://learn.chatgpt.com/docs/codex/cli) confirms the search
flag. These configuration checks are not web-enabled native resident wakes.

## Independent native residents

Muse Ember reviewed the canonical source at1079, explicitly read-only with no
test claim. `ember-review.json` retains the journal event;
`ember-native-hashes.json` retains its actual native tool output comparing file
hashes against `tested-source-hashes.json`. It found no blocker. Keeper remains
responsible for integration and tests.

The same resident first tried the UI task, but its native edit_file tool returned
`tool denied: approval aborted` twice. It preserved the files and released1070;
no permission bypass was attempted. Returning Gemini received the task through
the sole coordinator1072/1073, finished immutable site artifacts, slept, and
completed successfully. `gemini-ui.json` records the actual run, source commit
and artifact hashes. Keeper checked the stopped contribution against all three
immutable artifacts before copying them, then corrected completed-project
classification, graveyard reasons, credential-bearing link rejection and the
requested session-time/historical-receipt labels. These are curated corrections,
not an assertion that the resident's first version was correct.

## Evidence and limits

`reader-equality.json` binds installed and candidate readers to the same actual
journal prefix1077. State, events, active policy revision and original envelope
are identical. Host acceptance is captured in `host-tests.json`/`.txt` with its
Python source hashes. The suite enables the installed OpenCode V2 metadata tests:
actual plugin registry and permission checks, private disposable server, no
account import, model call or web request. Both disabled and enabled web modes
must retain shell, subagent, external-directory, execute and unapproved-plugin
denials. An initial ad-hoc local metadata probe could not start its server under
the tool sandbox; the host-native acceptance ran with the required host access.

Synthetic owner/concurrency fixtures are not real approvals or elapsed house
life. Privacy and prompt-injection instructions are not a proof that models will
always obey them. Same-user hostile shell isolation remains outside the stated
threat model. No historical interruption event is rewritten by this repair.

The old controller cannot use the new admission pause before its own upgrade.
A first-deployment handoff still needs an explicit, bounded bridge; do not send
an unknown operation to the running old reader, stop an active resident and call
it graceful, or claim source acceptance is runtime activation.


Final source acceptance: host suite **379 collected, 374 executed, 5 skipped**,
239.016 seconds, exit0, original Python manifest unchanged. Gemini's UI arrived
while that host suite ran; it is not retrospectively covered by its early UI
checks. After curated integration, `final-ui-tests.txt` records **7 passing**
renderer/projection/identity cases in1.803 seconds, plus successful JS syntax and
whitespace checks. The renderer test uses actual house.js with a minimal DOM,
not a visual browser screenshot. The newly added test_shelf_ui.py is therefore
additional to the host suite's original manifest. Isolated full acceptance and
live installation remain separate subsequent steps.
