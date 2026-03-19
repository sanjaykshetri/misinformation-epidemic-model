"""Advanced visualization module for academic paper-quality plots.

This module provides publication-ready visualizations for SEIR model analysis,
including sensitivity heatmaps, confidence intervals, and comparative analyses.

All plots follow academic standards:
- 300+ DPI for publication
- Publication-quality color palettes
- Clear axis labels with units
- Proper typography and spacing
"""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import gaussian_kde


# Publication-quality style settings
PUBLICATION_STYLE = {
    "figure.dpi": 100,
    "savefig.dpi": 300,
    "font.size": 11,
    "font.family": "sans-serif",
    "axes.labelsize": 12,
    "axes.titlesize": 14,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "lines.linewidth": 2.5,
    "axes.linewidth": 1.2,
    "grid.alpha": 0.3,
    "figure.constrained_layout.use": True,
}


def set_publication_style() -> None:
    """Apply publication-quality matplotlib settings."""
    plt.rcParams.update(PUBLICATION_STYLE)
    sns.set_palette("Set2")


def plot_seir(
    results: pd.DataFrame,
    title: str = "SEIR Dynamics of Misinformation",
    save_path: str | None = None,
) -> plt.Axes:
    """Plot S, E, I, R trajectories from a simulation DataFrame.
    
    Args:
        results: DataFrame with columns ['t', 'S', 'E', 'I', 'R']
        title: Plot title
        save_path: Optional path to save figure (publication quality)
    
    Returns:
        Matplotlib axes object
    """
    set_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))

    colors = {"S": "#1f77b4", "E": "#ff7f0e", "I": "#d62728", "R": "#2ca02c"}

    for compartment in ["S", "E", "I", "R"]:
        ax.plot(
            results["t"],
            results[compartment],
            label=compartment,
            linewidth=2.5,
            color=colors[compartment],
        )

    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Time (days)", fontsize=12)
    ax.set_ylabel("Population Fraction", fontsize=12)
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_intervention_comparison(
    experiment_results: list[dict[str, Any]],
    compartment: str = "I",
    title: str | None = None,
    save_path: str | None = None,
) -> plt.Axes:
    """Plot intervention scenarios with styled comparison.
    
    Args:
        experiment_results: List of dicts with 'name' and 'time_series' keys
        compartment: Which compartment to plot ('I', 'R', 'E', 'S')
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    """
    if not experiment_results:
        raise ValueError("experiment_results cannot be empty")

    set_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))

    colors = sns.color_palette("husl", len(experiment_results))

    for i, result in enumerate(experiment_results):
        ts = result["time_series"]
        ax.plot(
            ts["t"],
            ts[compartment],
            linewidth=2.5,
            label=result["name"],
            color=colors[i],
        )

    ax.set_title(title or f"Intervention Comparison: {compartment} Compartment", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Time (days)", fontsize=12)
    ax.set_ylabel("Population Fraction", fontsize=12)
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_sensitivity_heatmap(
    param_ranges: dict[str, np.ndarray],
    metric_fn,
    param_names: list[str] | None = None,
    title: str = "Parameter Sensitivity Analysis",
    save_path: str | None = None,
) -> plt.Axes:
    """Create publication-quality sensitivity heatmap.
    
    Computes a metric across a 2D parameter grid and visualizes as heatmap.
    
    Args:
        param_ranges: Dict like {'beta': np.linspace(...), 'sigma': np.linspace(...)}
                     Must have exactly 2 keys for 2D heatmap
        metric_fn: Function that takes (param_dict) -> float
                  Called at each grid point
        param_names: Optional custom names for parameters
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    
    Example:
        >>> from src.simulation import run_simulation
        >>> def attack_rate(params):
        ...     ts = run_simulation(**params, days=180)
        ...     return ts['R'][-1]
        >>>
        >>> beta_values = np.linspace(0.1, 1.0, 20)
        >>> sigma_values = np.linspace(0.05, 0.5, 20)
        >>> ax = plot_sensitivity_heatmap(
        ...     {'beta': beta_values, 'sigma': sigma_values},
        ...     attack_rate,
        ...     param_names=['β (transmission)', 'σ (adoption)']
        ... )
    """
    set_publication_style()

    param_keys = list(param_ranges.keys())
    if len(param_keys) != 2:
        raise ValueError("Heatmap requires exactly 2 parameters")

    param1_key, param2_key = param_keys
    param1_vals = param_ranges[param1_key]
    param2_vals = param_ranges[param2_key]

    # Compute metric grid
    metric_grid = np.zeros((len(param2_vals), len(param1_vals)))
    for i, p1_val in enumerate(param1_vals):
        for j, p2_val in enumerate(param2_vals):
            params = {param1_key: p1_val, param2_key: p2_val}
            metric_grid[j, i] = metric_fn(params)

    # Create heatmap
    fig, ax = plt.subplots(figsize=(11, 8))
    im = ax.imshow(
        metric_grid,
        aspect="auto",
        origin="lower",
        cmap="RdYlGn_r",
        extent=[param1_vals.min(), param1_vals.max(), param2_vals.min(), param2_vals.max()],
    )

    # Labels
    param1_label = param_names[0] if param_names else param1_key
    param2_label = param_names[1] if param_names else param2_key

    ax.set_xlabel(param1_label, fontsize=12)
    ax.set_ylabel(param2_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)

    # Colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Metric Value", fontsize=11)

    ax.grid(True, alpha=0.2, linestyle="--")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_cascade_distribution(
    fake_cascades: np.ndarray,
    real_cascades: np.ndarray,
    title: str = "Cascade Distribution: Fake vs Real News",
    save_path: str | None = None,
) -> plt.Axes:
    """Plot cascade size distributions with KDE overlay.
    
    Useful for visualizing FakeNewsNet calibration data.
    
    Args:
        fake_cascades: Array of fake news cascade sizes
        real_cascades: Array of real news cascade sizes
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    """
    set_publication_style()
    fig, ax = plt.subplots(figsize=(11, 6))

    # Histograms
    ax.hist(
        fake_cascades,
        bins=40,
        alpha=0.6,
        label=f"Fake News (n={len(fake_cascades)})",
        color="#d62728",
        density=True,
    )
    ax.hist(
        real_cascades,
        bins=40,
        alpha=0.6,
        label=f"Real News (n={len(real_cascades)})",
        color="#2ca02c",
        density=True,
    )

    # KDE overlay
    try:
        fake_kde = gaussian_kde(fake_cascades)
        real_kde = gaussian_kde(real_cascades)
        x_range = np.linspace(
            min(fake_cascades.min(), real_cascades.min()),
            max(fake_cascades.max(), real_cascades.max()),
            200,
        )
        ax.plot(x_range, fake_kde(x_range), color="#d62728", linewidth=2.5, linestyle="--", label="Fake KDE")
        ax.plot(x_range, real_kde(x_range), color="#2ca02c", linewidth=2.5, linestyle="--", label="Real KDE")
    except Exception:
        pass  # KDE may fail with sparse data

    ax.set_xlabel("Cascade Size (# shares)", fontsize=12)
    ax.set_ylabel("Density", fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.3, axis="y")

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_ensemble_trajectories(
    ensemble_results: list[pd.DataFrame],
    compartment: str = "I",
    percentiles: list[int] = [5, 25, 50, 75, 95],
    title: str | None = None,
    save_path: str | None = None,
) -> plt.Axes:
    """Plot ensemble trajectories with confidence bands.
    
    Visualizes uncertainty in model outputs from multiple runs or parameter sets.
    
    Args:
        ensemble_results: List of DataFrames from multiple simulations
        compartment: Which compartment to plot
        percentiles: Percentiles to show as confidence bands
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    
    Example:
        >>> from src.simulation import run_simulation
        >>> # Run model with parameter uncertainty
        >>> results = [run_simulation(**p, days=180) for p in param_list]
        >>> ax = plot_ensemble_trajectories(results, compartment='I')
    """
    set_publication_style()

    # Collect trajectories
    trajectories = np.array([r[compartment].values for r in ensemble_results])
    time = ensemble_results[0]["t"].values

    # Compute percentiles
    percentile_dict = {}
    for p in percentiles:
        percentile_dict[p] = np.percentile(trajectories, p, axis=0)

    fig, ax = plt.subplots(figsize=(11, 6))

    # Draw confidence bands
    colors_bands = ["#fee5d9", "#fcae91", "#fb6a4a", "#cb181d"]
    percentile_pairs = [
        (5, 95, colors_bands[0]),
        (25, 75, colors_bands[1]),
    ]

    for low_p, high_p, color in percentile_pairs:
        ax.fill_between(
            time,
            percentile_dict[low_p],
            percentile_dict[high_p],
            alpha=0.5,
            color=color,
            label=f"{low_p}–{high_p} percentile",
        )

    # Plot median
    ax.plot(
        time,
        percentile_dict[50],
        color="#d62728",
        linewidth=2.5,
        label="Median (50th percentile)",
    )

    ax.set_xlabel("Time (days)", fontsize=12)
    ax.set_ylabel(f"{compartment} Compartment", fontsize=12)
    ax.set_title(
        title or f"Ensemble Uncertainty: {compartment} Trajectory",
        fontsize=14,
        fontweight="bold",
        pad=15,
    )
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_r0_sensitivity(
    base_params: dict[str, float],
    vary_param: str,
    vary_range: np.ndarray,
    title: str | None = None,
    save_path: str | None = None,
) -> plt.Axes:
    """Plot R₀ sensitivity to parameter variation.
    
    Shows how basic reproduction number changes with a single parameter.
    
    Args:
        base_params: Dict with base parameter values
        vary_param: Name of parameter to vary
        vary_range: Array of values for vary_param
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    
    Example:
        >>> from src.analysis import calculate_r0
        >>> base_params = {'beta': 0.5, 'sigma': 0.1, 'gamma': 0.1}
        >>> beta_values = np.linspace(0.1, 1.0, 50)
        >>> ax = plot_r0_sensitivity(base_params, 'beta', beta_values)
    """
    set_publication_style()

    r0_values = []
    for var_val in vary_range:
        params = base_params.copy()
        params[vary_param] = var_val
        r0 = params["beta"] / params["gamma"]  # Simplified R₀
        r0_values.append(r0)

    fig, ax = plt.subplots(figsize=(11, 6))
    ax.plot(vary_range, r0_values, linewidth=2.5, color="#1f77b4", marker="o", markersize=4)

    ax.axhline(y=1.0, color="red", linestyle="--", linewidth=2, label="R₀ = 1 (epidemic threshold)")
    ax.fill_between(vary_range, 0, 1.0, alpha=0.1, color="green", label="R₀ < 1 (controlled)")
    ax.fill_between(vary_range, 1.0, ax.get_ylim()[1], alpha=0.1, color="red", label="R₀ > 1 (epidemic)")

    ax.set_xlabel(f"{vary_param}", fontsize=12)
    ax.set_ylabel("Basic Reproduction Number (R₀)", fontsize=12)
    ax.set_title(title or f"R₀ Sensitivity to {vary_param}", fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="best", framealpha=0.95)
    ax.grid(True, alpha=0.3)

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax


def plot_parameter_impact(
    param_dict: dict[str, list[float]],
    metric_label: str,
    title: str = "Parameter Impact Analysis",
    save_path: str | None = None,
) -> plt.Axes:
    """Bar plot comparing metric across parameter variations.
    
    Args:
        param_dict: Dict where keys are parameter names, values are [metric_values]
        metric_label: Label for the metric (e.g., "Attack Rate (%)")
        title: Plot title
        save_path: Optional path to save figure
    
    Returns:
        Matplotlib axes object
    """
    set_publication_style()

    fig, ax = plt.subplots(figsize=(11, 6))

    names = list(param_dict.keys())
    means = [np.mean(v) for v in param_dict.values()]
    stds = [np.std(v) for v in param_dict.values()]

    colors = sns.color_palette("husl", len(names))
    bars = ax.bar(names, means, yerr=stds, capsize=10, color=colors, alpha=0.8, edgecolor="black", linewidth=1.5)

    ax.set_ylabel(metric_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=15)
    ax.grid(True, alpha=0.3, axis="y")

    # Add value labels on bars
    for bar, mean in zip(bars, means):
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2.0,
            height,
            f"{mean:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")

    return ax
