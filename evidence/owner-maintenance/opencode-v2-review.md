# OpenCode V2 compatibility repair: no-model witness

Witness prepared this repair in an ordinary private clone of source
`b40060326fbddd3e18b76b4c9c914d1896bd01a3`, on `codex/opencode-v2`, with its
origin removed. The failed real admission 462–466 remains a spent attempt;
this document neither grants another admission nor ratifies source activation.
Root integrates and records any owner-authorized repair separately.

The installed package is `@opencode/cli` 2.3.0. The earlier V1 adapter supplied
`run --dir`, which V2 rejects before the model starts. The existing V1
`tools/house_journal.js` also was not a V2 plugin. Merely deleting the flag
would have left the tool unavailable and could have reused a global service.

## Changed contract

The adapter now launches `run --standalone`, with both the process working
directory (set by the supervisor) and `PWD` bound to the resident's private
clone. V2 prefers `PWD` over `process.cwd()`. Standalone mode starts a private
stdio-owned server instead of connecting to an existing background service.
The provider/model allowance and native result parser are unchanged.

`opencode-config/plugins/house_journal.js` now exports a native V2 plugin with
`id` and `setup`. It registers one tool through `ctx.tool.transform`, using a
JSON-schema `input` and returning `{content}`. It asserts native permission
before invoking the existing fixed Python mailbox client, with `-I`, literal
argument arrays, no shell, bounded arguments/output/time, and fixed resident,
workspace and runtime. The tool propagates the native cancellation signal.
There is no runtime package installation or plugin dependency.

Global and selected-agent `permissions` share the deny-by-default envelope.
Only read/glob/grep/edit and the journal tool are allowed, retaining env-file
read exclusions and `.house-client` edit exclusions. Git metadata edits are denied for `.git`
and descendants, including nested paths and every ASCII case spelling of
`.git`, because macOS can resolve differently cased paths to the same directory. Shell, subagents, external
directories and Code Mode are explicitly denied. Policies additionally restrict
providers to `opencode-go`, deny MCP/skills/web search, enforce the tool envelope,
and reject external plugin imports except the exact generated journal file.

Inherited `OPENCODE_*` overrides are removed before setting supported V2
configuration variables. The config root and test-home are private; project
configuration and Claude skill discovery are disabled. The obsolete V1 pure,
default-plugin and external-skill flags were removed. Their names are absent
from the installed 2.3.0 binary; the tagged startup source does not honor them.
V2 does normalize old V1 permissions, so the original permission object was
not simply ignored. The replacement uses native fields to make the boundary
explicit and inspectable.

A later independent actual-tool probe found that V2 directory permission checks
are lexical: a workspace symlink bypasses both read and write confinement. The
production gate therefore rejects every symlink, hard link and special file in
the room before importing an account or executing the model. The restricted native
tool set cannot create links. Rooms have one assigned writer; this is not isolation
from a hostile same-user shell. See `opencode-v2-boundary-review.md` for the actual
witness and protected-path controls. Permission-object tests alone missed this.

## Native acceptance actually performed

Command, in the private clone:

```sh
EMBERHALL_NATIVE_OPENCODE=1 python3 -m unittest \
  tests.test_providers tests.test_opencode_tool tests.test_opencode_v2 -v
```

Observed: **12 tests passed in 0.798 seconds**. This included the installed
native binary, not a simulated OpenCode process. Its version output was
`opencode v2.3.0`; `run --standalone --help` accepted the launch flags.

The native fixture used empty, disposable XDG data/cache/state/config paths,
a private DB, disabled model-catalog fetching, and a stdio-owned private server.
Its fixed transport password was a disposable fixture value, not an account
credential. Native `debug agents --server <private endpoint>` initialized only
that server's test location. The fixture then:

- loaded the actual generated production plugin through V2 discovery;
- created a session without ever submitting a prompt or generating a title;
- observed the configured agent's native permission projection;
- saw native permission checks reject shell, subagent, external_directory,
  execute and webfetch actions, plus edits to `.house-client`, `.git/config`,
  `.GIT/hooks/pre-commit` and nested mixed-case Git paths; ordinary source edits
  remained allowed;
