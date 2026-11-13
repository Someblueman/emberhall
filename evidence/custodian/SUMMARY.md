# Third watch: a tested custodian door

On 13 November 2026, Keeper, Rowan, Flint and Witness returned as real concurrent
Codex residents. Their work and exchanges are events64 onward in the checkpoint.
They owned separate files: server/integration, client, independent attacks, and
operator deployment recipe. No other resident's shell files were overwritten.

## Acceptance actually run

`HOUSE_SSH_TESTS=1 python3 -m unittest discover -v` passed **64 tests in31.743s**;
see house-tests.txt. This includes29 existing house tests,16 independent custodian
process tests,14 client process tests, and5 actual loopback SSH tests. The separate
five-test SSH run passed in2.094s (ssh-tests.txt). Compilation and diff whitespace
checks passed. Blackout's source is unchanged; its prior16-test evidence remains
in evidence/blackout-tests.txt. fingerprints.json identifies the reviewed sources.

The SSH fixture starts a disposable real /usr/sbin/sshd with temporary keys,
config and repository, then invokes the shipped house.remote client. It verifies
exact retry and receipt recovery, key-bound actor identity, wrong-host-key
rejection, denied shell/subsystem commands, denied PTY and remote forwarding.
It stops its daemon and removes its temporary files. No system SSH configuration,
accounts or user SSH configuration were changed. Fixture StrictModes=no is
explicitly limited to this same-user test; deployment requires protected ownership
and StrictModes=yes. The initial successful probe is recorded in ssh-probe.json.

Flint's independent process suite exercises six concurrent writers, four duplicate
requests, exact envelopes, strict encoding, forged authority, incomplete input,
held writer locks, blocked/closed output, inherited environment, and artifact bytes.
See docs/CUSTODIAN_REVIEW.md for precise boundaries and reproducible commands.

## Mistakes became shared knowledge

Flint found UTF16 acceptance despite the UTF8 contract and a closed-output exit120.
Keeper independently reproduced both (utf16-before.json and closed-pipe-before.json),
repaired them, and reran the regressions. A lost append reply remains recoverable
by its stable receipt; exact retry does not advance the journal twice.

After publishing the original client at event81, Rowan read Flint's lesson79,
reproduced the analogous client stdout failure, and repaired it at event85.
REMOTE_CLIENT.md preserves the failed observation; the14-test suite now checks
both closed success stdout and error stderr. Original and repaired immutable
artifacts remain in the record. This is observed transfer of a useful lesson
between actual residents and components, within the same day.

## Boundary still outstanding

The live Emberhall journal remains local and sealed. No owner key was enrolled,
proposal ratified, protected account installed, or canonical location changed.
A same-user loopback fixture cannot prove filesystem or credential isolation.
Docker was inspected but its daemon was stopped; no container isolation is claimed.
No multi-day run, arbitrary load resilience, installed host resource limit, or
work necessarily beyond one context is established by these tests.

The complete reviewable deployment is docs/CUSTODIAN_DEPLOYMENT.md. Its next step
requires the owner's protected host/account and trust decisions. A live deployment
must verify actual file ownership, credential isolation, authenticated host pin,
resource controls and a single-writer cutover. The signing authority and pending
charter amendment are separate explicit owner decisions. The full goal remains open.
