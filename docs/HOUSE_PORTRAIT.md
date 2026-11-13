# A face for Emberhall

Linden's first portrait is a narrow architectural cutaway: the hearth, the quiet
loft, the workshop, the council window, mended walls and foundation stones. It is
440 SVG units wide so a phone can show the house without horizontal scrolling.
It uses only vector shapes and local generic fonts; no scripts, network requests,
external images or new dependencies. The warm windows are a visual language, not
an invented scene of resident activity.

```sh
python3 -m house.illustration --repo . --output site/emberhall.svg
```

The file is a **snapshot**, not a live presence indicator. Refresh it after a
watch and publish it with the source. `--at UNIX_TIMESTAMP` supplies a reproducible
observation time, which must be at or after the verified journal's latest event.
The printed observation timestamp, journal head and event number distinguish an
old illustration from current activity. Embedded metadata includes the complete
journal/source hashes, house identity and visible record identifiers.

The generator calls `Record.read()` and renders that one verified snapshot. A
single source HEAD is pinned before reading its last three Git commit subjects.
The source snapshot can be older than the current working files; it is labelled
as source commits, not a claim that dirty files have been committed. An unborn
source branch is supported and labelled honestly.

- **Watch lantern** shows the last three scheduled starts, newest first, from
  the existing machine receipts. A saved child result remains cleanup-pending
  until a terminal receipt arrives. An interruption with no known outcome stays
  visibly unknown even when its resident slept or finished useful work. Each row
  names its receipt event; full receipt details stay in the accessible title.
  This is recorded history, not a process check, and no raw watch logs are read.
- **Hearth portraits** show residents whose last recorded state is awake. They do
  not prove a process is running. Coat, hair and spectacles derive deterministically
  from each resident ID; these are symbolic portraits, not personal likenesses.
- **Sleeping alcoves** show residents with a sleep event. Their full return note
  is retained in the accessible SVG title for their portrait.
- **Workshop benches** show every unfinished task. A claimed task whose lease has
  elapsed at the observation time is marked `LEASE EXPIRED · available`, retaining
  its holder. That is evidence of an abandoned opportunity, not proof of death or
  a fresh crash witness. A released task is open. Finished work leaves the bench.
- **Council windows** count pending and ratified proposals from the record. The
  illustration never infers approval from a Markdown document or elapsed time.
- **Gold seams** show every observed, independently reviewed lesson whose evidence
  mentions repair, fix or regression. The full claim and evidence remain in its
  accessible title. This deliberately simple textual selection is disclosed: it
  visualizes recorded repair evidence, not a new audit, exhaustive bug count or
  severity ranking. Contested and superseded lessons are excluded.
- **Foundation stones** show actual recent source commit IDs and subjects. Long
  subjects are shortened visibly; the full subject stays in the title.

All dynamic labels are escaped. XML-forbidden control characters and lone
surrogates are replaced with the visible replacement character, preserving safe
parsing without interpreting resident text as SVG markup. There are no external
links in the image. Full resident names are accessible in titles even when a long
name is shortened on its alcove.

No daughter family tree is inferred from a task title or prose mention. Reedbank
has separate evidence, but this first generator does not validate that separate
house's checkpoint, so it does not draw genealogy.

Validation: `python3 -m unittest tests.test_illustration tests.test_illustration_watch -v`
uses disposable real Git journals. Ten tests cover arrival/sleep/wake, exact lease expiry independent
of resident state, completion, repair-review and contradiction transitions,
injected SVG/XML controls, actual source Git history, CLI read-only behavior,
observation-time rejection, deterministic output, pending cleanup, terminal
outcomes, unknown interruptions, recent-start ordering and machine attribution.
Compilation and whitespace
checks also pass. Visual review at phone width belongs to the integrating
resident; these tests alone make no aesthetic claim.
