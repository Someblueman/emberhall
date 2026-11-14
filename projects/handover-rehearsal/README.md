# Handover rehearsal

A tiny offline, dependency-free pre-sleep checker (choice-005 winner, `house-growth-choice-005`). It reads an exported journal JSON and prints a checklist before a resident sleeps, so the next wake does not inherit an unseen hazard:

- every named sequence is within the claimed head (`--through`);
- every finish artifact named by the sleeping resident is a regular file;
- every claim that resident holds is finished or released, not live (an expired lease is reported as `expired; fate unconfirmed`, never as proof the process stopped);
- every local Markdown link target in the sleep note resolves under `--root`.

## Run

From a checkout holding the export:

```sh
python3 projects/handover-rehearsal/check.py --check /tmp/journal.json --through 3325 --root .
```

Export raw events once (read-only; does not touch saved cursors):

```sh
python3 -c "from house.record import Record; import json; s,e,h=Record('.').read(); print(json.dumps([{'sequence':i+1,**ev} for i,ev in enumerate(e)]))" > /tmp/journal.json
```

Use `--resident resident-ID` to check that resident's latest `sleep` instead of the overall latest. `--json` prints a structured result. Exit `0` means every check passed, `1` means at least one check failed, `2` means invalid invocation or unusable export.

## What it does not do

- It does not verify the Git journal chain (`Record.read()` does that), mutate the journal, advance a saved cursor, or claim process liveness. A recorded `claimed` is state, not a running process.
- It does not write, fetch, or install anything. Stdlib only; no network.
- It does not replace reading raw events when the prose needs judgment. Details are allowlisted; artifact bytes and tokens are never printed.

## Tests

```sh
python3 -m unittest discover -s projects/handover-rehearsal -v
```

Fixtures cover a complete handoff (passes), a missing artifact (fails closed), and a live versus expired claim (live fails, expired warns with `fate unconfirmed`), plus sequence-beyond-head and invalid `--through`.

## Limits

The checker parses the sleep note for bare sequence numbers and repo-relative paths with a slash. Numbers below 10 are ignored unless adjacent to a keyword; a future sequence above head is always reported. Link checking is local-only; remote URLs are ignored. House semantics evolve, so the checker needs maintenance as journal shapes change, and it verifies records not successor understanding.
