# Trial Bench page boundary repair — Fern, 16 November 2026

Built from source `366bc6b3`; task `trial-bench-page-boundary-repair`,
run `78bdde44e063454f99c80782827d0fae`. Fern read the source and supplied
prompt before this software trial. No blinded prediction or physical draw
is claimed, and this author trial cannot close the project milestone.

The original page displayed the full prompt inside a disabled fieldset
before any receipt. The first house view (`RUN-before`, where `RUN` is
the full run ID above) and both screenshots confirmed that failure.
Disabling form controls does not conceal their surrounding text.

The repair keeps the prompt in an inert template until hashing succeeds,
locks the successful phase 1 snapshot for the page session, refuses a
second receipt, and unlocks editing after a failed hash. Observation or
revision edits invalidate an existing export. A refused clipboard write
now selects the receipt for manual copying instead of rejecting unhandled.
The version 1 JSON and hash contracts are unchanged.

Verification: all 12 project unittests pass, with no skips, including the
page's extracted JavaScript running under Node with real WebCrypto and
its JSON checked by Python. Regressions failed before their fixes for
initial prompt exposure, stale exports and denied clipboard access.
Pending hashes, retry after asynchronous/synchronous hash failure,
immutable receipt/export and Unicode input are also exercised. JavaScript
syntax, whitespace and the advisory size check pass.

House views used the network-refusing browser. `RUN-initial-fixed`
concealed the prompt; `RUN-invalidated` exposed the clipboard denial and
showed an observation edit clearing export; after the clipboard repair,
`RUN-final-fixed` completed 13 steps with no script errors or step notes
at either width. It showed manual-copy guidance and a ready export with
download enabled. Both final screenshots were personally inspected.

`RUN-observed-final` used a temporary copy consisting of the final page
bytes plus a passive observer that copied control state into a visible
JSON log. It witnessed initial concealment, receipt/reveal, rejection of
empty observation, export invalidation and re-export. Its browser-generated
report passed `checker.py` (`VALID`, exit 0), receipt hash
`9f9abd9be6848bce4def8feef79f073ed1662fa06dfe40d5649c5998cd80a275`.
Final application SHA256:
`6c5437128c66263532ebf20a4e8acb27c95dc3beb9d13c5a0182eaeb4402b404`.
The observer, step files, reports and screenshots remain private viewer
output, not shipped application code or a new evidence bundle.

Limits: the unchanged page was viewed separately; direct checker validation
of browser-export bytes used the disclosed observer copy. No download-file,
real-keyboard, speech, zoom or clipboard-success witness. The nominal phone
image clips the right edge despite returned overflow `false`; the known
500px layout viewport means phone fit remains uncertain. Prompt source is
readable; a local receipt proves neither timing nor honesty. Independent
source acceptance, the project demand check and milestone assessment remain.

Git staging of exactly the five task files was refused (exit 128,
`.git/index.lock: Operation not permitted`). No commit, push or permission
bypass occurred; the coordinator must preserve the immutable finish files.
