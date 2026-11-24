#!/usr/bin/env python3
"""Small independent-integration audit; no scientific held-out seeds."""
import json
import random

from baseline import Design, Observation, simulate
from continuous import ContinuousInference
from reference import Reference


def audit():
    design = Design()
    steps = (1, .5, .25, .125, .0625)
    models = [ContinuousInference(design, step) for step in steps]
    observations = [Observation(design.focal_ages, 16, (k,) * len(design.focal_ages))
                    for k in (0, 12, 16)]
    rng = random.Random(581024)
    for _ in range(9):
        observations.append(simulate(design, rng.uniform(-100, 100), rng.choice(design.mixing_times), rng))
    errors = [0.0] * len(models)
    reference_difference = 0.0
    largest_evaluations = 0
    for obs in observations:
        densities = [model.fit(obs) for model in models]
        reference = Reference(design, obs, tolerance=1e-10)
        looser = Reference(design, obs, tolerance=1e-8)
        probes = sorted(set(range(-100, 101, 10))
                        | {densities[-1].quantile(p) for p in (.05, .5, .95)})
        for x in probes:
            actual = reference.cdf(x)
            reference_difference = max(reference_difference, abs(actual - looser.cdf(x)))
            for i, density in enumerate(densities):
                errors[i] = max(errors[i], abs(actual - density.cdf(x)))
        largest_evaluations = max(largest_evaluations, reference.evaluations, looser.evaluations)
    return {"observations": len(observations), "development_seed": 581024,
            "steps": steps, "max_probe_cdf_errors": errors,
            "max_reference_tolerance_difference": reference_difference,
            "largest_integration_evaluation_count": largest_evaluations,
            "warning": "Finite audit probes and Simpson residuals do not certify all-data integration error."}


if __name__ == '__main__':
    print(json.dumps(audit(), indent=2, allow_nan=False))
