"""Intervention experiments for misinformation SEIR dynamics.

This module defines four intervention scenarios:
1. Baseline: No intervention (control)
2. Reduced Exposure: Platform interventions lowering β
3. Increased Recovery: Fact-checking interventions raising γ
4. Education: Combined educational + platform interventions

Each experiment returns results including time series, parameters, and aggregate metrics.

Experiment Results Format:
    dict[str, Any] with keys:
        - 'name': str, scenario identifier
        - 'parameters': dict[str, float], model parameters {beta, sigma, gamma}
        - 'time_series': pd.DataFrame, SEIR compartments vs. time
        - 'metrics': dict[str, float], derived epidemiological metrics
"""

from __future__ import annotations

from typing import Any, TypedDict

import pandas as pd

from .population import generate_population
from .simulation import aggregate_parameters_from_population, run_simulation


class ExperimentMetrics(TypedDict):
    """Result metrics computed from time series."""
    peak_infection: float
    time_to_peak: float
    final_recovered: float
    area_under_infection_curve: float


class ExperimentResult(TypedDict):
    """Complete result from a single intervention experiment."""
    name: str
    parameters: dict[str, float]
    time_series: pd.DataFrame
    metrics: ExperimentMetrics


def _summarize_time_series(df: pd.DataFrame) -> ExperimentMetrics:
    """Compute epidemiological metrics from simulated time series.
    
    Args:
        df: DataFrame with columns [t, S, E, I, R] from run_simulation().
    
    Returns:
        ExperimentMetrics with keys:
            - peak_infection: Maximum fraction infected at any time point
            - time_to_peak: Time (days) when peak occurs
            - final_recovered: Fraction recovered at final time point
            - area_under_infection_curve: ∫I dt (cumulative infection exposure)
    """
    peak_idx: int = int(df["I"].idxmax())
    return ExperimentMetrics(
        peak_infection=float(df.loc[peak_idx, "I"]),
        time_to_peak=float(df.loc[peak_idx, "t"]),
        final_recovered=float(df["R"].iloc[-1]),
        area_under_infection_curve=float(df["I"].sum() * (df["t"].iloc[1] - df["t"].iloc[0])),
    )


def baseline(population_size: int = 10000, gamma: float = 0.10, days: int = 180) -> ExperimentResult:
    """Baseline scenario from unmodified synthetic population.
    
    No interventions applied. Serves as control for comparing intervention effectiveness.
    Parameters derived directly from synthetic population features.
    
    Args:
        population_size: Number of synthetic individuals. Default 10000.
        gamma: Fixed recovery rate parameter. Default 0.10.
        days: Simulation horizon. Default 180 days.
    
    Returns:
        ExperimentResult containing baseline trajectory and metrics.
    """
    population: pd.DataFrame = generate_population(population_size)
    beta, sigma, gamma = aggregate_parameters_from_population(population, gamma=gamma)
    ts: pd.DataFrame = run_simulation(beta=beta, sigma=sigma, gamma=gamma, days=days)

    return ExperimentResult(
        name="baseline",
        parameters={"beta": beta, "sigma": sigma, "gamma": gamma},
        time_series=ts,
        metrics=_summarize_time_series(ts),
    )


def reduced_exposure(
    reduction_fraction: float = 0.25,
    population_size: int = 10000,
    gamma: float = 0.10,
    days: int = 180,
) -> ExperimentResult:
    """Intervention reducing exposure rate beta.
    
    Represents platform interventions (content moderation, algorithm changes, warning labels)
    that reduce likelihood of contact with misinformation sources.
    
    Mechanism: β(intervention) = β(baseline) × (1 - reduction_fraction)
    
    Args:
        reduction_fraction: Fractional reduction in β ∈ [0, 0.95]. Default 0.25 (25% reduction).
        population_size: Number of synthetic individuals. Default 10000.
        gamma: Fixed recovery rate parameter. Default 0.10.
        days: Simulation horizon. Default 180 days.
    
    Returns:
        ExperimentResult containing reduced-exposure trajectory and metrics.
    """
    base: ExperimentResult = baseline(population_size=population_size, gamma=gamma, days=days)
    reduction_fraction = max(0.0, min(0.95, reduction_fraction))

    beta: float = base["parameters"]["beta"] * (1 - reduction_fraction)
    sigma: float = base["parameters"]["sigma"]
    gamma_val: float = base["parameters"]["gamma"]

    ts: pd.DataFrame = run_simulation(beta=beta, sigma=sigma, gamma=gamma_val, days=days)
    return ExperimentResult(
        name="reduced_exposure",
        parameters={"beta": beta, "sigma": sigma, "gamma": gamma_val},
        time_series=ts,
        metrics=_summarize_time_series(ts),
    )


