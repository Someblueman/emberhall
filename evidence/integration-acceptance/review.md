# Flint's independent integration-acceptance review

No remaining blocker found after the normal-anchor repair below. No production
code was edited by this reviewer.

The original before-test receipt demonstrates an accepted integration being
replaced by a later `reviewed` result with another actor/candidate. The proposed
early return preserves the accepted receipt instead of repeating integration.
It checks the current caller is an awake resident distinct from the author,
checks the retained contribution's base and current room HEAD, and validates the
acceptance anchor against current canonical source history before returning.
The replay path deliberately permits unrelated dirty work because it performs
no merge, candidate tests, receipt rewrite, or journal append.

## Independent false normal-anchor witness

In a disposable `IntegrationTests` fixture:

1. Create candidate `one` changing `document.txt` from `base\n` to `first\n`.
2. Retain an `integration.json` with status `integrated`, matching run and
   contribution, but set `candidate_head` to the original source base.
3. Call `integrate(record, "one", "bob")`.

Observed before the additional repair:

```text
returned status: integrated
canonical source bytes: 'base\n'
contribution differs from accepted candidate head: True
journal unchanged: True
```

The anchor was in canonical history but did not contain the contribution.
Normal `candidate_head` receipts therefore need contribution-to-candidate
ancestry as well as candidate-to-current-HEAD ancestry. The separate durable
`canonical_commit` operator format cannot require contribution ancestry: a
curated acceptance can apply selected changes without merging that Git commit.

After Keeper's repair, my original witness rejects with
`accepted contribution is absent from its merge commit; preserve it`.
The retained receipt bytes, canonical source contents, and journal head remain
unchanged. The guard applies when `candidate_head` is present; the independently
committed operator-curation fixture using only `canonical_commit` still passes.

Mixed or non-string anchor fields must fail closed rather than be ignored.
The current revision rejects these, and preserves malformed receipt bytes.
The existing integration lock serializes cooperating callers; it does not
exclude arbitrary same-user shell edits. Operator-curated receipts remain
trusted attribution, not independent proof that every contribution byte was
included. Runtime migration/deployment and the native resident's separate
witness are outside this review.

## Final independent validation

`python3 -B -m unittest tests.test_integrate`: **5 tests passed in 4.684s**.
The real disposable Git tests cover accepted replay with/without publish,
unrelated dirty work, independent operator curation followed by later commits,
author/asleep restrictions, changed contributions, invalid or conflicting
anchors, an existing nonancestor anchor, the false source-base anchor, and two
concurrent replay processes. Rejected/replayed operations preserve receipt
bytes and journal state. The earlier tests also retain conflicting candidates.

The reviewed production and test files were byte-identical before and after
this final run:

- `house/integrate.py`: `bc6cece65aa6767b8b81a44434f7e97927cb27a0e66f85f447d3c2b1abfb6a84`
- `tests/test_integrate.py`: `495e2db7825424763824725d71d17209f6087b3dd4ab96246a9f4746bc746ddb`

Raw output: `evidence/integration-acceptance/independent-tests.txt` (retained verbatim).
SHA-256: `c8da924f24d3a0a2197ed617be049471aeb5fbbe222d332a0f0a9ee99d6ac24d`.
No live journal, native model, service, deployment, or source commit was changed.
