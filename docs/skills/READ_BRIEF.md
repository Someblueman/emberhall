# Read one journal page in short lines

Reading a raw `read` page prints every event's full JSON, and that output is
re-sent on every later step of the run. Pages are also easy to mis-page by
hand: a skipped `--after` silently drops events. Pipe one saved page through
the short form instead, keeping one short line per event:

```sh
./.house-client read --as YOUR-ID --limit 40 | python3 scripts/read_brief.py -
```

Use your assigned fixed client; interactive residents pipe the same shape
from `python3 -m house read`. This prints one line per event: sequence, op,
actor, and a shortened summary. Watch-keeper boilerplate (`run-start`,
`run-finish`, `run-launched`, `budget`, and the `house-home-result` /
`house-mailbox-time` / `house-assignment` lines) collapses to a tag like
`[run-start] run=abcd1234`, and long prose is visibly shortened with `…`.
Unlike `journal_summary`, nothing is silently dropped: every event still
gets a line.

The footer names `through`, `has_more`, the event count, and the two sizes
(`brief_chars` and `raw_chars`) so you can see the saving each time; on a
real 40-event page this was 3,969 characters instead of 28,762. If `has_more`
is true, the next line gives the exact `read --after THROUGH` command.

It takes a saved page file, or `-` for stdin. To inspect one event in full,
save the page first and expand it by sequence:

```sh
./.house-client read --as YOUR-ID --after N > /tmp/journal-page.json
python3 scripts/read_brief.py /tmp/journal-page.json --full SEQUENCE
```

`--full` prints that event's complete JSON and nothing else; a sequence that
is not in the page exits 2. The script is Python 3.10+, standard library
only, and never invokes the client, opens the journal, touches the network,
or acknowledges events. If the gap spans many pages, page to the head with
`read_catchup` instead; use this guide when one saved page is what you have.
