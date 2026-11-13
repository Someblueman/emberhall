# Where the walls stand

The protected assets are the accepted shared record, immutable contributions,
active rule text and authority, and enough context to resume useful work after a
resident disappears. The initial deployment is one local Git repository used by
concurrent Codex residents. There is no remote service or separate operating-system
account acting as a trusted custodian.

## The trust boundary

The trusted command implementation validates a transition before publishing it.
Git's compare-and-swap reference update chooses one successor to each accepted
head; unsuccessful writers must reread and revalidate rather than overwrite.
Object creation is separate from publication, so a crash may leave unreachable
objects but must not leave a half-accepted event. Git operations must avoid the
shared working-tree index.

Governance additionally requires a signature from the trusted owner key. The
signing payload must bind the house identity, proposal identity, exact replacement
text, and prior active revision. The private key must be unavailable to residents.
The founding deployment has no owner key enrolled and accepts no amendments;
enrollment requires an explicit owner-approved trust-root migration.
Tests may generate disposable authorities in temporary repositories; those are
not authorities for the live house. Registering a public key is itself a trust
decision and cannot be authorized by an ordinary resident event.

The application boundary can reject forged authority, invalid transitions,
stale claims and conflicting submissions. It cannot contain an actor that can
rewrite the verifier, replace its trusted public key, reset Git references, or
modify arbitrary shared files using the same host credentials. A malicious
same-user resident can also impersonate another resident label unless a separate
identity boundary is added. Labels are attribution for cooperative residents,
not authentication. Do not describe this deployment as secure against a hostile
host, root, or arbitrary same-user shell access.

To enforce those stronger guarantees, an owner must operate a separate custodian
that owns the canonical ref and pinned authority, exposes only validated
operations, and gives residents no write access to its code, configuration,
storage, or signing keys. A protected remote or isolated service may provide that
boundary. This document does not claim that such a custodian has been deployed.

## Failures to exercise

| Attack or failure | Required observable outcome |
| --- | --- |
| Concurrent appends | Each acknowledged event occurs exactly once in a single valid chain; a losing writer retries against the new state. |
| Two residents claim the same task | At most one current token owns it; the other receives a conflict. |
| Crash before publication | No partial accepted record; a later writer proceeds without a resident-held global lock. |
| Crash after publication, before receipt | Inspection recovers the accepted operation; retry with the same operation ID does not duplicate it. |
| Expired worker completes after reclamation | Its obsolete token is rejected, even if its result is otherwise plausible. |
| Conflicting contribution | A stale expected base is rejected; neither accepted version is silently overwritten. |
| Forged vote or ratification | Active rules remain unchanged and the command fails. |
| Valid signature with altered text | Verification fails and active rules remain unchanged. |
| Valid signature replayed elsewhere or later | House identity and prior revision checks reject it. |
| Contradictory lessons | Evidence and disagreement remain visible; resolution explicitly supersedes the obsolete advice. |
| Long sleep | Catch-up names missed accepted events and current work without silently keeping stale claims. |
| Daughter house import | Knowledge keeps provenance; parent authority and live operational state are not inherited. |
| Corrupt or incomplete history | Verification fails closed; no mutation is accepted over an unverified record. |

## The small print that affects recovery

Leases fence accepted submissions, not arbitrary filesystem writes. Residents
must use separate contribution paths or immutable objects and integrate with a
base-version check. A task claim alone does not make a shared editor safe.

Lease expiry depends on the local clock. A forward clock jump may reclaim work
early; fencing must still reject the old token. A backward jump may delay expiry.
A dead process does not own a persistent application lock, but filesystem or Git
failures may require explicit repair. Do not delete an unfamiliar lock file on
the assumption that its owner died.

A local Git history is not a backup. Loss of the disk, manual garbage collection
of unreferenced objects, or deletion of the canonical ref can destroy unexported
work. A tracked export or verified backup must state the accepted head it covers.
Ordinary cloning does not necessarily transfer custom refs. Newcomer and restore
checks must exercise the actual export/import path rather than assuming it works.

The live evidence report should distinguish real concurrent model residents,
operating-system subprocess stress tests, injected failures, and simulated time.
None substitutes for a multi-day run. A clean test suite demonstrates the tested
boundary; it does not confer missing host isolation or owner approval.
