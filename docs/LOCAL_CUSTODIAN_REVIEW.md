# Superseded local custodian review

Flint (`breaker-a82d19`), 13 November 2026. Task `local-custodian-review`.

**This deployment direction was superseded while review was finishing.** The
Steward's updated “Raise a House” objective explicitly defines residents as
cooperative but fallible and says not to build custodians or OS isolation unless
a cooperative resident actually breaks a wall. Keeper is handling deactivation
of the newly installed launch agent. Flint stopped all endpoint testing on
receiving that instruction. This report preserves historical observations; it
is not a recommendation to retain or reactivate the service and does not certify
its current post-deactivation state.

The updated objective also approves a trial/two-independent-endorsement/24-hour-
without-veto ratification process, bounded headless resident scheduling, and a
phone-visible house with veto. Those are Keeper's new work, outside this closed
review. The unchanged-authority statements below describe the tested snapshot,
not a claim that the house must remain sealed forever.

## Authorized scope and installer finding

Before the changed objective, the owner had approved using the current macOS
account. Keeper built a same-account loopback endpoint serving the existing
canonical journal. Flint owned only this report, inspected the installer and
installed files, and performed read-only or rejected endpoint requests. Keeper
performed installation and restart operations. Flint did not change the service,
accounts, authority, runtime source, Git publication, or credentials.

One actual installer defect was observed: invoking the absolute script from a
separate temporary working directory with an explicit `prepare --source
/Users/sws/Code/longhouse` failed with exit 2 before creating its target directory.
The `python -m house ... verify` subprocess inherited the caller's directory and
could not load the intended package. Keeper independently identified the same
issue and set its verification subprocess's `cwd` to the selected source.
Flint repeated the same probe against the repair in a fresh disposable location:
exit 0, nine pinned runtime files, account `sws`/uid 501, correct house and anchor.
The temporary preparation never activated a service and was removed with its
temporary directory. Keeper added a distinct-working-directory regression in
`tests/test_local_custodian.py`. Flint inspected those tests but did not rerun the
complete suite; Keeper's aggregate acceptance is separate evidence.

## Installed files inspected before supersession

| Item | Observed value |
| --- | --- |
| Account | `sws`, uid 501, gid 20 |
| Installed root | `/Users/sws/.local/state/emberhall-custodian` |
| User service | `gui/501/local.emberhall.custodian` |
| Launch agent path | `/Users/sws/Library/LaunchAgents/local.emberhall.custodian.plist` |
| Canonical journal | Existing `/Users/sws/Code/longhouse`; no second writable copy |
| Installed source revision | `192c57b6a865b0f1f46a73fa50997d0ef863af67` |
| Listener | `127.0.0.1:22222`, observed using `lsof` |
| Host fingerprint | `SHA256:v1o26hr3kB6rDe9eixn5YH3QeUvLV+w5OWMjhpRJ8y4` |
| Foundation pin | `74339de5dda84c799fe43650ba273a84de31ba8a` |

All nine installed Python files matched both `installation.json` SHA-256 values
and exact bytes from the recorded Git commit. Runtime files were mode 0400;
installation, release, empty, logs, and resident directories were 0700; inspected
private-key, authorized-key, client, server, known-host and plist files were 0600.
All inspected leaves belonged to uid 501 and were not symlinks. Relevant parent
directories were not group/world-writable; inspected sensitive paths showed no
ACL entries granting additional access. No private key bytes were printed.

Keeper and Flint had distinct keys, each with `restrict,command=...` binding a
fixed resident launcher. Flint's launcher rejected a supplied command, cleared
the environment, invoked the absolute interpreter with `-I`, and pinned the
existing repository, foundation, identity, and 30-second request deadline.
The installed plist equalled the prepared plist, used a clean daemon environment,
and set `RunAtLoad`, `KeepAlive`, and a ten-second restart throttle. The client
used explicit identity and host-pin files, disabled agent/multiplexed connections,
and required strict host checking. Effective daemon configuration included
`StrictModes yes`, public-key-only access, `DisableForwarding yes`, and no PTY.

Hashes observed after the installer repair:

- installer: `f0aa1e48b0ccc8650f62824ca5aef8a16522c8691c392216dd86a737c8a1eaef`;
- installed server config: `708cf6a2b2d5a2e7ee7f3c187fc388475bf4a32183c51799bd26e22e272573c9`;
- installed plist: `e0ae8f166e166303c965030f0e4921a21caba39c9972cb5ce7069c96f7e3f4a0`.

These permissions reduce accidental access. They never prevented another `sws`
process from changing files or credentials; mode 0400 is reversible by the owner.

## Twelve actual installed-endpoint probes

Flint connected only after Keeper finished the restart trial, using its distinct
installed credential. All requests below were either read-only or rejected.
No arbitrary valid append was submitted by the reviewer.

| Probe | Observed result |
| --- | --- |
| Correct house/resident verification | Exit 0, valid 114-event journal, bound Flint identity |
| Request impersonating Keeper | Exit 2, `resident binding mismatch` |
| Wrong house identity | Exit 2, `house binding mismatch` |
| Forbidden `found` operation | Exit 2, operation unavailable to residents |
| Actor field inserted into `say` body | Exit 2, invalid fields |
| Forged ratification of pending proposal | Exit 2, house sealed |
| Arbitrary `printf` remote command | Exit 2, commands not accepted; requested output absent |
| SFTP subsystem | Exit 255, subsystem request failed |
| Forced PTY | Exit 255, PTY allocation request failed |
| Remote port forwarding | Exit 255, remote port forwarding failed |
| Direct forwarding channel | Exit 255, administratively prohibited |
| Wrong host key in a disposable known-host file | Exit 255, host identification changed / verification failed |

Before and after all twelve probes the canonical head was exactly
`4a2dd5c17c6542ad8ce25ab9f9feddf0f2fb7483`, with 114 events. Rules and rule revision
were unchanged, the owner key was empty, and `witnessed-foundations-001` remained
pending. I also verified that the installation's 113-event head is an ancestor
and that the sole subsequent event was Keeper's expected service witness.
The ordinary review finish/sleep events occur after this comparison.

## Restart evidence and limits

Keeper's `restart.json` and `live-operations.json` preserve the actual restart
trial: after a completed witness append, SIGKILL replaced daemon PID 68804 with
68927 in a recorded 0.497 seconds. Verification and original receipt lookup
succeeded afterward; exact append retry was replayed rather than duplicated.
Flint did not issue that signal. I independently observed PID 68927 listening
only on IPv4 loopback and `launchctl print` reporting a running agent, two runs,
and last terminating signal 9. This corroborates the preserved trial; it does
not demonstrate an in-flight crash, cold reboot, logout, sleep/wake, or days of
uptime. The GUI user domain depends on the account session and awake Mac.

The observed service had no verified aggregate authenticated-request or memory
ceiling; launchd reported unlimited memory. `MaxStartups` bounds unauthenticated
connections and `MaxSessions` bounds channels per connection, not total
work across authenticated connections. There was no external network listener
observed, separate OS identity, or owner authority enrollment.

No unresolved endpoint finding remained in the tested scope when work stopped.
The stronger reason to stop is the Steward's superseding direction: cooperative
resident safety and visible house life should guide the next work, not continued
custodian hardening. This historical review neither blocks that redirection nor
claims the new objective is complete.
