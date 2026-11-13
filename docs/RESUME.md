# The next watch

Welcome back to Emberhall. Read AGENTS.md, then the verified record—not a guess
about what the previous resident intended.

House identity: `9c5a77af-0f1a-4995-8e52-e91c0d814569`.
Foundation anchor: `74339de5dda84c799fe43650ba273a84de31ba8a`.
The anchor is a local integrity reference, not an external security boundary.

The founding implementation and independent Blackout Kit are complete. The owner
authorized unsigned local commits for this task; see `docs/DELIVERY.md` and
`evidence/publication.json` for the publication and recovery receipts. Five real
residents contributed; tests passed; all residents left return notes. The exact
checkpoint head/event count is in `evidence/checkpoint.json`. Root was the founding
integrator. No code ownership from that session remains active after its completed
claims. Current assignments and open work always come from `house status`.

## If the house refs are present

```
python3 -m house verify
python3 -m house status
```

A returning resident uses `wake --as ID` and `read --as ID`. A new resident arrives
with a unique ID. If `read` says `has_more`, continue with `--after THROUGH`.
Never advance a sleep cursor beyond what you read. A recovered claim receipt
proves past acceptance, not current ownership: check the current lease before work.

## If this is a fresh source clone

The source checkout contains the checkpoint bundle. Restore it exactly:

```
python3 -m house restore evidence/house-publication.bundle --expect-anchor 74339de5dda84c799fe43650ba273a84de31ba8a
python3 -m house verify
```

Restoration refuses to overwrite an existing house, validates the entire chain
before publishing refs, and preserves original commit identities. Do not use
`found` to repair this house. Never merge `house-ledger` into source. The source
branch and journal branch deliberately have separate histories.

If a local house is newer than the bundle, do not restore over it. Inspect its
valid head and make a new bundle with a new filename. Keep the old receipt until
recovery is verified. Before any source-only clone or backup, remember that the
custom foundation ref is not automatically included. A checkpoint only covers
the exact head named in its receipt.

## Useful work is waiting

`next-watch-scale` is now completed. The second watch measured and repaired
quadratic replay copying: 10,000-event read/append fell from about 13 seconds to
0.22/0.25 seconds, with full validation intact. The repair has 29 passing house
tests and independently verified identical state at every live prefix. Read
`evidence/scale-watch/SUMMARY.md` and REVIEW.md before changing projection ownership.

The owner explicitly authorized unsigned local source commits for this task.
Use only a per-command signing override; do not change persistent Git settings.
Stronger custodian isolation and authority enrollment remain explicit owner
decisions. Source publication does not ratify the pending charter proposal.

The house has evidence-backed lessons about filesystem inputs, authority replay,
and daughter seeding. Read their evidence and scope before applying them.
Imported advice is unreviewed locally; a seed is not certification.

## Unresolved boundary

Governance remains sealed. `witnessed-foundations-001` is pending, and the founding
charter is unchanged. No resident signing key exists. The owner must explicitly
approve an authority migration and choose a protected custodian before stronger
hostile-resident enforcement can be claimed. See `docs/OWNER_DECISION.md`.

If verification fails, stop house mutations, preserve the refs and files, and
inspect the precise failure. Do not reset away evidence or delete unfamiliar Git
locks. A failing disk cannot be repaired by inventing data.

Read `docs/EVIDENCE.md` for exactly what was proved and what was not. No push,
automation, multi-day operation, or independent daughter society is claimed.
