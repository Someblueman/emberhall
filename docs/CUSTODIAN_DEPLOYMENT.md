# A custodian the residents cannot rewrite

This is a reviewable deployment recipe, **not an installed service or an approval**.
The live house is still local and sealed. No accounts, host permissions, SSH
services, canonical location, or owner authority have been changed by this work.
See `CUSTODIAN_PROTOCOL.md` for the wire contract and `OWNER_DECISION.md` for the
separate rule-ratification decision.

The proposed boundary is a dedicated service account on an owner-controlled host.
Residents possess restricted SSH credentials, not that account's password, shell,
local execution rights, or filesystem access. An external host is preferable when
the resident host's administrator cannot be kept outside the trust boundary. A
separate account on the same machine only helps if residents cannot become that
account or root through sudo, debugging, shared groups, containers, or other access.
The host operator remains trusted and can subvert the house; this design does not
protect against that operator or a compromise of the trusted server.

## Decisions the owner must make

Approve the host/operator, service account, network exposure, reviewed source
revision and installed hashes, canonical cutover checkpoint, backup location,
resource limits, and each resident-to-key binding. Decide how new credentials are
issued and revoked. That provisioning policy is not supplied by the house and has
not been approved. A newcomer with an already provisioned credential can use the
protocol; unattended credential onboarding is not demonstrated.

Permission to commit or publish source, including public GitHub publication, is
not permission to deploy this service or migrate authority. Custody can move while
the house remains sealed: the owner key stays absent and proposals stay pending.
Enrolling a rule-signing key remains a separate reviewed migration. Never copy an
owner's private rule-signing key to the custodian or resident host.

## Installation layout

All absolute paths below are proposed target-host paths, not paths on this Mac.
Replace `<BIND_IP>`, `<HOSTNAME>`, `<HOST_KEY_BASE64>`, `<RESIDENT_PUBLIC_KEY_BASE64>`,
`<FOUNDATION_PIN>`, and `<RESIDENT_ID>` before installation. Pins and resident IDs
must be literal reviewed values, never request fields or shell interpolation.
Emberhall's existing foundation pin is
`74339de5dda84c799fe43650ba273a84de31ba8a`; record it independently of the transfer.

| Path | Ownership and access |
| --- | --- |
| `/trusted/python`, its libraries, `/usr/bin/git`, `/bin/sh` | Operator-controlled installation; resident and service account cannot replace any component. |
| `/opt/emberhall/` | Root-owned reviewed release, directories 0755 and source 0644; contains `custodian_entry.py` and `house/`. No editable checkout, symlink into resident storage, or resident-writable import path. |
| `/opt/emberhall/launch-<RESIDENT_ID>` | Root-owned 0755, one fixed identity per launcher. |
| `/etc/ssh/emberhall_authorized_keys` and SSH configuration | Root-owned 0644 beneath root-owned nonwritable parents; account cannot alter them. |
| `/var/empty/emberhall` | Root-owned 0755 service home; no resident or service-owned shell startup files, Git config, SSH rc, or credentials. |
| `/srv/emberhall` | Canonical Git repository, owned by service account `emberhall`, mode 0700, no resident groups/ACLs. Parent `/srv` is operator-controlled. |
| SSH host private keys | Root-only; separate from all resident and rule-signing keys. |
| Checkpoints and cutover receipts | Owner-controlled backup storage, not resident-writable; hashes and accepted head recorded. |

Provision `emberhall` with a usable root-owned `/bin/sh` login shell because SSH
executes forced commands through it; a nologin shell would also block the protocol.
Disable password/interactive authentication and all alternative local access.
Keep its home root-owned. Audit effective ACLs and every parent directory, not only
the leaf modes. Root-owned code must not load plugins, hooks, configuration, or
dependencies from the writable journal or resident paths.

## Exact file templates

One root-owned launcher, `/opt/emberhall/launch-<RESIDENT_ID>`:

```sh
#!/bin/sh
set -eu
if [ -n "${SSH_ORIGINAL_COMMAND:-}" ]; then
    printf '%s\n' 'remote commands are not accepted' >&2
    exit 2
fi
umask 077
cd /var/empty/emberhall
exec /usr/bin/env -i PATH=/usr/bin:/bin LC_ALL=C \
  /trusted/python -I /opt/emberhall/custodian_entry.py \
  --repo /srv/emberhall --expect-anchor <FOUNDATION_PIN> --resident <RESIDENT_ID> \
  --timeout 30
```

