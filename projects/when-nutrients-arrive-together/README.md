# When Nutrients Arrive Together

A controlled consumer–resource study of diet inference under shared nutrient
delivery. Current work is the **independent-input pilot**, not a completed
correlated-input study or a replication of a published figure.

From the repository root, with the already installed NumPy and SciPy:

```
python3 projects/when-nutrients-arrive-together/reference.py --output /tmp/nutrient-reference
```

This regenerates four seeded communities, their supply and abundance arrays,
per-community metrics at three spectral resolutions, and `report.json` with
uncertainty, solver/forcing convergence, versions and failures. Runtime is a few minutes on the development machine. Outputs are generated outside the source
checkout; binary arrays are not committed. To test:

```
cd projects/when-nutrients-arrive-together
python3 -m unittest -q
```

Read [MODEL.md](MODEL.md) before interpreting a score. It distinguishes the
source equations from our explicit supply choices, lists every approximation,
and names the remaining scientific work. [PILOT.md](PILOT.md) records the first
run. No web interface, new dependency, or external service is needed.

For longer records or finer forcing, use `--duration`, `--burn`,
`--drive-spacing` and `--seeds`. At least 240 retained observations are
required for all spectral checks. Existing outputs are replaced, so use a new
output directory to preserve an earlier experiment.

For paired forcing and record-length convergence with a fixed community/drive
schedule and resumable runs, see [CONVERGENCE.md](CONVERGENCE.md). This remains
a diagnostic until all planned realizations and independent review are complete.
