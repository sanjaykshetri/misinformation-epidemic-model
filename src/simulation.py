"""Simulation engine for deterministic misinformation SEIR dynamics.

This module provides the computational framework for integrating the SEIR differential equations
and mapping population parameters to model dynamics.

Key Functions:
    - run_simulation: Integrates ODE system with given parameters
    - aggregate_parameters_from_population: Converts synthetic population features to model parameters
    - beta_from_media_exposure: Maps media consumption to transmission rate
    - sigma_from_crt_score: Maps critical thinking ability to adoption rate

Type Annotations:
    - All functions use Python 3.10+ type hints with explicit parameter and return types
    - Supports both positional and keyword arguments for flexibility
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
import pandas as pd
from scipy.integrate import odeint

from .model import seir_model


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration for a single SEIR simulation run."""

    beta: float = 0.28
    sigma: float = 0.18
    gamma: float = 0.10
    days: int = 180
    time_steps: int = 1801
    initial_exposed: float = 0.01
    initial_infected: float = 0.01


def beta_from_media_exposure(
    media_exposure_hours: float,
    base_beta: float = 0.20,
    slope: float = 0.035,
    min_beta: float = 0.05,
    max_beta: float = 1.00,
) -> float:
    """Map media exposure to exposure rate beta.
    
    Converts hours of daily media consumption to the transmission rate parameter β.
    
    The relationship is approximately linear: β(h) = base_beta + slope × h, clipped to [min_beta, max_beta].
    
    Args:
        media_exposure_hours: Average daily hours spent consuming media (0-12 typical range).
        base_beta: Baseline transmission rate with zero media exposure. Default 0.20.
        slope: Sensitivity of beta to media hours (higher = more sensitive). Default 0.035.
        min_beta: Lower bound on transmission rate. Default 0.05.
        max_beta: Upper bound on transmission rate. Default 1.00.
    
    Returns:
        Transmission rate β ∈ [min_beta, max_beta] (1/time units).
        
    Biological Interpretation:
        - Higher media exposure increases likelihood of encountering misinformation
        - Increased contact with infected individuals' content → higher transmission probability
        - Clipping prevents unrealistic extremes
    
    Example:
        >>> beta = beta_from_media_exposure(4.0)  # 4 hours/day → β ≈ 0.34
    """
    beta: float = base_beta + slope * float(media_exposure_hours)
    return float(np.clip(beta, min_beta, max_beta))


def sigma_from_crt_score(
    crt_score: float,
    base_sigma: float = 0.25,
    slope: float = 0.03,
    min_sigma: float = 0.02,
    max_sigma: float = 0.60,
) -> float:
    """Map CRT score to adoption rate sigma (inverse relationship).
    
    Converts Cognitive Reflection Test score (0-5) to adoption rate σ.
    
    Higher CRT (better critical thinking) → Lower σ (slower belief adoption).
    The relationship is approximately linear: σ(c) = base_sigma - slope × c, clipped to [min_sigma, max_sigma].
    
    Args:
        crt_score: Cognitive Reflection Test score from 0 (no reflection) to 5 (high reflection).
        base_sigma: Baseline adoption rate with zero critical thinking. Default 0.25.
        slope: Sensitivity of sigma to CRT improvement (higher = more sensitive). Default 0.03.
        min_sigma: Lower bound on adoption rate (minimum susceptibility). Default 0.02.
        max_sigma: Upper bound on adoption rate (maximum susceptibility). Default 0.60.
    
    Returns:
        Adoption rate σ ∈ [min_sigma, max_sigma] (1/time units).
        
    Psychological Interpretation:
        - CRT measures ability to suppress intuitive but incorrect responses
        - Higher CRT → greater epistemic vigilance → slower belief adoption
        - Inverse relationship documented in cognitive psychology literature
        - Clipping prevents unrealistic extremes
    
    Example:
        >>> sigma = sigma_from_crt_score(4.0)  # High CRT (4/5) → σ ≈ 0.13
    """
    sigma: float = base_sigma - slope * float(crt_score)
    return float(np.clip(sigma, min_sigma, max_sigma))


