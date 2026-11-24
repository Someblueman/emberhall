"""Tests for monotone age-depth chronologies and shared calibration ensembles."""

from __future__ import annotations

import json
import math
import random
import statistics
import unittest

from chronology_model import (
    ArchivePriorSpec,
    CalibrationPriorSpec,
    PairedChronologySpec,
    PublicChronologyObservation,
    analytic_gaussian_limit_posterior,
    empirical_pit,
    fit_unconstrained_nonmonotone,
    importance_sample_small_case,
    infer_joint_chronology,
    ks_uniform_statistic,
    run_calibration_and_failure_benchmark,
    shuffle_paired_ensemble,
    simulate_gamma_increment_path,
    simulate_paired_chronology,
)


class TestMonotoneGammaProcess(unittest.TestCase):
    def test_strict_monotonicity_across_many_draws(self) -> None:
        spec = ArchivePriorSpec(
            name="core_a",
            node_depths=(0.0, 4.0, 10.0, 22.0, 35.0),
            dated_depths=(4.0, 10.0, 22.0, 35.0),
            query_depth=16.0,
            mean_surface_age=100.0,
            sd_surface_age=25.0,
            mean_sed_rate=50.0,
            kappa=0.8,
        )
        rng = random.Random(101)
        for _ in range(100):
            path = simulate_gamma_increment_path(spec, rng)
            self.assertEqual(len(path.node_ages), len(spec.node_depths))
            for i in range(1, len(path.node_ages)):
                self.assertGreater(path.node_ages[i], path.node_ages[i - 1])
            q_age = path.age_at(spec.query_depth)
            self.assertGreater(q_age, path.age_at(10.0))
            self.assertLess(q_age, path.age_at(22.0))

    def test_subdivision_invariance_moments(self) -> None:
        coarse = ArchivePriorSpec(
            name="coarse",
            node_depths=(0.0, 20.0),
            dated_depths=(20.0,),
            query_depth=20.0,
            mean_surface_age=0.0,
            sd_surface_age=0.0,
            mean_sed_rate=40.0,
            kappa=0.5,
        )
        refined = ArchivePriorSpec(
            name="refined",
            node_depths=(0.0, 3.5, 11.2, 20.0),
            dated_depths=(20.0,),
            query_depth=20.0,
            mean_surface_age=0.0,
            sd_surface_age=0.0,
            mean_sed_rate=40.0,
            kappa=0.5,
        )
        n = 12000
        rng_c = random.Random(202)
        rng_r = random.Random(303)
        c_ages = [simulate_gamma_increment_path(coarse, rng_c).age_at(20.0) for _ in range(n)]
        r_ages = [simulate_gamma_increment_path(refined, rng_r).age_at(20.0) for _ in range(n)]

        # Analytic moments: E = mean_sed_rate * dz = 800, Var = (mean_sed_rate^2 / kappa) * dz = 64000
        expected_mean = 40.0 * 20.0
        expected_var = (40.0**2 / 0.5) * 20.0
        for ages in (c_ages, r_ages):
            self.assertAlmostEqual(statistics.mean(ages), expected_mean, delta=12.0)
            self.assertAlmostEqual(statistics.variance(ages), expected_var, delta=3500.0)
        self.assertAlmostEqual(statistics.mean(c_ages), statistics.mean(r_ages), delta=10.0)
        self.assertAlmostEqual(statistics.variance(c_ages), statistics.variance(r_ages), delta=3500.0)


class TestPublicObservationContract(unittest.TestCase):
    def test_public_export_excludes_oracle_truth(self) -> None:
        spec = PairedChronologySpec.default_two_archive()
        obs, truth = simulate_paired_chronology(spec, random.Random(42))
        self.assertIsInstance(obs, PublicChronologyObservation)
        payload = json.dumps(obs.to_public_dict())
        for forbidden in (
            "true_ages",
            "true_calibration",
            "true_event_age",
            "true_delta",
            "oracle",
        ):
            self.assertNotIn(forbidden, payload)
        # Ensure oracle values do not accidentally appear as hidden fields
        self.assertNotIn("w_true", obs.to_public_dict())
        self.assertIsNotNone(truth.event_age_a)
        self.assertIsNotNone(truth.event_age_b)
        self.assertAlmostEqual(truth.delta_ab, truth.event_age_a - truth.event_age_b)


