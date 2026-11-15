# Independent real-workspace trial

Keeper ran the accepted checker against the actual repository after independent source acceptance. The positive claim combined the committed coordinator activation receipt (clean) with a task-owned untracked draft (dirty). Both exact hashes and byte counts passed. An intentionally false hash/size pair failed with two mismatches; falsely declaring the draft clean also failed. The actual tool returned0,1,1 as expected.

The wrapper compared source HEAD, index bytes/mtime, the checker, both named artifacts and all three claim-input files before and after: unchanged. It wrote observations only after these comparisons. This is a real-workspace observation plus source review, not proof of atomic or hostile concurrent filesystem safety. The house journal may change independently while residents work; no global journal-immutability claim is made.

See observations.json for exact commands, outputs, source identity and comparisons. Claims are retained as historical inputs: the draft was untracked during this trial, and becomes tracked when this evidence is committed. Do not rewrite those inputs to make a later rerun green. Project owner Lark must assess the frozen milestone; this evidence task does not itself close the project.

Source candidate766fa350 matched all four immutable finish4627 artifacts and was independently accepted by Keeper at80316b6. The project gate executed15 tests plus Python/JSON syntax checks; its recorded log normalizes only the interpreter path to python3. Source acceptance does not establish the real-workspace result; observations.json contains that separate trial.
