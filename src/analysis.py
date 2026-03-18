"""Analysis utilities for SEIR model: R₀, sensitivity, and epidemiological metrics.

This module provides tools to understand model behavior:
- Basic Reproduction Number (R₀): Average secondary infections
- Sensitivity analysis: Which parameters matter most?
- Epidemiological metrics: Attack rates, durations, etc.

**Key Concept: R₀ (Basic Reproduction Number)**

R₀ is the expected number of secondary infections caused by a single infected individual
in a completely susceptible population. It's THE central quantity in epidemiology.

For SEIR:
    R₀ = β / γ = (contact rate) / (recovery rate)

Interpretation:
    R₀ < 1: Epidemic dies out naturally
    R₀ = 1: Endemic equilibrium (disease persists)
    R₀ > 1: Exponential growth initially

For misinformation:
    - R₀ = 2.5 means each person who believes spreads to 2.5 others on average
    - Interventions that lower R₀ below 1 eliminate the "epidemic"

**References:**
- Anderson, R. M., & May, R. M. (1991). Infectious Diseases of Humans: Dynamics and Control.
- Wallinga, J., & Lipsitch, M. (2007). How generation intervals shape the relationship between
  growth rates and reproductive numbers. Proceedings of the Royal Society B, 274(1609), 599–604.
"""

from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy.integrate import odeint

from .model import seir_model
from .simulation import SimulationConfig, run_simulation


def calculate_r0(beta: float, gamma: float) -> float:
    """Calculate basic reproduction number R₀.

    **Mathematical Definition:**
    R₀ = β / γ

    Where:
    - β: Rate at which infected contacts susceptible individuals
    - γ: Rate at which infected individuals recover

    **Interpretation:**
    - R₀ < 1: Epidemic dies out
    - R₀ = 1: Endemic steady state
    - R₀ > 1: Exponential growth

    **For Misinformation Context:**
    Each infected person convinces R₀ others on average before being corrected.

    Args:
        beta: Exposure rate (β > 0).
        gamma: Recovery rate (γ > 0).

    Returns:
        float: Basic reproduction number R₀ ≥ 0.

    Raises:
        ValueError: If parameters are not positive.

    Example:
        >>> r0 = calculate_r0(beta=0.3, gamma=0.1)
        >>> r0
        3.0
        >>> # Each misinformed person reaches 3 others on average
    """
    if beta <= 0 or gamma <= 0:
        raise ValueError(f"beta and gamma must be positive; got beta={beta}, gamma={gamma}")
    return float(beta / gamma)


def calculate_attack_rate(results: pd.DataFrame) -> float:
    """Calculate final attack rate (proportion ultimately infected).

    The attack rate is the fraction of the population that was ever infected
    (moved through I compartment) over the course of the epidemic.

    **Formula:**
    Attack Rate = R(∞) = 1 - S(∞)

    Where S(∞) is the limiting susceptible fraction at end of observation.

    Args:
        results: Simulation results DataFrame from run_simulation().

    Returns:
        float: Attack rate in [0, 1].
    """
    final_recovered = float(results["R"].iloc[-1])
    return final_recovered


def calculate_epidemic_duration(results: pd.DataFrame, threshold: float = 0.001) -> float:
    """Estimate duration of epidemic (time until I below threshold).

    **Definition:**
    Epidemic is "over" when infectious individuals drop below threshold fraction.
    Typical thresholds: 0.001 (0.1%) or 0.01 (1%).

    Args:
        results: Simulation results DataFrame.
        threshold: Proportion of I below which epidemic is considered over (default 0.001).

    Returns:
        float: Time (in days) when I(t) drops permanently below threshold.
                Returns the final time if threshold never reached.
    """
    i_values = results["I"].values
    times = results["t"].values

    # Find where I drops below threshold and stays below
    below_threshold = i_values < threshold
    if np.any(below_threshold):
        idx = np.argmax(below_threshold)
        return float(times[idx])
    return float(times[-1])


def calculate_peak_metrics(results: pd.DataFrame) -> Dict[str, float]:
    """Calculate peak infection statistics.

    Returns:
        Dict with keys:
            - peak_infection: Maximum fraction infected
            - time_to_peak: Time when peak occurs
            - peak_susceptible: Minimum fraction susceptible
    """
    peak_idx = int(results["I"].idxmax())
    return {
        "peak_infection": float(results.loc[peak_idx, "I"]),
        "time_to_peak": float(results.loc[peak_idx, "t"]),
        "peak_susceptible": float(results.loc[peak_idx, "S"]),
    }


