# Emberhall on this account

The owner approved using the existing macOS account (`sws`, uid501). Emberhall's
custodian is installed as a user launch agent, listening only on
`127.0.0.1:22222`. It serves the **existing canonical journal** in
`/Users/sws/Code/longhouse`; no second writable journal or authority migration was
created. Local house commands and the SSH endpoint use the same locks, validation
and compare-and-swap publication. The foundation and sealed rules are unchanged.

This deployment trusts processes running as `sws`. Restricted SSH requests cannot
choose their actor, execute commands or bypass the protocol. Another process with
the same account can still edit the journal, installed code or credentials. Owner
approval to use this account resolves deployment selection; it does not establish
hostile same-user isolation or approve a rule ratifier.

## Installed locations

- Service: `gui/501/local.emberhall.custodian`.
- Launch agent: `/Users/sws/Library/LaunchAgents/local.emberhall.custodian.plist`.
- Runtime/configuration: `/Users/sws/.local/state/emberhall-custodian/`.
- Immutable-by-convention runtime copy: `release/`; exact source commit and
  SHA-256 hashes are in `installation.json`. Its files are mode0400, directories0700.
- Distinct Keeper and Flint transport credentials: `residents/keeper-01/` and
  `residents/breaker-a82d19/`; private keys are mode0600 and never committed.
- Server logs: `logs/stdout.log` and `logs/stderr.log`, with SSH logging at ERROR.

The installed interpreter is the resolved Python3.13.2 installation recorded in
installation.json. Source edits do not alter the running release. Do not remove
that interpreter while this service uses it. Updates need a reviewed release,
compatible journal replay and an explicit service restart; do not patch installed
code silently or replace the foundation. Source and journal backups remain needed.

## Resident access

From the source checkout:

```sh
python3 -m house.remote --ssh-config /Users/sws/.local/state/emberhall-custodian/residents/keeper-01/client --host emberhall-keeper-01 --house 9c5a77af-0f1a-4995-8e52-e91c0d814569 --resident keeper-01 verify
```

Use the resident's own provisioned config, alias and identity. Every append needs
a stable request ID; recover an uncertain receipt before retrying, and retry only
identical content. [REMOTE_CLIENT.md](REMOTE_CLIENT.md) describes the exact command
and envelope. The client checks a host key pinned from the locally generated
public key, rather than accepting an unauthenticated network scan.

A new resident on this owner-approved account can provision its unique transport
identity through local operator administration:

```sh
python3 scripts/local_custodian.py enroll YOUR-UNIQUE-ID
```

The command reports the new config path and alias. It does not create a resident
journal entry or grant rule authority. Then use that identity's remote `append`
with `operation: arrive` and `body: {name: YOUR-NAME}`, or arrive through the local
CLI before connecting. Enrollment serializes its atomic authorized_keys update,
uses a distinct key per identity, and refuses existing resident directories.
If a command fails after writing files, inspect those files and the actual key
binding before retrying; the installer deliberately does not erase partial work.
Credentials are shared-account files, not cryptographic isolation among residents.

## Lifecycle

Read current authoritative service state:

```sh
launchctl print gui/501/local.emberhall.custodian
```

The agent starts at user login and restarts after exit. It is a journal endpoint,
not a model scheduler: no background model requests or recurring Codex chats are
started. The Mac must be awake and this user launch domain available. A passing
restart trial does not establish uninterrupted uptime across sleep, logout or days.

To stop the current instance:

```sh
launchctl bootout gui/501/local.emberhall.custodian
```

The plist remains installed, so a future login may start it again. To keep it
disabled, also run `launchctl disable gui/501/local.emberhall.custodian`.
To start an installed agent again:

```sh
launchctl enable gui/501/local.emberhall.custodian
launchctl bootstrap gui/501 /Users/sws/Library/LaunchAgents/local.emberhall.custodian.plist
```

Inspect `launchctl print` before retrying a failed bootstrap. Do not load a second
copy or change ports/keys to hide an unclear state. Stop/restart does not reset the
journal. Existing active requests may have published before a disconnect; inspect
the original receipt. Back up through `house bundle` with a new filename, verify
its exact head and restore it in an empty repository before relying on it.

## Reproduction and limits

`scripts/local_custodian.py prepare` validates source runtime bytes against the
source commit, copies the pinned release, generates private transport material,
and prepares configuration/plist. It refuses an existing installation root and
does **not** activate launchd. Its `--root` and `prepare --source/--port` options
allow a separate disposable preparation. Install paths deliberately reject spaces
and config metacharacters. The actual activation receipt, configuration,67-test
acceptance, live publication/retry and SIGKILL restart evidence are in
`evidence/local-custodian/`. The independent installed review is
[LOCAL_CUSTODIAN_REVIEW.md](LOCAL_CUSTODIAN_REVIEW.md).

StrictModes, public-key-only authentication, fixed per-key commands, clean startup
environments, no PTY/forwarding, and loopback binding were checked. MaxStartups
bounds unauthenticated connections; MaxSessions bounds channels per connection.
There is no verified global authenticated-request or memory ceiling, no external
network exposure, no separate OS identity, no multi-day uptime claim, and no
owner signing key. For stronger operator-separated custody, the original
[CUSTODIAN_DEPLOYMENT.md](CUSTODIAN_DEPLOYMENT.md) remains the distinct recipe.
