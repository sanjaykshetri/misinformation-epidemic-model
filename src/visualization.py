"""Plotting helpers for misinformation SEIR simulations."""

from __future__ import annotations

from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


def plot_seir(results: pd.DataFrame, title: str = "SEIR Dynamics of Misinformation"):
    """Plot S, E, I, R trajectories from a simulation DataFrame."""
    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    for compartment in ["S", "E", "I", "R"]:
        ax.plot(results["t"], results[compartment], label=compartment, linewidth=2)

    ax.set_title(title)
    ax.set_xlabel("Time")
    ax.set_ylabel("Population Fraction")
    ax.legend()
    fig.tight_layout()
    return ax


def plot_intervention_comparison(
    experiment_results: list[dict[str, Any]],
    compartment: str = "I",
    title: str | None = None,
):
    """Plot one compartment trajectory across multiple intervention scenarios."""
    if not experiment_results:
        raise ValueError("experiment_results cannot be empty")

    sns.set_theme(style="whitegrid")
    fig, ax = plt.subplots(figsize=(10, 6))

    for result in experiment_results:
        ts = result["time_series"]
        ax.plot(ts["t"], ts[compartment], linewidth=2, label=result["name"])

    ax.set_title(title or f"Intervention Comparison ({compartment})")
    ax.set_xlabel("Time")
    ax.set_ylabel("Population Fraction")
    ax.legend()
    fig.tight_layout()
    return ax