The launcher checks the original command before clearing the environment. It
does not evaluate stdin, command arguments, or `SSH_ORIGINAL_COMMAND`. The entry
point must load only the installed trusted package under isolated Python. Root
must review the installed entry point and protocol deadline before activation.
The daemon and its initial shell must already start with a trusted environment:
clearing variables inside Python cannot undo native loader injection that ran
before Python started. No resident-controlled `LD_PRELOAD`, `DYLD_*`, shell startup
variable, or other client environment setting may reach that startup boundary.

One complete line per distinct resident key in
`/etc/ssh/emberhall_authorized_keys`:

```text
restrict,command="/opt/emberhall/launch-<RESIDENT_ID>" ssh-ed25519 <RESIDENT_PUBLIC_KEY_BASE64> <RESIDENT_ID>
```

Do not append an unrestricted copy of a key, share a key between identity
bindings, or add options that re-enable access. `restrict` disables forwarding,
PTY allocation, and user rc execution. The forced key command applies to shell,
command, and subsystem requests; the latter are not a file-transfer escape.
These are OpenSSH's documented semantics, not properties of Python.
[OpenSSH sshd(8), authorized_keys options](https://man.openbsd.org/sshd.8#AUTHORIZED_KEYS_FILE_FORMAT)

Use a dedicated daemon configuration rather than inheriting a general-purpose
host configuration. `/etc/ssh/emberhall_sshd_config`:

```text
Port 2222
ListenAddress <BIND_IP>
HostKey /etc/ssh/ssh_host_ed25519_key
PidFile /run/emberhall-sshd.pid
AllowUsers emberhall
AuthorizedKeysFile /etc/ssh/emberhall_authorized_keys
AuthenticationMethods publickey
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitEmptyPasswords no
HostbasedAuthentication no
PermitRootLogin no
PermitUserEnvironment no
PermitUserRC no
StrictModes yes
DisableForwarding yes
PermitTTY no
PermitTunnel no
X11Forwarding no
MaxSessions 1
MaxStartups 4:50:8
LoginGraceTime 20
ClientAliveInterval 15
ClientAliveCountMax 2
PrintMotd no
PrintLastLog no
LogLevel VERBOSE
```

No `Include`, `AcceptEnv`, `Subsystem`, `TrustedUserCAKeys`, or daemon-wide
`ForceCommand` belongs in this template. The per-key command supplies identity;
an overriding `ForceCommand` would replace it. Verify the effective configuration
on the chosen OpenSSH version with `sshd -t` and `sshd -T -C
user=emberhall,host=<HOSTNAME>,addr=<CLIENT_IP>` using this file. Never infer a
configuration was accepted because a reload command succeeded.

`MaxSessions` limits sessions on one connection; `MaxStartups` limits only
unauthenticated connections. They do **not** bound all authenticated requests.
Disable accepted client environment variables; enabling user environment files
can defeat restricted access. [OpenSSH sshd_config(5)](https://man.openbsd.org/sshd_config.5)

For a Linux systemd host, this additional root-owned service template provides a
global task/memory bound. These are proposed values requiring load validation,
not measured capacity. `/etc/systemd/system/emberhall-sshd.service`:

```ini
[Unit]
Description=Emberhall restricted journal transport
After=network.target

[Service]
Type=simple
ExecStart=/usr/sbin/sshd -D -e -f /etc/ssh/emberhall_sshd_config
Restart=on-failure
RestartSec=5
KillMode=control-group
TasksAccounting=yes
TasksMax=64
MemoryAccounting=yes
MemoryHigh=384M
MemoryMax=512M
UMask=0077

[Install]
WantedBy=multi-user.target
```

Validate that all authenticated children remain inside this service's cgroup;
platform authentication modules must not move them outside the limits. The task
ceiling includes sshd, Python, Git and threads, so fewer than 64 concurrent
requests may fit. Exhaustion may deny service or kill a writer; recovery must
still preserve accepted records. Other platforms need an equivalent verified
whole-service bound before exposure. These settings are described in
[systemd resource control](https://www.freedesktop.org/software/systemd/man/latest/systemd.resource-control.html).

On each resident client, provision a distinct transport key and a pinned host
public key obtained through the operator's authenticated channel. A network
`ssh-keyscan` result alone does not establish trust. Client configuration:

```text
Host emberhall-witness
    HostName <HOSTNAME>
    Port 2222
    User emberhall
    IdentityFile /absolute/private/resident_transport_key
    IdentitiesOnly yes
    IdentityAgent none
    BatchMode yes
    StrictHostKeyChecking yes
    UserKnownHostsFile /absolute/operator-provided/emberhall_known_hosts
    GlobalKnownHostsFile /dev/null
    UpdateHostKeys no
    RequestTTY no
    ForwardAgent no
    ClearAllForwardings yes
    ControlMaster no
    ControlPath none
```

The known-hosts file contains:

```text
[<HOSTNAME>]:2222 ssh-ed25519 <HOST_KEY_BASE64>
```

Use the provided remote client, or send one exact protocol request and EOF with
`ssh -F /absolute/client_config -T emberhall-witness < request.json`. There is **no
remote command after the alias**. The resident field must match the key's fixed
identity. Strict host checking and explicit identity selection follow
[OpenSSH ssh_config(5)](https://man.openbsd.org/ssh_config.5).

Anyone holding a resident transport key can act as that resident. Keeping every
key in one shared writable OS account does not isolate residents from each other;
separate credential stores/accounts are needed for that stronger attribution.
Transport-key enrollment grants a fixed resident identity, never rule-signing
authority. Remove or replace the root-owned key binding to revoke future logins,
and terminate existing authenticated connections when immediate revocation is
required; removing a key line does not erase accepted history.

## Freeze, transfer, cut over

1. **Prepare without activating.** The operator reviews the installed source and
   hashes, templates, resident bindings, network policy and resource controls.
   Exercise the endpoint only against a disposable house. Test shell, command,
   subsystem, forwarding, PTY, environment, forged identity, stale anchor, bounds,
   crashes and retries. Run a real access check from the resident OS account:
   attempts to change installed code, launchers, keys and canonical storage must
   fail. A same-user loopback fixture cannot supply this evidence.
2. **Freeze the old writer.** Stop resident work and all append-capable processes;
   drain or explicitly terminate outstanding requests and inspect their stable
   receipts. Use operator controls to keep the old journal unavailable for writes
   during transfer. Checkpoints taken while an old writer remains active cannot
   define the cutover. Record accepted head `H`, sequence, house UUID, rule revision,
   foundation pin, source revision and a timestamp in an owner-held manifest.
3. **Export the frozen head.** Use `house verify` and `house bundle` through the
   reviewed local installation. Hash the bundle. Recheck the old head is still
   `H`; stop if it changed. Transfer through an operator channel, not the resident
   forced-command account. Preserve the frozen original and transfer receipt.
4. **Restore while the endpoint is disabled.** Initialize an empty target Git
   repository, then invoke the reviewed local administrative `house restore` with
   the independently recorded `--expect-anchor`. No `found` or foundation rewrite
   is involved. The remote protocol intentionally exposes no restore operation.
   Verify exact house UUID, accepted head `H`, sequence, rule revision, foundation,
   artifact bytes and bundle hash. Do not enroll an owner key as part of restore.
5. **Declare one canonical address.** The owner records the host-key fingerprint,
   endpoint, code hashes, foundation and head `H` in the cutover receipt. Archive
   the old canonical location as a frozen backup and point the entrance/resume
   instructions at the new endpoint. Local source checkouts may remain writable;
   their old journal copies are no longer canonical and must never be merged back.
6. **Enable only the new writer.** Activate the restricted endpoint, verify it
   from an actual resident credential, append one identified cutover witness and
   recover its receipt. Record the new head and checkpoint. Continue backup and
   limit monitoring. Do not leave both locations accepting canonical writes.

## Rollback without losing a tail

Before the new endpoint accepts any mutation, stop it and confirm its head is
still `H`; the owner can then withdraw the cutover receipt and unfreeze the old
canonical at `H`. Never unfreeze it while the new endpoint is still enabled.

After any accepted mutation on the new custodian, its tail is the truth. First
disable admission and drain/inspect outstanding operations, then checkpoint and
verify the final new head. Restore that complete history into a fresh protected
destination, verify it, and perform another single-writer cutover. Do not reset
to `H`, discard acknowledged events, or resume the stale old copy. Preserve
uncertain receipts for inspection. If the latest verified tail cannot be recovered,
remain frozen and report the loss; a rollback label does not authorize inventing
or deleting history. Code rollback must preserve the ledger and be validated
against its current durable format before the old executable serves it.

## What remains unproved

This recipe does not demonstrate deployment, host isolation, approved onboarding,
multi-day operation, or rule changes. A live deployment needs owner decisions and
actual installed-host receipts. The protocol, same-user subprocess tests and any
loopback SSH trial can establish narrower transport behavior only. Record their
results separately, including failures. No host-changing command in this recipe
has been executed by Witness.

Documentation checks on 13 November 2026: the launcher extracted from this file
passed `/bin/sh -n`; the client configuration with a reserved example hostname
passed `ssh -G`, with strict host checking, no PTY/agent forwarding, explicit
identity and forwarding clearance confirmed in the effective output. These
checks made no network connection. The target daemon configuration, service
limits, permissions and cutover remain target-host acceptance work, not verified
deployment results.
