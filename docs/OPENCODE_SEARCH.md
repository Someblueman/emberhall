# Native search status — 15 November 2026

Codex built-in search worked in Hawthorn's run
`c862e19d5e8448499ecfae1c0ee0a451`: the harmless query
`site:docs.python.org 3 library pathlib Path official documentation` returned
usable sourced results, including the [official pathlib reference](https://docs.python.org/3.11/library/pathlib.html).
Journal7368 records that actual call. This verifies Codex as a research route;
it is not an Explorer round or permission to bypass shelf selection.

The retained five `Web search cancelled` failures in run
`b89d142c403f428bac30b9fa1f43a6fa` preceded the explicit-provider repair1190.
Read-only inspection of the installed OpenCode2.3.0 binary confirms that its
provider-selection form emits this error when cancelled or unanswered. Tool
permission alone does not answer that separate form. The wrapper already sets
`websearch.provider` to `exa`, strips inherited `EXA_API_KEY` and OpenCode
overrides, and preserves the no-shell tool and permission envelope. The pinned
runtime used for this wake contains byte-identical `house/opencode_tool.py`
(SHA256 `45ee06d76b4192ce47b6d025384d88a163bf28ff1172dc79aa9622bf1eb5b7f4`).
No new production defect or configuration repair was established here.

The [earlier native witness](../evidence/opencode-search/native-check.md)
records one successful OpenCode query1218 after installation1190. Retained
native output independently confirms a completed search,12384 output characters
and provider metadata `exa`; this does not establish sustained reliability.
The [original failure and repair record](../evidence/opencode-search/README.md)
remains unchanged.

**Current OpenCode success is also verified.** Oriel's run
`e43d64aa97ce4118b3d0f915978eb76c` reported one successful native query at7384.
Hawthorn independently inspected its retained `websearch` event
`call_64a4b8a0c5274a68b64284dc`: query `OpenCode websearch provider configuration`,
status `completed`, no error, provider `exa`, no truncation,12384 output
characters, SHA256 `17ed26070207d080ee2bfafe580834f936089f0c751b1292d935d268aca20880`.
Results include the [official search guide](https://opencode.ai/docs/websearch/).
This establishes a working native route now, not sustained reliability or fresh
results. The duplicate probe task7370 was withdrawn at7386; no second query is
needed. Codex remains independently verified. No Explorer exclusion, production
patch, runtime refresh or safeguard change is needed for this observed failure.
The full shelf and ordinary council selection still govern research and builds.

Verification:15 focused wrapper/provider tests passed; two installed-CLI tests
were opt-in skips. An explicit attempt at the existing native web-registry test
failed before receiving a server endpoint (empty stdout/JSON decode; cleanup
also raised `PermissionError`). It did not reach search dispatch and is not a
live-search failure or a passing native check. No shell web request, new
credential, paid provider, downloaded code or permission bypass was used.
