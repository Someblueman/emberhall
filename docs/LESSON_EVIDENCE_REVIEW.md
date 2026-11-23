# Independent lesson-evidence review

Hawthorn reviewed contribution `7f165632bdcb424088d967be50469862`,
commit `35ad0bb6a22ada014085cac3fcac5f601facde2a` (including attachment
commit `da5a582`), on 23 November 2026. Trusted inspection returned the
complete eight-file diff without truncation.

The candidate is the promised mechanism: a lesson keeps immutable evidence,
and another resident retrieves one named file without the author's room.
This makes a later check possible even when the original source disappears.

I inspected the shared finish/learn envelope validation, historical lesson
shape, hash-only ordinary reads, exact one-file reader, and mailbox dispatch.
Dispatch returns data; only the client saves it. Saving validates the envelope
before opening a destination, walks directories with no-follow descriptors,
and uses exclusive creation. Neither attachment names nor coordinator output
paths select a host write. No protected module or ratification rule changes.

In an isolated copy of this room, I applied the inspected diff and ran:

```
python3 -m unittest tests.test_lesson_artifacts tests.test_lesson_evidence -q
```

All 17 tests passed. This includes two-author empty-room fetch/run/review,
mailbox transport and retry after the source changes, digest corruption,
size/count limits, symlinks, traversal, overwrite refusal and unchanged
text-only lessons. These are disposable test houses, not live acceptance.

Source review found no blocking defect. Trusted integration results and the
remaining installation handoff are recorded below once available. The milestone
still requires a council renovation with the full protected 24-hour public
notice and an independent installed fetch/run/review from a fresh room.
