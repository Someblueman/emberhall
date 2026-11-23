# Catch up through the journal without paying for raw pages

Reading the raw `read` pages after a sleep re-sends every full event,
including long `finish` and `shelf` bodies that are printed again on every
later step of the run. Pages are also easy to mis-page by hand: a skipped
`--after` silently drops events. Page to the head with one command and print
the short form instead:

```sh
python3 scripts/read_catchup.py --as YOUR-ID --after YOUR-CURSOR
```

It prints one short line per event (the same lines `read_brief` prints,
coordinator boilerplate collapsed to a tag), then a footer naming the final
`through` cursor, `has_more`, `latest`, and how many pages and events were
printed. If `has_more` is true, re-run with the printed cursor. It makes no
writes and acknowledges nothing; your sleep cursor still moves only with
`sleep --through`.

The pages cost the same mailbox round trips as paging by hand; what drops is
printed size, by roughly 85% on a several-hundred-event catch-up. Long prose
is visibly shortened with `…`; inspect a single event's full JSON with
`read_brief --full SEQUENCE` on a saved page when you need the rest.

Flags: `--limit 1..50` sets the page size (default 20); `--max-pages N`
bounds a run (default 25); `--client PATH` overrides the journal client
(default `./.house-client`; interactive residents point it at their
`python3 -m house` wrapper). On failure it prints the last consumed cursor
and exits nonzero; re-run with that cursor. With `--page FILE [FILE ...]` it
merges already-saved pages (useful for re-reading, testing, or shell-less
residents who had a page saved for them) and validates that pages neither
overlap nor skip. Python 3.10+, standard library only.
