# A real zero-test discovery failure and repair

Returning OpenCode Juniper actually inspected the case-bible contribution through
the new fixed channel, then attempted independent acceptance. Receipt1728 refused
it with test_exit5 because unittest discovery found zero tests, before the JSON
syntax check. The failed receipt and exact log are retained here. No source was
published by that failed attempt.

The correction uses TestLoader and TextTestRunner directly for project checks.
It reports the actual count, including zero, preserves loading/test failures,
and continues to the applicable syntax checks. Foundation checks are unchanged.
A real sandbox regression accepts prose/valid JSON without dummy tests and still
refuses malformed JSON. Focused8 passed5.509s; full host431 passed421/10 skips in
411.204s. Emberwick independently reviewed exact3-file hashes1749 and directly
witnessed empty/passing/failing/erroring exit codes0/0/1/1, plus JSON refusal.

Isolated owner preparation and activation remain pending at this commit. The
new narrow project-checks-20261114 scope changes only owner modules/integrate;
no sandbox, governance, native permissions or project files change. After it is
installed, one explicit native case retry is required: the earlier automatic
review correctly resolved with a failed-check disposition rather than looping.
