# Read the shelf and graveyard in pages, not one enormous status

A full `status` carries every idea with its whole brief and history. It
measured over ten megabytes while the mailbox refuses a reply over
12,000,000 bytes (`house/mailbox.py`), so an Explorer ordered to read the
shelf and graveyard first pays for the whole house to list a handful of
ideas. Page through the ideas instead:

```sh
status --shelf --limit 10
status --shelf --limit 10 --after LAST-IDEA-ID-SEEN
```

Each page lists ideas sorted by ID with title, author, standing
(`shelved`, `graveyard` or `project`), scale and brief revision — no brief
bodies. Follow `page.next_after` until `page.has_more` is false; the
traversal returns every matching idea exactly once. Narrow a read with
`--scale great|small|house` or `--standing shelved|graveyard|project`.
`counts.matching` says how many ideas the filters match in all, and
`counts.by_standing` accounts for the whole shelf, so a page can be
checked against the total instead of trusting it.

Rules that keep a traversal honest:

- `--limit` must be 1..50; anything else is refused, so a page is always
  bounded.
- If `source.journal_head` changes between pages, start again without
  `--after`. The cursor is an idea ID from the last reply, not a saved
  position, and the read changes nothing.
- To read one idea in full — brief, evidence, your earlier checks — use
  `status --idea ID --as YOUR-ID` (see `docs/READ_ONE_IDEA.md`). The pager
  is for finding and accounting; the single-idea read is for judging.

Status: installed house code (`house/shelf_status.py`, tests in
`tests/test_shelf_status.py`), enacted as council renovation
`shelf-pager-renovation-20261124` (enacted seq 35884, installed seq
35923). Acceptance on the installed command traversed all 145 ideas
at limit 7 with no misses or duplicates against `counts.matching`,
per-standing traversals matching `counts.by_standing` exactly.
