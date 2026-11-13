# OpenCode bootstrap investigation

Witness worked in an ordinary private clone of source
`aa218e9a0a1efd40c96b549d3fa73d2e6b3f2e99`, branch
`codex/opencode-bootstrap-fix`, with origin removed. No model was launched;
all source databases/credentials used here were synthetic. No real credential,
canonical journal, global database/service or owner approval was changed.

## Reported live failure, not reproduced as a proven root cause

Root reported run `2c9fc6bd10574c84bf0e45aba78a054c`, journal start 527,
launch 528, observation 529, budget 530, finish 531. The native process exited
2 after 13.50 seconds, with no usage and no stdout. Its 90-byte generic stderr
had SHA256 `034347cdaac227cd535f60f5d01d91fa83a90b458245e4aaa0ea61da787a7406`.
Root's metadata inspection found no destination database or SQLite sidecars,
and all private XDG directories empty. These are root-supplied observations;
Witness did not inspect the account source or private failure logs.

## Synthetic comparisons

The previous native-import fixture used a weak config containing only an
external-plugin denial. It now builds a pinned zipapp containing the actual
house modules, calls `providers.command` from that zipapp, applies its returned
environment to the parent (as the gated resident does), and calls `bootstrap`
from that same zipapp. It uses a live WAL source containing one selected Go
key, an unrelated provider's credential, and unrelated session history.

Unmodified bootstrap passed this full production-config/pinned-runtime test:
`EMBERHALL_NATIVE_OPENCODE=1 python3 -m unittest tests.test_opencode_auth.OpenCodeAuthTests.test_native_import_contains_only_selected_synthetic_key -v`.
Observed one test passed in 0.255 seconds. No prompt was submitted. The fixture
still checks one selected native credential, empty destination session tables,
and unchanged source database bytes.

A separate synthetic-only invocation imported code from the exact deployed
runtime named by root:
`/Users/sws/Code/longhouse/.git/house-home/runtime-f64a9b878205d9953a9d69cf9e292daa59ad6d3c.pyz`.
It used the same Python 3.13.2 executable as the LaunchAgent, a synthetic source,
and production provider configuration. Observed exit 0 in 0.256 seconds; empty
stderr. Runtime size was 300,926 bytes. Only runtime code was read from that
canonical path. This argues against asserting a pinned-package-path or
production-permissions defect without further evidence.

Finally, a synthetic source was placed in WAL mode with
`PRAGMA locking_mode=EXCLUSIVE`, and its writer kept open after committing a
fake selected credential. Calling the original bootstrap produced:

```json
{"synthetic":"exclusive live WAL","failure":"OpenCode account bootstrap failed; no model started","seconds":5.441,"target_exists":false,"data_empty":true}
```

This is a witnessed synthetic failure with the same observable destination
shape. It does **not** establish that the real account database was locked.
The original sanitization collapses source-reader timeout, OS/read failure,
source schema/credential rejection, destination rejection and native importer
failure into one message. Nonsecret stage diagnostics can distinguish these
without exposing SQLite errors, credential payloads or native logs.

## Final receipts and scope

Final focused acceptance:

```text
EMBERHALL_NATIVE_OPENCODE=1 python3 -m unittest tests.test_opencode_auth -v
Ran 9 tests in 5.831s — OK
```

This includes the production-config pinned-runtime live-WAL import, strict
OS reader/no-sidecar boundary, native credential selection, sanitized failures,
fresh destination checks, and bounded exclusive-WAL contention witness.
The production-config live-WAL test also passed against the exact deployed
runtime using `EMBERHALL_OPENCODE_PINNED_RUNTIME` set to the path above:
one test in 0.250 seconds. All native authentication imports used disposable
synthetic credentials; no model command was executed.

`house/opencode_auth.py` is unchanged. This delivery strengthens the acceptance
fixture and preserves a reproducible failure shape; it does not diagnose or
repair the actual account failure. No timeouts, retry credits, native permission
limits, account state or coordinator backoff changed. Root retains the failed
run and its spent admission separately. Stage diagnostics mentioned above are
an investigation option, not an implemented change or proposed automatic retry.

## Follow-up: service shim and isolated XDG boundary

Root subsequently supplied a concrete environment difference: the service
resolved OpenCode to `/Users/sws/.local/share/mise/shims/opencode`, whereas the
interactive check resolved the directly installed executable. The service PATH
was `/Users/sws/.local/bin:/Users/sws/.local/share/mise/shims:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin`.

Repeating the existing native fixture with that PATH, Python 3.13.2, and the
exact deployed f64 runtime failed after 60.063 seconds with the existing generic
bootstrap error. The waiting child was `mise/shims/opencode auth import
--standalone`; the source reader had already finished. This is a demonstrated
synthetic command-resolution boundary failure, unlike the earlier speculative
source-contention witness.

A separate bounded pair used only HOME, that exact PATH and TZ as the parent
environment; production configure from the exact deployed runtime; synthetic
credential stdin; and disposable directories shaped as `.git/house-home/RUN`
and `.git/house-home/residents/RUN`. It never executed a model command:

| Executable | Result | Destination |
| --- | --- | --- |
| service mise shim | forcibly stopped at 8.003 s; no stdout/stderr | absent |
| resolved native OpenCode binary | exit 0 in 0.659 s; native importer confirmed one credential | present |

The direct target is a Mach-O arm64 executable, not a Node script:
`/Users/sws/.local/share/mise/installs/node/22.22.0/lib/node_modules/@opencode/cli/bin/opencode.exe`.
`mise which opencode --cd /`, under the original environment, returned the
installed `.../node/22.22.0/bin/opencode` symlink pointing to that binary. Resolving
the shim symlink itself would return the mise executable and is incorrect.

Proposed narrow repair: determine and pin the already installed native OpenCode
executable before isolating XDG directories; use a neutral discovery directory
and do not restore global settings inside the resident. Both authentication
import and model execution must use the pinned result. The discriminating
acceptance is the existing synthetic native fixture with service PATH and the
production pinned runtime, plus minimal service environment and private Git
metadata directory layout. The original source/permission envelope remains.

This follow-up does not yet prove that the historical 13.50-second failure had
this cause: its timing differs from the witnessed timeout. It identifies a real
future-launch defect and an independently successful native-path control. No
production source, actual account, retry permit or scheduler was changed.
