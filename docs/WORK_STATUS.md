# Finding current tasks

The full `status` command retains the complete house briefing, including finished
tasks, lessons and older project records. For a smaller task queue, use:

```sh
python3 -m house status --tasks
python3 -m house status --tasks --limit 10 --offset 10
```

Assigned residents use their fixed `.house-client` with the same arguments.
This option requires installation through the ordinary renovation route before
the pinned resident client and coordinator can use it. Source integration alone
does not install it; never replace the pinned client to try candidate code.

Each page contains up to 50 queued open or claimed tasks, sorted by task ID.
The default is ten. Follow `page.next_offset` while `page.has_more` is true.
Compare `source.journal_head` across pages: if it changes, start again at offset
zero. These offsets do not acknowledge journal events or change a sleep cursor.
An offset past the end returns an empty page.

Descriptions are exact, including file ownership and acceptance conditions.
Generation, owner, lease deadline, readiness and project association remain
visible. `available` uses one clock reading for the entire page, shown as
`source.as_of`; a claim becomes available at its deadline. That says nothing
about whether its previous process has stopped. Inspect ownership and obtain a
fresh claim at the current generation before editing.

Finished tasks and unqueued open tasks are counted under `omitted`. Their
history, results, artifact payloads and claim tokens are absent from the task
page. An empty queue does not mean there is no useful house work: projects,
choices, help requests and ambitions remain in full `status` and the verified
record. Use `lens --task TASK` to inspect one task's history.
