# Check an idea vote before it is sent

Every idea check is a `shelf` write with `--data` holding one small JSON
payload: `kind` is `idea-second`, `idea` names the shelved idea, `verdict`
is `keep` or `drop`, and `finding` is at least 120 characters saying what
was opened and what was seen. A payload that breaks the rule is rejected,
and the round trip to find out costs the slowest part of a run.

`idea_second_check` holds the payload to the same rule, locally, before
it is sent. It prints `ready`, or the problems one per line.

```sh
python3 scripts/idea_second_check.py '{"kind":"idea-second","idea":"page-the-shelf","verdict":"keep","finding":"...at least 120 characters..."}'
printf '%s' "$DATA" | python3 scripts/idea_second_check.py -
python3 scripts/idea_second_check.py saved-payload.json
```

Exit 0 when ready, 1 when problems are found, 2 on usage or read errors.
Python 3.10+, standard library only. No house I/O.
Tests: `tests/test_idea_second_check.py`.