def aggregate_parameters_from_population(
    population: pd.DataFrame,
    gamma: float = 0.10,
) -> tuple[float, float, float]:
    """Convert synthetic population features into aggregate model parameters.
    
    Transforms individual-level population characteristics (CRT scores, media exposure)
    into population-averaged SEIR model parameters β, σ, γ.
    
    This mapping implements a mean-field approximation: population-level dynamics are averages
    of individual-level heterogeneity.
    
    Args:
        population: DataFrame with required columns:
            - crt_score: float, Cognitive Reflection Test scores ∈ [0, 5]
            - media_exposure: float, Hours per day ∈ [0, 12]
        gamma: Recovery rate parameter (independent of population features). Default 0.10.
    
    Returns:
        Tuple (beta, sigma, gamma) where:
        - beta: float, Transmission rate computed from mean media exposure
        - sigma: float, Adoption rate computed from mean CRT score
        - gamma: float, Recovery rate (copy of input parameter)
    
    Raises:
        ValueError: If population is missing required columns.
    
    Mean-Field Approximation:
        β(population) = β(mean media_exposure)
        σ(population) = σ(mean CRT_score)
        
        This trades off spatial/individual heterogeneity for computational tractability.
        See METHODOLOGY.md Section 3 (Key Assumptions) for validity discussion.
    
    Example:
        >>> pop = pd.DataFrame({'crt_score': [2, 3, 4], 'media_exposure': [3, 4, 5]})
        >>> beta, sigma, gamma = aggregate_parameters_from_population(pop)
    """
    required_cols: set = {"crt_score", "media_exposure"}
    missing: set = required_cols - set(population.columns)
    if missing:
        raise ValueError(f"Population missing required columns: {sorted(missing)}")

    mean_media: float = float(population["media_exposure"].mean())
    mean_crt: float = float(population["crt_score"].mean())

    beta: float = beta_from_media_exposure(mean_media)
    sigma: float = sigma_from_crt_score(mean_crt)
    return beta, sigma, float(gamma)


def run_simulation(
    config: SimulationConfig | None = None,
    *,
    beta: float | None = None,
    sigma: float | None = None,
    gamma: float | None = None,
    days: int | None = None,
    time_steps: int | None = None,
    initial_exposed: float | None = None,
    initial_infected: float | None = None,
) -> pd.DataFrame:
    """Run deterministic SEIR simulation and return compartment time series.
    
    Integrates the system of differential equations:
        dS/dt = -β·S·I
        dE/dt = β·S·I - σ·E
        dI/dt = σ·E - γ·I
        dR/dt = γ·I
    
    using scipy.integrate.odeint with RK45 solver (default).
    
    Parameters:
        config: SimulationConfig object for parameter defaults. If None, uses SimulationConfig().
                Individual keyword arguments override config values.
        beta: Transmission rate (1/time). Default from config or 0.28.
        sigma: Adoption rate (1/time). Default from config or 0.18.
        gamma: Recovery rate (1/time). Default from config or 0.10.
        days: Simulation horizon (time units). Default from config or 180.
        time_steps: Number of integration steps. Default from config or 1801.
        initial_exposed: Initial fraction in E compartment. Default from config or 0.01.
        initial_infected: Initial fraction in I compartment. Default from config or 0.01.
    
    Returns:
        DataFrame with columns [t, S, E, I, R] where:
        - t: Time points (0 to days)
        - S, E, I, R: Fraction of population in each SEIR compartment
        
        DataFrame.attrs['parameters'] contains a dictionary of all parameter values used.
    
    Raises:
        ValueError: If initial_exposed + initial_infected > 1 (impossible initialization).
    
    Numerical Details:
        - Initial susceptible computed as S(0) = 1 - E(0) - I(0)
        - Scalar constraint S + E + I + R = 1 preserved by ODE structure
        - Time spacing: equal steps from 0 to days
    
    Example:
        >>> ts = run_simulation(beta=0.3, gamma=0.1, days=100)
        >>> print(ts[['t', 'I']].head())  # First few time points
        >>> peak_infected = ts['I'].max()
    """
    cfg: SimulationConfig = config or SimulationConfig()

    beta_val: float = cfg.beta if beta is None else float(beta)
    sigma_val: float = cfg.sigma if sigma is None else float(sigma)
    gamma_val: float = cfg.gamma if gamma is None else float(gamma)
    days_val: int = cfg.days if days is None else int(days)
    time_steps_val: int = cfg.time_steps if time_steps is None else int(time_steps)
    initial_exposed_val: float = cfg.initial_exposed if initial_exposed is None else float(initial_exposed)
    initial_infected_val: float = cfg.initial_infected if initial_infected is None else float(initial_infected)

    initial_susceptible: float = 1.0 - initial_exposed_val - initial_infected_val
    if initial_susceptible < 0:
        raise ValueError("initial_exposed + initial_infected must be <= 1")

    y0: list[float] = [initial_susceptible, initial_exposed_val, initial_infected_val, 0.0]
    t: np.ndarray = np.linspace(0, days_val, time_steps_val)

    solution: np.ndarray = odeint(seir_model, y0, t, args=(beta_val, sigma_val, gamma_val))
    results: pd.DataFrame = pd.DataFrame(solution, columns=["S", "E", "I", "R"])
    results.insert(0, "t", t)

    results.attrs["parameters"] = {
        "beta": beta_val,
        "sigma": sigma_val,
        "gamma": gamma_val,
        "days": days_val,
        "time_steps": time_steps_val,
        "initial_exposed": initial_exposed_val,
        "initial_infected": initial_infected_val,
    }

    return results
