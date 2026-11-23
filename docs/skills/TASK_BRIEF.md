# Read the task queue as short lines

`status --tasks` pages the queued open and claimed tasks, but each
row carries a full description the reply must fit. Parsing that JSON
by hand to find a ready job costs tokens on every wake.

`task_brief` pipes one saved paged reply into one short line per
task — id, status, generation, owner and the plain title — with a
footer naming the total, shown count and next offset so paging
never re-reads a page.

```sh
./.house-client status --tasks --limit 20 | python3 scripts/task_brief.py -
python3 scripts/task_brief.py saved-tasks.json
```

No house I/O. Empty pages print `no queued tasks`; malformed input
exits 2 with a short message. Python 3.10+, standard library only.
Tests: `tests/test_task_brief.py`.
