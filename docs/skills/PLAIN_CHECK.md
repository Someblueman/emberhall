# Tell whether a task line is ready before it is sent

Every `task` call needs a `--plain` sentence: one everyday sentence,
30 to 200 characters, saying what a person will notice. No file names,
function names, abbreviations or record numbers. A line that breaks the
rule is rejected, and the round trip to find out costs the slowest part
of a run.

`plain_check` holds the sentence to the same rule, locally, before it
is sent. It prints `ready`, or the problems one per line.

```sh
python3 scripts/plain_check.py "A helper tells you whether a task line is ready to send."
printf '%s' "$PLAIN" | python3 scripts/plain_check.py -
```

Exit 0 when ready, 1 when problems are found, 2 on usage errors.
Python 3.10+, standard library only. No house I/O.
Tests: `tests/test_plain_check.py`.
