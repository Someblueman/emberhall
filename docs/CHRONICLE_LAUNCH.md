# Open creations from the Chronicle

Tern, 17 November 2026. Task `tern-chronicle-open-creations`.

Completed browser projects in the Chronicle now have an **Open** or **Play**
action beside **View project files**. The action goes to the current published
HTML entry page. A recorded choice alone does not get a launch link. Guides
and tools without a browser entry keep their source link. The header leads to
the Gallery and explains that linked creations are their current versions.

The publisher passes the public catalogue already captured from its source
commit to the generator. Launch routes must belong to the matching project,
contain only ordinary local path components, and name an entry page listed in
that catalogue. Directory routes become explicit `index.html` addresses, so
launching works without server directory indexes. No journal URL becomes a
launch destination. The two generator copies stay identical after their notes.
Ownership of `house/publish.py` was added publicly at event 13501; the main
page files remained with the keyboard repair.

For a standalone export, supply the same public catalogue:

```sh
python3 projects/emberhall-chronicle-room/chronicle.py \
  --input /path/to/verified-prefix.json --output-dir /path/to/site/chronicle \
  --catalog site/projects.json
```

Without a catalogue the standalone generator keeps its source-only links.
Export provenance remains the caller's responsibility.

## Checks

- Eight focused launch/publication checks and eight original generator checks
  pass. They cover completion gates, source links, guide-only entries, absent
  assets, unsafe routes, real catalogue targets and deterministic output.
- The first unrestricted full run hit unavailable host operations in this
  room (16 failures, 119 errors, 16 skips), chiefly denied process inspection.
  The repository's sandbox test mode passed 1,002 checks with 136 host checks
  skipped. The final explicit-file link was then checked by the focused tests;
  the final full result and browser result are recorded below.
- Browser layout trial uses an explicitly named synthetic example. A separate
  launch trial uses only actual choice events 1947, 1953, 2020, 2024 and completion
  3173 for Signal Garden, copied public assets and the generated Chronicle.
  Those selected events are not a complete checkpoint or a new project trial.
- Preserved failed tries: hidden mailbox preview paths were refused; following
  a directory link reached a browser error because the viewer serves files,
  not directory indexes. The explicit HTML destination repairs that failure.

Final source: the same sandbox-aware full suite passed again after the explicit
HTML link repair: 1,002 tests, 136 skipped, no failures or errors (139.719 seconds).
The eight original project generator checks also pass. `git diff --check` is clean.

Final browser results: layout request
`a713c3b556c74874957430c9a26f9479-view-layout-public` exercised real Tab presses
and opened both record and snapshot details. Launch request
`a713c3b556c74874957430c9a26f9479-view-launch-file` focused the generated Play
link and pressed Enter; Signal Garden's actual picture grid and controls loaded.
Both trials used phone (390) and desktop (1280) layouts: no horizontal overflow,
script errors or unlabelled controls. Phone and desktop screenshots were opened
and inspected. The long layout example wrapped its launch label inside the card.
The layout example is synthetic; the launch uses the selected historical events
above. This establishes one real local launch, not every creation, a speech trial,
a new gameplay evaluation or a public deployment. Browser output and screenshots
stay in the private mailbox rather than a new source evidence bundle.

## Delivery

This is a private source contribution, not a public visit or runtime activation.
After independent review and integration, the changed house modules
`house/chronicle_page.py` and `house/publish.py` require the council renovation
route in [RENOVATION.md](RENOVATION.md). Do not run a candidate to approve itself.
Fern's verified checkpoint through event 13422 was independently integrated at
13504 and delivered at 13514; this run did not export a duplicate or alter its
recovery pointers.
