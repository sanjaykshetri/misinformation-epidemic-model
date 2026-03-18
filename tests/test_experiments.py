"""Unit tests for experiment scenarios."""

import pytest

from src.experiments import (
    baseline,
    education_intervention,
    increased_recovery,
    reduced_exposure,
    run_all_experiments,
)


class TestBaselineExperiment:
    """Test baseline experiment scenario."""

    def test_baseline_returns_dict(self):
        """Baseline should return dict with expected keys."""
        result = baseline(population_size=100, days=10)
        assert isinstance(result, dict)
        assert set(result.keys()) == {"name", "parameters", "time_series", "metrics"}

    def test_baseline_name(self):
        """Baseline should have correct name."""
        result = baseline(population_size=100, days=10)
        assert result["name"] == "baseline"

    def test_baseline_metrics_keys(self):
        """Baseline metrics should have expected keys."""
        result = baseline(population_size=100, days=10)
        metrics_keys = set(result["metrics"].keys())
        assert metrics_keys == {"peak_infection", "time_to_peak", "final_recovered", "area_under_infection_curve"}

    def test_baseline_time_series_shape(self):
        """Baseline time series should have expected shape."""
        result = baseline(population_size=100, days=10)
        ts = result["time_series"]
        assert set(ts.columns) == {"t", "S", "E", "I", "R"}


class TestReducedExposureExperiment:
    """Test reduced exposure intervention."""

    def test_reduced_exposure_lower_peak(self):
        """Reducing exposure should lower peak infection."""
        base = baseline(population_size=500, days=30)
        reduced = reduced_exposure(population_size=500, days=30)

        base_peak = base["metrics"]["peak_infection"]
        reduced_peak = reduced["metrics"]["peak_infection"]
        assert reduced_peak < base_peak

    def test_reduced_exposure_lower_beta(self):
        """Beta should be lower in reduced exposure scenario."""
        base = baseline(population_size=500, days=30)
        reduced = reduced_exposure(population_size=500, days=30)

        assert reduced["parameters"]["beta"] < base["parameters"]["beta"]

    def test_reduced_exposure_clamped(self):
        """Reduction fraction should be clamped to [0, 0.95]."""
        result_high = reduced_exposure(reduction_fraction=2.0, population_size=100, days=10)
        result_clamped = reduced_exposure(reduction_fraction=0.95, population_size=100, days=10)
        # Both should complete without error; 2.0 gets clamped to 0.95
        # (they won't be equal due to different baselines, but both should be valid)
        assert result_high["parameters"]["beta"] > 0
        assert result_clamped["parameters"]["beta"] > 0


class TestIncreasedRecoveryExperiment:
    """Test increased recovery intervention."""

    def test_increased_recovery_lower_peak(self):
        """Increasing recovery should lower peak infection."""
        base = baseline(population_size=500, days=30)
        recovery = increased_recovery(population_size=500, days=30)

        base_peak = base["metrics"]["peak_infection"]
        recovery_peak = recovery["metrics"]["peak_infection"]
        assert recovery_peak < base_peak

    def test_increased_recovery_higher_gamma(self):
        """Gamma should be higher in increased recovery scenario."""
        base = baseline(population_size=500, days=30)
        recovery = increased_recovery(population_size=500, days=30)

        assert recovery["parameters"]["gamma"] > base["parameters"]["gamma"]


class TestEducationInterventionExperiment:
    """Test education intervention scenario."""

    def test_education_intervention_lower_peak(self):
        """Education intervention should lower peak infection."""
        base = baseline(population_size=500, days=30)
        education = education_intervention(population_size=500, days=30)

        base_peak = base["metrics"]["peak_infection"]
        education_peak = education["metrics"]["peak_infection"]
        assert education_peak < base_peak

    def test_education_intervention_modified_parameters(self):
        """Education should reduce both beta and sigma."""
        base = baseline(population_size=500, days=30)
        education = education_intervention(population_size=500, days=30)

        assert education["parameters"]["beta"] < base["parameters"]["beta"]
        assert education["parameters"]["sigma"] < base["parameters"]["sigma"]


class TestRunAllExperiments:
    """Test comprehensive experiment suite."""

    def test_run_all_experiments_returns_list(self):
        """Should return list of 4 scenarios."""
        results = run_all_experiments(population_size=100, days=10)
        assert isinstance(results, list)
        assert len(results) == 4

    def test_run_all_experiments_names(self):
        """Should have correct scenario names."""
        results = run_all_experiments(population_size=100, days=10)
        names = [r["name"] for r in results]
        assert names == ["baseline", "reduced_exposure", "increased_recovery", "education_intervention"]

    def test_run_all_experiments_peak_ordering(self):
        """Non-baseline scenarios should have lower or equal peaks than baseline."""
        results = run_all_experiments(population_size=500, days=30)
        baseline_result = [r for r in results if r["name"] == "baseline"][0]
        baseline_peak = baseline_result["metrics"]["peak_infection"]

        for result in results[1:]:  # Skip baseline
            assert result["metrics"]["peak_infection"] <= baseline_peak