def parameter_sensitivity_analysis(
    base_beta: float = 0.28,
    base_sigma: float = 0.18,
    base_gamma: float = 0.10,
    variation: float = 0.2,
    days: int = 180,
    population_size: int = 1000,
) -> pd.DataFrame:
    """Perform sensitivity analysis by varying each parameter ±variation.

    Tests how sensitive model outputs are to parameter changes.
    Helps identify which parameters most influence epidemic trajectory.

    **Methodology:**
    For each parameter θ:
    1. Vary θ by ±variation % from baseline
    2. Run simulation
    3. Compute metrics (R₀, peak, attack rate)
    4. Calculate sensitivity = (output_high - output_low) / output_base

    **Interpretation:**
    - Sensitivity > 1: Output changes more than parameter changes (high sensitivity)
    - Sensitivity < 1: Output changes less than parameter changes (low sensitivity)
    - Sensitivity can be negative if output decreases when parameter increases

    Args:
        base_beta: Baseline exposure rate.
        base_sigma: Baseline adoption rate.
        base_gamma: Baseline recovery rate.
        variation: Fractional change for sensitivity (default 0.2 = ±20%).
        days: Simulation duration.
        population_size: Population for experiments (smaller = faster).

    Returns:
        pd.DataFrame: Sensitivity table with columns:
            [Parameter, BaselineValue, Plus%, Minus%, Sensitivity_Peak,
             Sensitivity_AttackRate, Sensitivity_R0]
    """
    results_list = []

    # Baseline
    base_sim = run_simulation(beta=base_beta, sigma=base_sigma, gamma=base_gamma, days=days, time_steps=int(days*10)+1)
    base_peak = base_sim["I"].max()
    base_attack_rate = calculate_attack_rate(base_sim)
    base_r0 = calculate_r0(base_beta, base_gamma)

    parameters = {
        "β (exposure)": ("beta", base_beta),
        "σ (adoption)": ("sigma", base_sigma),
        "γ (recovery)": ("gamma", base_gamma),
    }

    for param_name, (param_key, base_val) in parameters.items():
        high_val = base_val * (1 + variation)
        low_val = base_val * (1 - variation)

        # High variation
        kwargs_high = {
            "beta": high_val if param_key == "beta" else base_beta,
            "sigma": high_val if param_key == "sigma" else base_sigma,
            "gamma": high_val if param_key == "gamma" else base_gamma,
            "days": days,
            "time_steps": int(days*10)+1,
        }
        sim_high = run_simulation(**kwargs_high)
        peak_high = sim_high["I"].max()
        attack_high = calculate_attack_rate(sim_high)
        r0_high = calculate_r0(
            kwargs_high["beta"] if param_key != "gamma" else base_beta,
            kwargs_high["gamma"],
        )

        # Low variation
        kwargs_low = {
            "beta": low_val if param_key == "beta" else base_beta,
            "sigma": low_val if param_key == "sigma" else base_sigma,
            "gamma": low_val if param_key == "gamma" else base_gamma,
            "days": days,
            "time_steps": int(days*10)+1,
        }
        sim_low = run_simulation(**kwargs_low)
        peak_low = sim_low["I"].max()
        attack_low = calculate_attack_rate(sim_low)
        r0_low = calculate_r0(
            kwargs_low["beta"] if param_key != "gamma" else base_beta,
            kwargs_low["gamma"],
        )

        # Sensitivity = (high - low) / (2 * variation * base)
        # This normalizes for the magnitude of change
        if base_peak > 0:
            sens_peak = (peak_high - peak_low) / (2 * variation * base_val) / base_peak if base_val > 0 else 0
        else:
            sens_peak = 0

        if base_attack_rate > 0:
            sens_attack = (attack_high - attack_low) / (2 * variation * base_val) / base_attack_rate if base_val > 0 else 0
        else:
            sens_attack = 0

        if base_r0 > 0:
            sens_r0 = (r0_high - r0_low) / (2 * variation * base_val) / base_r0 if base_val > 0 else 0
        else:
            sens_r0 = 0

        results_list.append({
            "Parameter": param_name,
            "Baseline": f"{base_val:.4f}",
            "+20% Value": f"{high_val:.4f}",
            "-20% Value": f"{low_val:.4f}",
            "Peak Infection @ +20%": f"{peak_high:.4f}",
            "Peak Infection @ -20%": f"{peak_low:.4f}",
            "Sensitivity (Peak)": f"{sens_peak:.3f}",
            "Sensitivity (Attack Rate)": f"{sens_attack:.3f}",
            "Sensitivity (R₀)": f"{sens_r0:.3f}",
        })

    return pd.DataFrame(results_list)


def intervention_effectiveness(
    baseline_results: pd.DataFrame,
    intervention_results: List[pd.DataFrame],
    intervention_names: List[str],
) -> pd.DataFrame:
    """Compare intervention effectiveness against baseline.

    Args:
        baseline_results: Simulation results without intervention.
        intervention_results: List of simulation results with interventions.
        intervention_names: Names of interventions.

    Returns:
        pd.DataFrame: Effectiveness metrics for each intervention.
    """
    baseline_peak = baseline_results["I"].max()
    baseline_attack = calculate_attack_rate(baseline_results)
    baseline_duration = calculate_epidemic_duration(baseline_results)

    metrics = []
    for inv_results, inv_name in zip(intervention_results, intervention_names):
        inv_peak = inv_results["I"].max()
        inv_attack = calculate_attack_rate(inv_results)
        inv_duration = calculate_epidemic_duration(inv_results)

        peak_reduction = ((baseline_peak - inv_peak) / baseline_peak) * 100 if baseline_peak > 0 else 0
        attack_reduction = ((baseline_attack - inv_attack) / baseline_attack) * 100 if baseline_attack > 0 else 0
        duration_reduction = ((baseline_duration - inv_duration) / baseline_duration) * 100 if baseline_duration > 0 else 0

        metrics.append({
            "Intervention": inv_name,
            "Peak Reduction (%)": f"{peak_reduction:.1f}%",
            "Attack Rate Reduction (%)": f"{attack_reduction:.1f}%",
            "Duration Reduction (%)": f"{duration_reduction:.1f}%",
            "Final Peak": f"{inv_peak:.4f}",
            "Final Attack Rate": f"{inv_attack:.4f}",
        })

    return pd.DataFrame(metrics)
