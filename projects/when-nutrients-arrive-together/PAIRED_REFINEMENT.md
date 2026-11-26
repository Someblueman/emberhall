# Replicated nonlinear mesh and record-length diagnostic

Mallow, 26 November 2026. Written before the new solves. The prior clean
reference's failed length and precision gates remain failed. This adaptive
development study addresses NEXT.md's broader nonlinear design; it does not
freeze a clean baseline, replace the accepted protocol, or use held-out seeds.

Use all twelve development communities 4–15 and two new independent input
paths each. Input seed is 80000 + 100*community + drive (drive 0 or 1).
Generate stationary independent OU supply on mesh 1/16, then conditionally
refine each interval at its midpoint with bridge seed 90000 + 100*community
+ drive. The bridge preserves every coarse endpoint exactly and has the
joint OU law checked in test_ou_bridge.py. The two meshes are paired
approximations to one path, never independent replicates. They do not
certify a continuum bound. No correlated inputs are generated.

Start every consumer and resource amount at one, as in the accepted
reconstruction. Supply means, private resources and amplitude remain the
explicit reconstruction choices in MODEL.md and SOURCE_AUDIT.md. No new
published-figure replication claim follows. Simulate 8704 units, discard
512, and retain 8192 unit-spaced samples. Both meshes use maximum step
1/32 and relative tolerance 1e-9 (absolute tolerance 1e-11), isolating
forcing interpolation while keeping solver settings equal. On preselected
community 4, drive 0, repeat both meshes at maximum step 1/64, relative
tolerance 1e-11 and absolute tolerance 1e-13. This is a representative
solver control, not an error bound on the other paths.

For each metric, report overlap Spearman, pair-label AUC and single-linkage
guild AUC separately. Segment 30 is primary; segments 16 and 60 are
diagnostics. Compare coarse with fine over the entire retained window;
compare first 4096 with all 8192 samples on the fine mesh and report the
second half separately. Report half-mean shifts and variance ratios as
descriptive stationarity diagnostics, not a stationarity proof. Preserve
nonpositive supply, resource or extinction failures without replacement.

Average the two drives within each community before marginal Student-t
intervals. Also report untruncated distribution-free marginal Hoeffding
radii (score ranges two for rank, one for AUC; difference ranges twice
these). Twelve independent communities cannot provide distribution-free
precision of .10: the marginal radii for means are about .784 and .392.
No nominal population-precision success is possible by pretending 24
paths are 24 communities. Missing or failed drives exclude the entire
community from conditional means, with failures retained. The signed mean
of paired changes can hide cancellation, so retain the worst individual
absolute change and community counts exceeding the original forcing
margins (.05 rank, .03 AUC) and length margins (.10 rank, .05 AUC).
Those are descriptive comparisons, not new acceptance gates. No multiple
comparison or simultaneous-coverage claim is made.

The computational budget is 48 primary solves and two representative
solver checks. Run two disjoint six-community partitions in local worker
processes, using only already installed NumPy/SciPy. A wall-time stop
leaves an explicitly incomplete batch with each completed receipt retained;
it cannot establish a population result. Exact settings, versions and
source hashes are frozen before solving, and all successful trajectories
are hash-bound outside Git. Only the small protocol, summary and a compact
per-realization score table belong in the repository.

```
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --start 4 --stop 10
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --start 10 --stop 16
OPENBLAS_NUM_THREADS=1 python3 projects/when-nutrients-arrive-together/paired_refinement.py --output /tmp/nutrients-paired-refinement --report-only
```

Initialize the shared protocol with `--report-only` before starting both
partitions. Each owns disjoint receipts and arrays. Resume retains success
and failure receipts only under matching protocol and seed identities.
An incomplete summary is a progress report, never completed evidence.
Independent milestone scientific review remains outstanding.

After the first paired solve took about 324 seconds, two additional local
workers took communities 8–9 and 14–15, far ahead of the original ascending
workers. The latter reuse the completed receipts when they reach those
communities. This changes computational scheduling only, not the frozen
seed list, mesh, duration or analysis. No realization is an extra replicate.
