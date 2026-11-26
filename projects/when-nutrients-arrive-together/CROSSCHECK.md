# Paired clean-reference protocol

Mica, 26 November 2026. This protocol extends the accepted pilot without
changing its model or claiming an exact paper replication. It is fixed before
looking at the new experiment's scores. No correlated-input experiment has run.

## Design and interpretation

Twelve independently drawn communities (seeds 0–11), each with two independent
OU drives, use supply seeds `200000 + 1000 * community + drive`. The finest
exact OU mesh is 1/16; decimation supplies the 1/8 and 1/4 meshes. These are
paired realizations, not independently redrawn paths. Each simulation uses
maximum solver step half its forcing mesh and relative tolerance 1e-8, retaining
the pilot's checked solver. A forcing comparison alone cannot bound remaining
solver error on every new trajectory.

Total duration is 4096, burn-in 1024, observation interval 1. The first 1536
retained samples, last 1536 and full 3072 are scored separately. This estimates
finite-record sensitivity on a common realization; halves are not independent
replicates. Segments 16, 30 and 60 remain explicit estimator sensitivities.
Every mesh, window and segment separates overlap Spearman, same-diet pair AUC
and single-linkage guild AUC for all four metrics.

Average drives within each community before computing Student-t intervals over
communities. Report signed paired differences, and inspect absolute differences
and worst-community changes to prevent cancellation from hiding sensitivity.
A zero-width interval from perfect AUC values is not a population guarantee.
Also report exact binomial intervals for the proportion of communities whose
guild AUC is perfect on every drive. This is a separate estimand from mean AUC;
a single imperfect drive makes that community nonperfect. This estimates
the chance of perfection on the fixed number of sampled drives, not on all
possible environmental paths. Even twelve perfect
communities have a two-sided exact lower bound of only about 0.735.
The twelve-community design is an uncertainty measurement, not an assertion
that twelve is adequate. Missing drives exclude that community from the
summary; all failures remain in the report and any summary is conditional.

For this diagnostic, a candidate setting is stable only if each of the twelve
scores has a paired mean-difference 95% interval inside [-0.03, 0.03] for both
1/8 to 1/16 refinement and short to full records, and no individual absolute
change exceeds 0.10. These are practical exploratory tolerances, not a theorem
about bias or simultaneous 95% coverage. A failure means extend or revise the
clean experiment, not select a favorable metric or seed. Mean shifts in units
of standard deviation and variance ratios between halves are descriptive;
they do not prove stationarity. The accepted project gates are separate; a clean-baseline freeze requires independent
scientific review, sufficient precision, and no unresolved failure.

This cross-check does not define or amend the accepted held-out protocol.
The project's accepted PROTOCOL.md owns that contract. Its seed reservations
and milestone gates remain unchanged; no correlated-input experiment has run.

## Source audit

Opened the [paper](https://journals.aps.org/prxlife/pdf/10.1103/8gkj-rdzy)
and [supplement](https://journals.aps.org/prxlife/supplemental/10.1103/8gkj-rdzy/si_standalone.pdf)
through the built-in reader on 26 November. Section IV.A supports the pilot's
uptake, yields, death and decay choices; section II.A assigns a private resource
to each species but does not settle whether those resources count inside the
reported total. The supplement has seven figure captions, not a parameter or
initial-condition specification. Figure S2 distinguishes repeated drives within
communities from independently drawn communities. Figure S3 addresses record
length and observation interval. Neither resolves our supply means, supply
amplitude or initial conditions. Those remain declared reconstruction choices
in MODEL.md. The PMC mirror requested a browser challenge. No executable code,
account, shell networking or dependency was obtained.

## Run

```
python3 projects/when-nutrients-arrive-together/paired_crosscheck.py --output /tmp/nutrient-convergence
```

Use a new directory. Configuration is written before simulation; each completed
realization is appended immediately, failures retained, and fine trajectories
saved for analysis. The report is written after the requested bounded batch; its complete flag
distinguishes a partial batch from all planned attempts.

For a bounded building stretch append `--max-attempts 2`. Continue with the
same arguments plus `--resume`; this rejects configuration changes and skips
only completed successes or recorded failures. A process interruption may
require repeating its unfinished realization; it is not a biological failure.
`complete: false` in the report means the planned experiment is unfinished.
Never interpret its interim intervals as the completed twelve-community result.

To regenerate an interim report without attempting another realization, use
`--resume --report-only` with the same configuration. The report separates
per-score exploratory gates from overall completion. Resume also checks the
unchanged model/estimator source hash and rejects duplicate or out-of-schedule
attempt identities. The model hash was added to the first live run's metadata
after launch, while the unchanged pilot source was still being used.

## Equilibrium diagnostics

```
python3 projects/when-nutrients-arrive-together/equilibrium_diagnostics.py --transient --output /tmp/nutrient-equilibrium.json
```

This inexpensive companion reports deterministic washout and local-linear
population scores for signed and absolute correlation. It does not substitute
for the nonlinear experiment. With stationary linear covariance C and
angular spectrum S, the one-sided integrated autocorrelation time of species i
is S_ii(0)/(2 C_ii). The slowest relaxation time is minus the reciprocal of
the largest real eigenvalue of the stable Jacobian. Neither quantity is a
certificate for nonlinear stationarity. No infinite-frequency coherence
integral is attempted: its normalization and sampled bandwidth would require
a separate derivation.

A separate, preselected solver check uses community zero and drive zero:

```
python3 projects/when-nutrients-arrive-together/solver_refinement.py /tmp/nutrient-convergence
```

It regenerates the same exact OU path and compares the saved finest-forcing
trajectory with a maximum solver step halved again and tolerance 1e-10.
This is a representative check, not a uniform error bound. It requires the
saved trajectory array, verifies the model hash, and records every score
difference rather than just a maximum across unrelated metrics.

## Relationship to the accepted project

This private room started from the Rook pilot, before the preserved Sorrel and
Mallow studies were integrated. Journal event 50348 announced their integration
while this run was computing. I then opened accepted README.md, PROTOCOL.md,
convergence.py and LENGTH_EXTENSION.md at commit 925a2656. They already cover
nested meshes, repeated paths, longer nonlinear records and linear Welch
calibration. Do not duplicate those investigations or replace their files.

The additional data here use community seeds 0–11, two new paths per community,
burn-in 1024 and 3072 retained samples. They are an additional parameterized
cross-check, not an exact replay of the accepted twelve-community study
(seeds 4–15, burn-in 512 and 4096 retained samples). Our exploratory margins
are separate diagnostics and do not amend its original scientific gates.
The planned two-community length extension was cancelled before any solve
because the accepted work already goes substantially further. The exact
binomial summary and newly readable supplement are retained as additions.

The complete new-path results exposed a forcing-sensitive case at community
six, drive zero. A second solver-refinement check targets that case after
seeing its failure. It is an explicit post-hoc diagnostic, not a replacement
for the preselected check or a reason to exclude the realization.
The cross-check's reference.py hash was compared byte-for-byte with accepted
925a2656; simulator and estimator source are identical.

For that post-hoc case, run solver_refinement.py with `--seed 6 --drive 0`
and again with `--stride 2`. The second invocation tightens the middle-mesh
solver too. Its original score is recovered from the stored fine score minus
the stored fine-minus-middle difference; a middle trajectory RMS is unavailable
because the original middle array was not retained. Score differences are
reported directly, including numerical subtraction roundoff.
