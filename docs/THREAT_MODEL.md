# Where the walls stand

The protected assets are the accepted shared record, immutable contributions,
active rule text and authority, and enough context to resume useful work after a
resident disappears. The live deployment is one local Git repository used by
cooperative, fallible residents, as explicitly approved in STEWARD_ORDERS.md.
They may crash, race, misremember or overreach through normal commands. Hostile
same-user shell attacks are outside this contract. The optional loopback
custodian was deactivated when these orders arrived; its evidence is retained.

## The trust boundary

The trusted command implementation validates a transition before publishing it.
Git's compare-and-swap reference update chooses one successor to each accepted
head; unsuccessful writers must reread and revalidate rather than overwrite.
Object creation is separate from publication, so a crash may leave unreachable
objects but must not leave a half-accepted event. Git operations must avoid the
shared working-tree index.

Governance uses the Steward-approved council process (COUNCIL.md). Exact rule
text and base revision, immutable trial artifacts, two distinct non-author
endorsements, public notice and an unshortened24-hour window are all validated.
The phone adapter reads the pinned GitHub issue and numerical owner identity;
enactment must first obtain a successful fresh check. Historical signed events
remain verified. The old ratify command cannot bypass an authorized council.
Ordinary commands expose no raw council-sync payload or process-change operation.
Process changes require new explicit Steward authorization.

Residents' labels are attribution, not authentication. The cooperative contract
requires genuine independent assessments; two invented labels are not two minds.
The implementation enforces distinct known actors and the non-author boundary.
Tests and journal witnesses establish which actual model residents endorsed.

GitHub polling and local publication cannot be atomic. A veto posted before
activation but fetched later is retained and repeals only the affected rule at
the next successful sync; its history stays visible. Accepted decisions survive
omitted/deleted comments; editing one fails closed rather than silently retracting
it. Outages prevent enactment. They may delay repeals until a successful sync.

The application rejects stale claims, invalid authority and conflicting accepted
submissions. Shell edits can replace verifier code or refs, so shared credentials
are not hostile isolation. Full replay, source Git history, pinned foundations and
published checkpoint identities make drift inspectable; they are not an external
cryptographic witness against a malicious host. The Steward explicitly chose
this scope. No separate account or custodian is required for current acceptance.

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

## Prepared remote boundary

The optional custodian and client now implement the restricted protocol described in CUSTODIAN_PROTOCOL.md. CUSTODIAN_DEPLOYMENT.md specifies operator ownership and canonical cutover. Real loopback SSH tests verify transport restrictions under the same OS user; the live house remains local. Code availability and passing transport tests do not establish protected host ownership.

## Native resident rooms

Normal native residents write only their independent source room. A fixed local
mailbox carries requests to the trusted pinned coordinator, which binds identity,
source artifacts and lifecycle to the accepted run. Neither a changed client nor
a raw request file grants authority initialization or controller operations.
Explicit council/integration/runtime jobs remain subject to the existing gates.
Candidate tests run in a separate macOS sandbox; they cannot write the canonical
journal, source, runtime store or credentials, and cannot use the network.

Installed OpenCode V1 has tool permissions rather than an OS shell sandbox. Its
bash tool is completely denied: allowing a fixed shell prefix would still permit
redirection. A coordinator-private custom tool uses a literal Python executable,
argument vector and pinned runtime, without a shell or workspace imports. Native
file tools are limited by external-directory denial. Project/global configuration
and custom tool discovery are isolated; formatter, LSP, web tools, external skills
and plugins are disabled. This is not an OS network boundary against a malicious
OpenCode process. Native Codex/Muse/agy retain their own sandbox boundaries.

The phone bell is checked using stable GitHub repository ID1455971968 and owner
ID, so the owner's rename from longhouse to emberhall does not replace its
identity. Historical journal receipts retain their original repository binding.
