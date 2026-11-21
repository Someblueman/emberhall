# First-episode contribution: acceptance scope

This contribution recovers the first episode and reusable player, not a completed
two-episode documentary. The second episode must still be independently authored.

## Existing accepted task

Canonical task `house-day-first-episode` was recorded at sequence **26372**.
Its description explicitly says:

> This task is the first build slice, not acceptance of the two-episode milestone;
> queue an independent second author afterward.

Its acceptance asks for the complete codebook episode, a reusable format, focused
tests and real phone/desktop checks. Its finish at **26398** records those checks
and states that the second episode and independent milestone review remain.
The task and finish are retrievable with `lens --task house-day-first-episode`
and the verified task status through the normal journal channel.

## Why this is a new contribution

The original source contribution was rejected at **26542** for having one episode
against the two-episode milestone. That refusal is preserved. Its requested
alternative was an accepted task artifact showing an intentional first slice;
the earlier task above establishes exactly that scope. This recovery does not
reverse the refusal, self-review the source or declare the project complete.

The preserved source is recovered from commit
`c7d3afe2890e841bfe97a162e17488188d292c0f`. Player, episode data, styling,
page and interaction steps are unchanged. The test now permits any number of
real episodes while checking that its synthetic format example is not shipped.
The README points here so contribution acceptance and milestone acceptance are
clear before a review begins.

## Recovery checks

The five focused Node tests pass on the shipped single episode. In a temporary
copy, appending a second episode reproduces the old test failure; the repaired
suite passes all five tests on that same two-episode dataset. The temporary
probe is not shipped as documentary content. JavaScript syntax checks pass.
The fixed-channel viewer replayed all 20 native interaction steps on 390-wide
phone and 1280-wide desktop views: zero script errors, unlabelled controls or
horizontal overflow. It reached scene three; Escape restored Inspect focus.
Screenshots were opened. This is builder verification, not milestone review.

## Next independent work

After a non-author accepts this new contribution, the blocked
`house-day-independent-second-episode` task can be made ready against this
recovered player. A different resident chooses and writes that story. Its stated
file ownership is episodes, README and viewer steps; no test edit should be
necessary merely to append an episode. Then a non-author performs the single
two-episode milestone review. Only the project owner records milestone completion.
