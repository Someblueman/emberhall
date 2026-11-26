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
they do not prove stationarity. A clean-baseline freeze requires independent
scientific review, sufficient precision, and no unresolved failure.

Held-out correlated inputs reserve community seeds 100–123 and input seeds
400000 onward. Do not inspect these while choosing resolution, duration,
segments, correlation strengths or comparisons. The clean model, estimator,
practical margins and analysis must be frozen and reviewed first; the
correlated-input intervention itself still needs its own written protocol.

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
python3 projects/when-nutrients-arrive-together/convergence.py --output /tmp/nutrient-convergence
```

Use a new directory. Configuration is written before simulation; each completed
realization is appended immediately, failures retained, and fine trajectories
saved for analysis. The final report is written only after all attempts.

For a bounded building stretch append `--max-attempts 2`. Continue with the
same arguments plus `--resume`; this rejects configuration changes and skips
only completed successes or recorded failures. A process interruption may
require repeating its unfinished realization; it is not a biological failure.
`complete: false` in the report means the planned experiment is unfinished.
Never interpret its interim intervals as the completed twelve-community result.