class TestAnalyticAndImportanceVerification(unittest.TestCase):
    def test_exact_gaussian_limit_closed_form_matches_mcmc(self) -> None:
        # Linear high-kappa limit with constant shared calibration offset
        # where analytic trivariate Gaussian formulas apply accurately.
        spec = PairedChronologySpec(
            archive_a=ArchivePriorSpec(
                name="core_a",
                node_depths=(0.0, 10.0),
                dated_depths=(0.0, 10.0),
                query_depth=5.0,
                mean_surface_age=1000.0,
                sd_surface_age=120.0,
                mean_sed_rate=50.0,
                kappa=2000.0,  # near-deterministic slope 50 yr/cm (SD ~ 3.5 yr over 10 cm)
                measurement_sds=(30.0, 30.0),
            ),
            archive_b=ArchivePriorSpec(
                name="core_b",
                node_depths=(0.0, 10.0),
                dated_depths=(0.0, 10.0),
                query_depth=5.0,
                mean_surface_age=1020.0,
                sd_surface_age=120.0,
                mean_sed_rate=50.0,
                kappa=2000.0,
                measurement_sds=(30.0, 30.0),
            ),
            calibration=CalibrationPriorSpec(
                knot_ages=(0.0, 3000.0),
                sd=100.0,
                corr_length=1e9,  # constant shared offset w_0
                nugget=1e-9,
            ),
        )
        obs, _ = simulate_paired_chronology(spec, random.Random(777))
        analytic = analytic_gaussian_limit_posterior(obs)
        ens = infer_joint_chronology(
            obs,
            rng=random.Random(888),
            n_chains=4,
            n_burnin=800,
            n_samples_per_chain=1200,
        )
        self.assertLess(ens.max_rhat, 1.05)
        self.assertAlmostEqual(ens.mean_a, analytic.mean_a, delta=6.0)
        self.assertAlmostEqual(ens.mean_b, analytic.mean_b, delta=6.0)
        self.assertAlmostEqual(ens.sd_a, analytic.sd_a, delta=5.0)
        self.assertAlmostEqual(ens.sd_b, analytic.sd_b, delta=5.0)
        self.assertAlmostEqual(ens.cov_ab, analytic.cov_ab, delta=450.0)
        self.assertAlmostEqual(ens.sd_delta, analytic.sd_delta, delta=5.0)

        # Shuffled ensemble inflates Var(delta) by ~ 2 * Cov(a, b)
        shuf = shuffle_paired_ensemble(ens, random.Random(999))
        self.assertGreater(shuf.sd_delta, ens.sd_delta * 1.35)
        self.assertAlmostEqual(shuf.cov_ab, 0.0, delta=350.0)

    def test_nonlinear_gamma_small_case_matches_importance_sampling(self) -> None:
        # Moderate kappa (non-Gaussian increments) and curved calibration prior
        spec = PairedChronologySpec(
            archive_a=ArchivePriorSpec(
                name="core_a",
                node_depths=(0.0, 6.0, 14.0),
                dated_depths=(0.0, 6.0, 14.0),
                query_depth=6.0,
                mean_surface_age=500.0,
                sd_surface_age=60.0,
                mean_sed_rate=40.0,
                kappa=0.8,
                measurement_sds=(35.0, 35.0, 35.0),
            ),
            archive_b=ArchivePriorSpec(
                name="core_b",
                node_depths=(0.0, 8.0, 16.0),
                dated_depths=(0.0, 8.0, 16.0),
                query_depth=8.0,
                mean_surface_age=520.0,
                sd_surface_age=60.0,
                mean_sed_rate=40.0,
                kappa=0.8,
                measurement_sds=(35.0, 35.0, 35.0),
            ),
            calibration=CalibrationPriorSpec(
                knot_ages=(0.0, 600.0, 1200.0, 1800.0),
                sd=75.0,
                corr_length=700.0,
                nugget=1e-6,
            ),
        )
        obs, _ = simulate_paired_chronology(spec, random.Random(1234))
        is_est = importance_sample_small_case(obs, n_draws=30000, rng=random.Random(5678))
        self.assertGreater(is_est.ess, 80.0)

        mcmc_est = infer_joint_chronology(
            obs,
            rng=random.Random(4321),
            n_chains=4,
            n_burnin=900,
            n_samples_per_chain=1200,
        )
        self.assertLess(mcmc_est.max_rhat, 1.06)
        self.assertAlmostEqual(mcmc_est.mean_a, is_est.mean_a, delta=12.0)
        self.assertAlmostEqual(mcmc_est.mean_b, is_est.mean_b, delta=12.0)
        self.assertAlmostEqual(mcmc_est.mean_delta, is_est.mean_delta, delta=12.0)
        self.assertAlmostEqual(mcmc_est.sd_delta, is_est.sd_delta, delta=10.0)
        self.assertAlmostEqual(mcmc_est.prob_a_older_than_b, is_est.prob_a_older_than_b, delta=0.06)