def increased_recovery(
    increase_fraction: float = 0.35,
    population_size: int = 10000,
    gamma: float = 0.10,
    days: int = 180,
) -> ExperimentResult:
    """Intervention increasing recovery rate gamma.
    
    Represents fact-checking and correction interventions that help people
    recover from misinformation beliefs.
    
    Mechanism: γ(intervention) = γ(baseline) × (1 + increase_fraction)
    
    Args:
        increase_fraction: Fractional increase in γ ∈ [0, 2.0]. Default 0.35 (35% increase).
        population_size: Number of synthetic individuals. Default 10000.
        gamma: Fixed baseline recovery rate parameter. Default 0.10.
        days: Simulation horizon. Default 180 days.
    
    Returns:
        ExperimentResult containing increased-recovery trajectory and metrics.
    """
    base: ExperimentResult = baseline(population_size=population_size, gamma=gamma, days=days)
    increase_fraction = max(0.0, min(2.0, increase_fraction))

    beta: float = base["parameters"]["beta"]
    sigma: float = base["parameters"]["sigma"]
    gamma_val: float = base["parameters"]["gamma"] * (1 + increase_fraction)

    ts: pd.DataFrame = run_simulation(beta=beta, sigma=sigma, gamma=gamma_val, days=days)
    return ExperimentResult(
        name="increased_recovery",
        parameters={"beta": beta, "sigma": sigma, "gamma": gamma_val},
        time_series=ts,
        metrics=_summarize_time_series(ts),
    )


def education_intervention(
    crt_gain: float = 1.0,
    exposure_reduction_fraction: float = 0.15,
    population_size: int = 10000,
    gamma: float = 0.10,
    days: int = 180,
) -> ExperimentResult:
    """Intervention improving CRT and reducing media exposure.
    
    Represents comprehensive educational intervention combining:
    1. Improved critical thinking (higher CRT scores) → lower σ
    2. Reduced media consumption (lower media hours) → lower β
    
    This is most comprehensive intervention, combining multiple mechanisms.
    
    Args:
        crt_gain: Points to add to each individual's CRT score (clipped to [0, 5]). 
                  Default 1.0 (everyone gains 1 point, typical effect size for edu).
        exposure_reduction_fraction: Fractional reduction in media exposure ∈ [0, 0.95].
                                     Default 0.15 (15% reduction).
        population_size: Number of synthetic individuals. Default 10000.
        gamma: Fixed recovery rate parameter. Default 0.10.
        days: Simulation horizon. Default 180 days.
    
    Returns:
        ExperimentResult containing education-intervention trajectory and metrics.
    
    Mechanism:
        1. Generate baseline population
        2. Increase CRT scores: crt_score → min(5, crt_score + crt_gain)
        3. Reduce media exposure: media → media × (1 - reduction_fraction)
        4. Aggregate modified features to new parameters
    """
    population: pd.DataFrame = generate_population(population_size)

    population = population.copy()
    population["crt_score"] = (population["crt_score"] + crt_gain).clip(0, 5)
    population["media_exposure"] = population["media_exposure"] * (1 - max(0.0, min(0.95, exposure_reduction_fraction)))

    beta, sigma, gamma_val = aggregate_parameters_from_population(population, gamma=gamma)
    ts: pd.DataFrame = run_simulation(beta=beta, sigma=sigma, gamma=gamma_val, days=days)

    return ExperimentResult(
        name="education_intervention",
        parameters={"beta": beta, "sigma": sigma, "gamma": gamma_val},
        time_series=ts,
        metrics=_summarize_time_series(ts),
    )


def run_all_experiments(
    population_size: int = 10000, gamma: float = 0.10, days: int = 180
) -> list[ExperimentResult]:
    """Run all intervention scenarios and return results.
    
    Executes the complete experimental protocol:
    1. Baseline (no intervention)
    2. Reduced Exposure (platform intervention)
    3. Increased Recovery (fact-checking intervention)
    4. Education (comprehensive intervention)
    
    All use the same population_size and gamma for fair comparison.
    
    Args:
        population_size: Number of synthetic individuals per scenario. Default 10000.
        gamma: Fixed recovery rate parameter for all scenarios. Default 0.10.
        days: Simulation horizon (time units) for all scenarios. Default 180.
    
    Returns:
        List of 4 ExperimentResult dictionaries in execution order:
            [baseline, reduced_exposure, increased_recovery, education_intervention]
    
    Comparison:
        Results can be compared by examining:
        - metrics['peak_infection']: Which intervention minimizes peak?
        - metrics['final_recovered']: Which prevents most infections?
        - parameters: How much do beta/sigma change?
    
    Example:
        >>> results = run_all_experiments(population_size=5000, days=180)
        >>> for r in results:
        ...     print(f"{r['name']}: peak={r['metrics']['peak_infection']:.4f}")
    """
    return [
        baseline(population_size=population_size, gamma=gamma, days=days),
        reduced_exposure(population_size=population_size, gamma=gamma, days=days),
        increased_recovery(population_size=population_size, gamma=gamma, days=days),
        education_intervention(population_size=population_size, gamma=gamma, days=days),
    ]
