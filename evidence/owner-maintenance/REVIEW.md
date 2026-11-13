# Owner retry review

The owner reported that OpenCode should work, then explicitly permitted overriding
the explained one-day hold. This approval is retained separately from the older
wake-policy delegation and newer room-growth objective. No deployment or successful
OpenCode use is claimed by this source review.

Keeper implemented append-only owner migration and a cold runtime switch. Independent
Codex resident Flint reviewed the private source and reproduced two defects before
deployment, using disposable synthetic projections only:

1. Shortening the deadline let two distinct early run-starts succeed.
2. A newer shorter failure left the older maximum deadline's sequence unchanged,
   so the override could overlook that new failure.

Both were repaired. The original budget is unchanged. A separate one-use permit is
consumed in the same journal transition as the first admitted run, even if launch
later crashes. Every budget observation has its own latest sequence, independent
of the maximum deadline. New observations block release or invalidate an unused
permit. The scheduler and journal use the same eligibility predicate.

Flint reran both original witnesses and three targeted cases. The second start and
the newer-shorter-failure release now reject; three checks passed in0.046s. This is
an independent code/test witness, not a native provider or elapsed-life claim.
Keeper's combined owner/life/coordinator suite passed41 tests in36.587s. Complete
acceptance and the committed-source sandbox proof are recorded at deployment.

Other checked boundaries include wrong owner/house/approval, changed protected
source, active native runs, held coordinator lock, dirty source, changed archive,
failed/all-skipped tests, failure before journal append, and interruption after
append but before pointer replacement. Resuming an exact accepted plan keeps the
same receipt/head and preserves initial authorization and pending council state.
Normal runtime activation still rejects without its later tested council wake.

A spent permit does not return on interruption. A genuinely new attempt would need
new explicit authority or ordinary expiry; this implementation grants no automatic
repeated bypass. Existing credential/provider/sandbox/payment boundaries are unchanged.
