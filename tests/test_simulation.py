"""Unit tests for simulation engine and parameter mapping."""

import pandas as pd
import pytest

from src.simulation import (
    SimulationConfig,
    aggregate_parameters_from_population,
    beta_from_media_exposure,
    run_simulation,
    sigma_from_crt_score,
)


class TestParameterMapping:
    """Test parameter mapping from features to dynamics."""

    def test_beta_from_media_exposure_increases(self):
        """Higher media exposure should increase beta."""
        beta_low = beta_from_media_exposure(0)
        beta_mid = beta_from_media_exposure(5)
        beta_high = beta_from_media_exposure(10)
        assert beta_low < beta_mid < beta_high

    def test_beta_from_media_exposure_bounded(self):
        """Beta should stay within [min_beta, max_beta]."""
        beta_extreme_low = beta_from_media_exposure(-100)
        beta_extreme_high = beta_from_media_exposure(1000)
        assert beta_extreme_low >= 0.05
        assert beta_extreme_high <= 1.00

    def test_sigma_from_crt_score_decreases(self):
        """Higher CRT score should decrease sigma (lower adoption)."""
        sigma_low_crt = sigma_from_crt_score(1)
        sigma_mid_crt = sigma_from_crt_score(3)
        sigma_high_crt = sigma_from_crt_score(5)
        assert sigma_low_crt > sigma_mid_crt > sigma_high_crt

    def test_sigma_from_crt_score_bounded(self):
        """Sigma should stay within [min_sigma, max_sigma]."""
        sigma_extreme_low = sigma_from_crt_score(-10)
        sigma_extreme_high = sigma_from_crt_score(100)
        assert sigma_extreme_low >= 0.02
        assert sigma_extreme_high <= 0.60

    def test_aggregate_parameters_from_population(self):
        """Test aggregation from population features."""
        from src.population import generate_population

        pop = generate_population(100, seed=42)
        beta, sigma, gamma = aggregate_parameters_from_population(pop, gamma=0.1)

        assert 0.05 <= beta <= 1.0
        assert 0.02 <= sigma <= 0.6
        assert gamma == 0.1

    def test_aggregate_parameters_missing_columns(self):
        """Should raise error if population missing required columns."""
        pop = pd.DataFrame({"id": [1, 2, 3], "other_col": [4, 5, 6]})
        with pytest.raises(ValueError, match="missing required columns"):
            aggregate_parameters_from_population(pop)


class TestSimulationConfig:
    """Test SimulationConfig dataclass."""

    def test_simulation_config_defaults(self):
        """Test default configuration."""
        cfg = SimulationConfig()
        assert cfg.beta == 0.28
        assert cfg.sigma == 0.18
        assert cfg.gamma == 0.10
        assert cfg.days == 180
        assert cfg.time_steps == 1801

    def test_simulation_config_frozen(self):
        """Config should be immutable."""
        cfg = SimulationConfig()
        with pytest.raises(Exception):  # FrozenInstanceError
            cfg.beta = 0.5


class TestRunSimulation:
    """Test simulation engine."""

    def test_run_simulation_output_shape(self):
        """Simulation should return correct shape."""
        results = run_simulation(days=10, time_steps=101)
        assert len(results) == 101
        assert set(results.columns) == {"t", "S", "E", "I", "R"}

    def test_run_simulation_conservation(self):
        """Total population should be conserved."""
        results = run_simulation(days=10, time_steps=101)
        for idx in results.index:
            total = results.loc[idx, "S"] + results.loc[idx, "E"] + results.loc[idx, "I"] + results.loc[idx, "R"]
            assert abs(total - 1.0) < 1e-10

    def test_run_simulation_initial_conditions(self):
        """Should respect initial conditions."""
        results = run_simulation(
            days=10,
            time_steps=101,
            initial_exposed=0.02,
            initial_infected=0.01,
        )
        assert abs(results.loc[0, "S"] - 0.97) < 1e-10
        assert abs(results.loc[0, "E"] - 0.02) < 1e-10
        assert abs(results.loc[0, "I"] - 0.01) < 1e-10
        assert abs(results.loc[0, "R"] - 0.00) < 1e-10

    def test_run_simulation_monotonic_recovery(self):
        """R should be monotonically increasing."""
        results = run_simulation(days=20, time_steps=201)
        r_values = results["R"].values
        assert all(r_values[i] <= r_values[i + 1] for i in range(len(r_values) - 1))

    def test_run_simulation_initial_population_invalid(self):
        """Should raise error if initial compartments exceed 1."""
        with pytest.raises(ValueError, match="must be <= 1"):
            run_simulation(initial_exposed=0.8, initial_infected=0.5)

    def test_run_simulation_with_config(self):
        """Should accept SimulationConfig object."""
        cfg = SimulationConfig(beta=0.5, sigma=0.3, gamma=0.15, days=20, time_steps=21)
        results = run_simulation(config=cfg)
        assert len(results) == 21
        assert results.attrs["parameters"]["beta"] == 0.5

    def test_run_simulation_parameter_override(self):
        """Keyword arguments should override config."""
        cfg = SimulationConfig(beta=0.5)
        results = run_simulation(config=cfg, beta=0.2, days=5, time_steps=51)
        assert results.attrs["parameters"]["beta"] == 0.2

    def test_run_simulation_attributes_stored(self):
        """Parameters should be stored in attrs."""
        results = run_simulation(beta=0.3, sigma=0.2, gamma=0.15, days=30, time_steps=301)
        assert results.attrs["parameters"]["beta"] == 0.3
        assert results.attrs["parameters"]["sigma"] == 0.2
        assert results.attrs["parameters"]["gamma"] == 0.15
