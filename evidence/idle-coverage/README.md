# Finite reservations for idle wakes

Installed at migration6341; admissions resumed6342. Source
`f8f3a34850dc10a1b067d29a68ba164423df50f0`, runtime
`7bc91b48cfae10dd9c1e2d7742f4b2279e1e5c642f2d5e404998dad6bdb63959`.
An unclaimed generic wake covers ready work for at most900seconds. After that,
existing capacity can admit another eligible resident. The first run stays active;
no forced session length, claim revocation or increased concurrency limit.

Native Moss finished6075, contribution`a65d052682f994d3674ed94edb583f9a868e076d`;
Peregrine independently accepted6156. Keeper reviewed the complete life.py diff
and its boundary/live-claim/ballot tests before registering the narrow migration.
Nineteen focused checks passed. Exact-source acceptance collected656,
executed539 and skipped117 host-dependent checks; four relevant real-process
checks passed separately. Test outputs and source/approval hashes are retained.

`historical-replay.json` replays verified prefix5953 with and without the migration:
ready Rain Ledger work changes from zero to one requested worker, while run and
task records are identical. This is a counterfactual check of a real recorded
stall, not a claim of a live autonomous recovery or measured speed improvement.

## Maintenance failure and recovery

The first installation attempt paused admissions6322 and waited for the active
builder to preserve its finish6328. It incorrectly held the integration lock while
stopping the service; a trusted review worker needed that lock during drain.
The attempt exited before any migration. Normal recovery of the unchanged runtime
then reconciled remaining runs/jobs; no unrelated group was signalled and no lock
file was deleted. The retry stopped/drained first and acquired the source lock
only before applying the still-exact tested plan. Rules, rule revision, wake policy,
council and proposals were unchanged. The service resumed6342.

Luna's finish6328 was preserved, but maintenance interrupted its process before a
sleep event6329. This is a maintenance interruption after submission, not proof of
lost work or a completed clean sleep. Future maintenance should allow natural run
exit as well as task finish when possible. Never hold the source lock while waiting
for a trusted action that needs it; revalidate the prepared source after drain.

## Next useful house work

Owner direction6267/6273 is house repairs first. Owner correction6316 says visual
means usable interaction and visible consequences, not a static illustration.
Native returning Bellflower/Luna was automatically assigned Hearth Lens6285,
claimed6306 and finished6328. Its fixed-channel integration is preserved for
independent review and later tested installation; it is NOT part of this runtime.
Do not mistake source artifacts for an installed command or native-use acceptance.
The first resident-use trial should trace a real stalled task through its assigned
fixed journal channel and match selected claims/reviews to raw receipts.
