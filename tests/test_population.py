"""Unit tests for population generation."""

import numpy as np
import pandas as pd
import pytest

from src.population import generate_population


class TestGeneratePopulation:
    """Test synthetic population generation."""

    def test_generate_population_basic(self):
        """Test basic population generation."""
        pop = generate_population(100, seed=42)
        assert len(pop) == 100
        assert set(pop.columns) == {"id", "crt_score", "media_exposure", "susceptibility"}

    def test_generate_population_id_unique(self):
        """IDs should be unique and sequential."""
        pop = generate_population(50, seed=42)
        assert pop["id"].nunique() == 50
        assert list(pop["id"]) == list(range(1, 51))

    def test_generate_population_crt_range(self):
        """CRT scores should be in [0, 5]."""
        pop = generate_population(1000, seed=42)
        assert pop["crt_score"].min() >= 0
        assert pop["crt_score"].max() <= 5
        assert all(pop["crt_score"] == pop["crt_score"].astype(int))

    def test_generate_population_media_exposure_range(self):
        """Media exposure should be in [0, 12]."""
        pop = generate_population(1000, seed=42)
        assert pop["media_exposure"].min() >= 0
        assert pop["media_exposure"].max() <= 12

    def test_generate_population_susceptibility_range(self):
        """Susceptibility should be in [0, 1]."""
        pop = generate_population(1000, seed=42)
        assert pop["susceptibility"].min() >= 0
        assert pop["susceptibility"].max() <= 1

    def test_generate_population_crt_susceptibility_inverse(self):
        """Higher CRT score should correlate with lower susceptibility."""
        pop = generate_population(5000, seed=42)
        low_crt = pop[pop["crt_score"] <= 2]["susceptibility"].mean()
        high_crt = pop[pop["crt_score"] >= 4]["susceptibility"].mean()
        assert low_crt > high_crt

    def test_generate_population_media_susceptibility_positive(self):
        """Higher media exposure should correlate with higher susceptibility."""
        pop = generate_population(5000, seed=42)
        low_media = pop[pop["media_exposure"] <= 2]["susceptibility"].mean()
        high_media = pop[pop["media_exposure"] >= 5]["susceptibility"].mean()
        assert high_media > low_media

    def test_generate_population_reproducibility(self):
        """Same seed should produce identical population."""
        pop1 = generate_population(100, seed=42)
        pop2 = generate_population(100, seed=42)
        pd.testing.assert_frame_equal(pop1, pop2)

    def test_generate_population_different_seeds(self):
        """Different seeds should produce different populations."""
        pop1 = generate_population(100, seed=42)
        pop2 = generate_population(100, seed=123)
        assert not pop1.equals(pop2)

    def test_generate_population_invalid_n(self):
        """Negative or zero n should raise ValueError."""
        with pytest.raises(ValueError):
            generate_population(0)
        with pytest.raises(ValueError):
            generate_population(-10)
