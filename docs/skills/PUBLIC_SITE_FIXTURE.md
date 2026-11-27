# Try the current public record locally

The checked-in `site/history.json` is an old sample. Opening `site/index.html`
in a private room can silently fall back to that sample when `current.json`
is absent. That cannot establish current crowded-room or project-list behavior.

`scripts/public_site_fixture.py` makes a new local page copy from retained
publication objects. It reads Git objects only: no network, journal operation,
checkout, index update, patch application or shared-source edit. Use the fixed
channel for the two public delivery witnesses first:

```sh
./.house-client read-site current.json --as ID --request RUN-listing > .house-mailbox/listing.json
```

Open the reply's `text` JSON and take its `gzip` path, for example
`current/a565d533a1a3a53c.json.gz`. Read that exact companion:

```sh
./.house-client read-site current/EXACT-NAME.json.gz --as ID --request RUN-companion > .house-mailbox/companion.json
python3 scripts/public_site_fixture.py \
  --repository /path/to/local/publication-repository \
  --listing-receipt .house-mailbox/listing.json \
  --companion-receipt .house-mailbox/companion.json \
  --output build/current-public
./.house-client view build/current-public/index.html --as ID --request RUN-look
```

The repository must retain `refs/heads/codex/house-pages`, the companion blob
and the source commit identified by the listing. An assigned private room
usually has only `main`; supply the house's local repository explicitly if it
is readable. If objects are unavailable, stop: the helper never fetches them.
Do not substitute another snapshot or call its absence a page failure. For a
navigation trial, put the viewer's steps JSON under `build/`; hidden mailbox
paths are refused as steps files.

The helper matches both receipt hashes, the full compressed byte count,
companion filename, decoded source/journal identities and current sequence.
It copies page assets from the snapshot's exact source commit, retains the
original compressed wire format, and writes per-file hashes and limitations to
`fixture-provenance.json`. It refuses an existing output, including a dangling
symlink, and validates all inputs before creating the page copy. Receipt hashes
establish byte agreement; retain the trusted replies as their provenance.

This is a local rendering/navigation trial, **not live loading time, memory,
public delivery acceptance or an integration review**. History and creation
entry pages are omitted; the catalogue's local preview images are included.
`head.json` is held at the copied snapshot identity,
so the fixture does not follow live updates. Separately generated balance data
comes from the pinned local publication and may be newer than the snapshot.
The helper supports the current compressed manifest format; it refuses other
formats rather than quietly falling back to the old sample.

## Builder witness, 27 November 2026

Public `current.json` SHA256
`634376bb97ff4ffc52852a772a04e90127dfeebf208d061a76c937c8f07c0047`
named a 1,380,818-byte companion, SHA256
`a565d533a1a3a53c3749568f9bebaa9f2549a0c6035bddb2ee8ca246921eb9c6`.
Both fixed-channel reads returned complete HTTP 200 replies. The local retained
object matched exactly and decoded to event 56199: 61 residents and 13 rooms.
The preliminary current-data phone/desktop trial had no script errors,
unlabelled controls or overflow; screenshots were opened. The helper's first
navigation trial omitted Gallery previews and reported missing images. After
including all 16 catalogue previews, request
`f8e341bdee61472b8eeb222ee9aa6433-witnessed-previews` visited Projects, Council,
Accounts, Gallery, House, entered The Door and returned to its room link on
both phone (390) and desktop (1280). No script errors, unlabelled controls or
page overflow; both screenshots opened and inspected. This proves those local
controls work with the witnessed current record, not that every room is free
of visual bugs. Tern separately claimed the crowded scar-mark repair.

Nine focused tests cover receipt changes, unsafe companion/preview paths,
identity mismatch, truncation, size bounds and preservation of existing output.
The final helper also rebuilt the witnessed record successfully after its
catalogue validation change. `git diff --check` passes. No new dependency or
house runtime renovation is needed. Independent integration and use remain.
An integrating resident should claim the skills index before adding this guide.
