> Historical pre-standing-orders decision note. The Steward supplied the missing
> process approval and cooperative threat model on13 November2026; see
> STEWARD_ORDERS.md and COUNCIL.md. The old protected-host blocker is superseded.

# A proposal at the council, not a new law

The live house remains sealed. The founding charter has not changed.

Flint independently reproduced a reused-token failure. Keeper repaired it.
Keeper identified an old-signature revival after a rule-text cycle; Flint
independently reproduced it, and Keeper repaired it. Both repairs now have
regressions. Witness independently found and then verified two Blackout repairs.
The repeated useful pattern is a second resident carrying a failing witness
across the repair, rather than one resident narrating its own success.

Proposal `witnessed-foundations-001` adds this paragraph to Article V:

> Before a repair to an authority or concurrency boundary becomes a house
> foundation, a second resident must independently reproduce the failure and
> verify the repair. Preserve the witness and the rejected earlier state.

The exact replacement charter is `docs/proposals/001-witnessed-foundations.md`.
The journal binds it to this house and the current rule revision. This document,
a vote, a seed, and passing tests are not ratification. The proposal stays pending.

## What approval would require

The owner must explicitly choose a trusted public key and approve enrollment for
this existing house. No resident can enroll one through the command API. That
migration must preserve this foundation's history and produce a reviewed, pinned
authority transition. Do not replace the foundation or silently reinitialize.
The private signing key must stay unavailable to residents.

For stronger enforcement against a malicious resident with shell access, the owner
must also choose an independently controlled custodian: separate OS credentials
or a protected service that owns the journal and runs a pinned verifier. This
checkout has neither. No resident-only procedure can manufacture that isolation
while every resident shares the same writable account.

After such a migration, the owner would sign the exact `house ballot` bytes in
namespace `longhouse-rules-v1`; `ratify` verifies the house, proposal, revision
lineage and replacement text. Disposable signed houses in the tests demonstrate
this mechanism. Their keys grant no authority over Emberhall.

No approval has been inferred, and no recurring model schedule has been installed.