- called the journal tool through the native tool registry and received the
  assigned fixture identity and literal `status` arguments from a harmless
  fake mailbox runtime;
- proved that hostile project configuration plus plugins in both the project
  and private config directory did not execute their sentinel writes.

The Node subprocess test separately verifies literal shell metacharacters and
workspace Python-module shadowing cannot alter the fixed invocation. Native
fixture cleanup signals its owned process group and has a bounded kill fallback.
No real account data, global service or global configuration was used by these
probes. No model was launched and no canonical journal command was executed.

The first native fixture incorrectly invoked permission checks during plugin
setup, before configured agent transforms were ready; it was repaired to perform
checks after native location startup. A subsequent assertion was corrected for
the V2 agent response's `data` envelope. These were fixture defects, not evidence
of model operation. The passing check above is the final relevant receipt.

Additional boundary command:

```sh
python3 -m unittest tests.test_home tests.test_home_work \
  tests.test_mailbox tests.test_mailbox_jobs -v
```

Observed: **35 tests passed in 40.555 seconds**. Compilation, `git diff --check`,
and the anti-bloat advisory also passed. Full repository acceptance belongs to
the integrating resident after the separate owner-maintenance changes are ready.

## Account reuse repair prepared after this witness

The investigation found that V2 stores logins in the same SQLite database as
sessions. Fresh private databases import legacy `auth.json`, but a recent V2
login updates only the database. Importing that legacy file could therefore
repeat an expired login despite the owner's repair. The model must not share
the global database or service to get around this.

Under the owner's existing explicit account-reuse authorization, the integrated
adapter uses empty private XDG data/cache/state/config directories. Inside the
already gated and supervised process group, a bounded bootstrap opens the existing
database with SQLite `mode=ro` inside an OS write/network-denied child,
selects only the native active `opencode-go` row,
and sends that one existing key credential to native `auth import --standalone`
on stdin. It imports into an absent private database, avoiding stale selection.
SQLite can create WAL coordination files even in read-only mode; the OS fence
prevents that, and a cold WAL database needing such files fails closed.
The original credential ID is retained; no key is created or changed. No unrelated
credential, chat, session or history is copied. Unsupported credential types or
an existing destination fail closed. Native import output is discarded and errors
are generic so account material cannot enter evidence or launch logs.

This replaces the earlier incomplete idea of relying on V2's automatic legacy
import. Synthetic installed-CLI tests are required before deployment. A local
import alone does not prove remote credential validity, quota or residency; those
remain separate observations from the sole coordinator's later actual run.

The original parser failure and original spent credit stay intact. A separate
repair scope is bound to that exact exit1, empty usage, absent arrival, retained
stderr hash, run462–466, and latest budget observation465. Admission rechecks the
absence of a late arrival and any newer provider failure. Its credit is one-use;
it leaves the original maximum cooldown untouched. This scope also protects the
new account bootstrap module from ordinary resident runtime changes.

## Upstream evidence

All code investigation used tag `v2.3.0`:

- [CLI run/PWD](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/cli/src/run/run.ts)
- [Server selection](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/cli/src/services/server-connection.ts)
- [Supported server environment](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/cli/src/server-process.ts)
- [Plugin import policy and export contract](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/plugin/module.ts)
- [V2 tool schema](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/schema/src/tool.ts)
- [Legacy normalization](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/config/normalize.ts)
- [Automatic legacy credential import](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/database/migration/20260805200742_import_legacy_credentials.ts)
- [Credential DB writes](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/credential.ts)
- [Integration login persistence](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/integration.ts)

- [Credential table](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/core/src/credential/sql.ts)
- [Native selective export](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/cli/src/commands/handlers/auth/export.ts)
- [Native import semantics](https://github.com/anomalyco/opencode/blob/v2.3.0/packages/cli/src/commands/handlers/auth/import.ts)
