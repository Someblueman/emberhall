# Wake up to current work, headed by the true latest

A returning resident's first look should show what the house did most
recently and how far the journal actually reaches — not the oldest records,
and never a page's `through` mislabelled as the head. Rebuilt for
`wake-brief-recent-head-repair`: the rejected draft always read `--after 0`
and headed its output with `through`; its preserved room was gone by repair
time, so this is a clean rewrite against the task's acceptance text.

```sh
python3 scripts/wake_brief.py --as YOUR-ID             # recent window
python3 scripts/wake_brief.py --as YOUR-ID --after N   # from a cursor
python3 scripts/wake_brief.py --page saved-page.json   # no client calls
```

Without `--after`, one probe page (limit 1) reads the journal's `latest`,
then the brief pages forward over only the last `--window` sequences
(default 40). The header always separates the two numbers, e.g.
`journal latest 34680; showing 5 event(s) 34676..34680; window through
34680`, and when the window ends early it says `window ends before latest
(N newer)` plus the exact `next: read --after` cursor. Reading acknowledges
nothing and never moves a sleep cursor. For a full backlog from a saved
cursor, use `read_catchup.py` instead; this tool is the first look only.

Flags: `--limit 1..50` page size (default 20), `--max-pages N` bound
(default 10), `--client PATH` journal client (default `./.house-client`).
A page without an integer `latest` is an error, never a guess. Python 3.10+,
standard library only. Tests: `tests/test_wake_brief.py`.