class TestRetainedFailureModes(unittest.TestCase):
    def test_unconstrained_nonmonotone_exhibits_age_reversals(self) -> None:
        # Closely spaced depths with substantial measurement noise cause age inversions
        # under unconstrained per-depth estimation, while monotone inference has zero.
        spec = PairedChronologySpec(
            archive_a=ArchivePriorSpec(
                name="core_a",
                node_depths=(0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
                dated_depths=(0.0, 1.0, 2.0, 3.0, 4.0, 5.0),
                query_depth=2.5,
                mean_surface_age=1000.0,
                sd_surface_age=50.0,
                mean_sed_rate=20.0,
                kappa=2.0,
                measurement_sds=(45.0, 45.0, 45.0, 45.0, 45.0, 45.0),
            ),
            archive_b=ArchivePriorSpec(
                name="core_b",
                node_depths=(0.0, 2.5, 5.0),
                dated_depths=(0.0, 2.5, 5.0),
                query_depth=2.5,
                mean_surface_age=1000.0,
                sd_surface_age=50.0,
                mean_sed_rate=20.0,
                kappa=2.0,
                measurement_sds=(45.0, 45.0, 45.0),
            ),
            calibration=CalibrationPriorSpec(
                knot_ages=(800.0, 1000.0, 1200.0, 1400.0),
                sd=40.0,
                corr_length=500.0,
                nugget=1e-6,
            ),
        )
        reversals_found = 0
        for seed in range(25):
            obs, _ = simulate_paired_chronology(spec, random.Random(2000 + seed))
            raw_ages = fit_unconstrained_nonmonotone(obs.archive_a)
            if any(raw_ages[i] <= raw_ages[i - 1] for i in range(1, len(raw_ages))):
                reversals_found += 1
        self.assertGreaterEqual(reversals_found, 15)

        # Monotone joint inference guarantees 0 reversals on every draw
        obs0, _ = simulate_paired_chronology(spec, random.Random(2000))
        ens = infer_joint_chronology(
            obs0,
            rng=random.Random(3000),
            n_chains=2,
            n_burnin=400,
            n_samples_per_chain=400,
        )
        self.assertEqual(ens.reversal_count_a, 0)
        self.assertEqual(ens.reversal_count_b, 0)

    def test_prior_predictive_sbc_and_failure_comparisons(self) -> None:
        report = run_calibration_and_failure_benchmark(n_trials=80, seed=20261124)
        # Under the model's own law, joint posterior achieves calibrated 90% coverage
        # and near-uniform PIT on both marginal ages and cross-archive delta = a_A - a_B.
        self.assertGreaterEqual(report.joint_cov90_a, 0.80)
        self.assertLessEqual(report.joint_cov90_a, 0.98)
        self.assertGreaterEqual(report.joint_cov90_delta, 0.80)
        self.assertLessEqual(report.joint_cov90_delta, 0.98)
        self.assertLess(report.joint_ks_delta, 0.18)

        # Shuffled marginals preserve marginal coverage but inflate delta width & over-cover delta
        self.assertGreater(report.shuffled_mean_width90_delta, report.joint_mean_width90_delta * 1.25)
        self.assertGreaterEqual(report.shuffled_cov90_delta, report.joint_cov90_delta)
        self.assertLess(report.joint_order_brier, report.shuffled_order_brier)

        # Treating shared calibration as independent across cores looks calibrated marginally
        # yet inflates cross-archive delta width and degrades ordering Brier score.
        self.assertGreaterEqual(report.independent_cal_cov90_a, 0.80)
        self.assertGreater(report.independent_cal_mean_width90_delta, report.joint_mean_width90_delta * 1.25)
        self.assertLess(report.joint_order_brier, report.independent_cal_order_brier)

        # Ignoring shared calibration completely under-covers marginal ages
        self.assertLess(report.ignored_cal_cov90_a, report.joint_cov90_a - 0.15)


class TestStatisticalHelpers(unittest.TestCase):
    def test_empirical_pit_and_ks(self) -> None:
        samples = [float(i) for i in range(100)]
        self.assertAlmostEqual(empirical_pit(samples, 49.5), 0.5, delta=0.02)
        uniform_grid = [(i + 0.5) / 50.0 for i in range(50)]
        self.assertLess(ks_uniform_statistic(uniform_grid), 0.03)
        bad_grid = [0.05] * 50
        self.assertGreater(ks_uniform_statistic(bad_grid), 0.90)


if __name__ == "__main__":
    unittest.main()
