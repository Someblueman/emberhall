# Snapshot-age contribution

Cairn (Gemini) built the house snapshot-age cue, task2223, claim2248,
finish2250, sleep2256. Its stopped source is commit
7f965acb5033899984dae99ca484dac69239b49c. Keeper inspected the complete
committed diff and matched every original file to the immutable finish hashes.
The native commit remains an ancestor of the curated source acceptance.

Keeper reproduced a RangeError for a finite out-of-range timestamp (1e20),
then checked the actual Date range before formatting. Future dates within a
minute now also say ahead of clock. The revised test exercises the real formatter
and lighting function, invalid and unknown dates, age units, London/New York
formatting and the current/history transition. The original phone-layout claim
was narrowed to intended CSS behavior because no browser witness exists.

before.txt records the real failing regression. focused-tests.txt records the
passing focused suite; JavaScript syntax and Git whitespace checks also passed.
The scope covers this UI change, the existing Parlor refresh and catch-up
behavior, public-history decoding and record-derived body export. This is an
owner-operator curated acceptance, not a full foundation integration gate.
No protected runtime source, pins or permissions changed.

The supervisor reported failed at2262/2264 despite exit0, finished artifacts
and an explicit sleep. That classification is retained, not rewritten; source
preservation and contribution review are independently evidenced here.

The public site has not been updated or browser-checked for this feature.
Publisher activation is still awaiting the separate exact owner authorization.
