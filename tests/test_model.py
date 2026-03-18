"""Unit tests for SEIR model equations."""

import pytest

from src.model import seir_model


class TestSEIRModel:
    """Test SEIR differential equations."""

    def test_seir_model_reduction_with_zero_infected(self):
        """When I=0, S should not decrease."""
        y = [1.0, 0.1, 0.0, 0.0]  # S, E, I, R
        derivs = seir_model(y, 0, beta=0.5, sigma=0.2, gamma=0.1)
        assert derivs[0] == 0.0  # dS/dt should be 0

    def test_seir_model_e_to_i_flow(self):
        """E should decrease when sigma > 0."""
        y = [0.5, 0.3, 0.1, 0.1]
        derivs = seir_model(y, 0, beta=0.5, sigma=0.2, gamma=0.1)
        assert derivs[1] < 0  # dE/dt negative (flow out)

    def test_seir_model_i_recovery(self):
        """I should decrease when gamma > 0."""
        y = [0.5, 0.1, 0.3, 0.1]
        derivs = seir_model(y, 0, beta=0.5, sigma=0.2, gamma=0.1)
        assert derivs[2] < 0  # dI/dt negative (recovery)

    def test_seir_model_conservation(self):
        """Total change should be zero (conservation of population)."""
        y = [0.6, 0.2, 0.1, 0.1]
        derivs = seir_model(y, 0, beta=0.3, sigma=0.2, gamma=0.1)
        total_deriv = sum(derivs)
        assert abs(total_deriv) < 1e-10  # Should sum to ~0

    def test_seir_model_disease_dynamics(self):
        """Exposure should drive transition to infected."""
        y = [0.8, 0.1, 0.1, 0.0]
        beta_high = 0.8
        beta_low = 0.1
        derivs_high = seir_model(y, 0, beta=beta_high, sigma=0.2, gamma=0.1)
        derivs_low = seir_model(y, 0, beta=beta_low, sigma=0.2, gamma=0.1)
        # Higher beta should lead to more S reduction
        assert derivs_high[0] < derivs_low[0]

    def test_seir_model_parameter_sensitivity(self):
        """Gamma should affect recovery rate."""
        y = [0.5, 0.2, 0.2, 0.1]
        derivs_low_gamma = seir_model(y, 0, beta=0.3, sigma=0.2, gamma=0.05)
        derivs_high_gamma = seir_model(y, 0, beta=0.3, sigma=0.2, gamma=0.2)
        # Higher gamma should lead to more I reduction
        assert derivs_high_gamma[2] < derivs_low_gamma[2]
