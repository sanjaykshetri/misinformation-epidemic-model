"""Command-line interface for running misinformation SEIR experiments."""

import argparse
from pathlib import Path

import pandas as pd

from .experiments import run_all_experiments
from .visualization import plot_intervention_comparison, plot_seir


def main():
    """Run experiments and save outputs to data/ and reports/ directories."""
    parser = argparse.ArgumentParser(
        description="Run misinformation SEIR model experiments and save outputs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--population-size",
        type=int,
        default=10000,
        help="Number of synthetic individuals to simulate.",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=180,
        help="Number of simulation days.",
    )
    parser.add_argument(
        "--gamma",
        type=float,
        default=0.10,
        help="Recovery rate (default: 0.10).",
    )
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data"),
        help="Output directory for CSV data files.",
    )
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports"),
        help="Output directory for plots.",
    )
    parser.add_argument(
        "--no-plots",
        action="store_true",
        help="Skip plot generation.",
    )

    args = parser.parse_args()

    # Create output directories if they don't exist
    args.data_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    print(f"Running experiments with population_size={args.population_size}, days={args.days}, gamma={args.gamma}...")
    scenarios = run_all_experiments(
        population_size=args.population_size,
        gamma=args.gamma,
        days=args.days,
    )

    # Save time series and metrics for each scenario
    for scenario in scenarios:
        name = scenario["name"]
        ts = scenario["time_series"]
        metrics = scenario["metrics"]

        # Save CSV
        csv_path = args.data_dir / f"{name}_timeseries.csv"
        ts.to_csv(csv_path, index=False)
        print(f"✓ Saved time series: {csv_path}")

        # Save metrics as JSON
        metrics_path = args.data_dir / f"{name}_metrics.txt"
        with open(metrics_path, "w") as f:
            f.write(f"Scenario: {name}\n")
            f.write(f"Parameters: {scenario['parameters']}\n")
            f.write("Metrics:\n")
            for key, value in metrics.items():
                f.write(f"  {key}: {value:.6f}\n")
        print(f"✓ Saved metrics: {metrics_path}")

    # Generate plots
    if not args.no_plots:
        # Plot all scenarios together
        fig_path = args.report_dir / "intervention_comparison_I.png"
        ax = plot_intervention_comparison(scenarios, compartment="I")
        ax.figure.savefig(fig_path, dpi=150, bbox_inches="tight")
        print(f"✓ Saved comparison plot (I): {fig_path}")

        fig_path = args.report_dir / "intervention_comparison_E.png"
        ax = plot_intervention_comparison(scenarios, compartment="E")
        ax.figure.savefig(fig_path, dpi=150, bbox_inches="tight")
        print(f"✓ Saved comparison plot (E): {fig_path}")

        # Plot each scenario individually
        for scenario in scenarios:
            fig_path = args.report_dir / f"{scenario['name']}_seir.png"
            ax = plot_seir(scenario["time_series"], title=f"SEIR: {scenario['name'].replace('_', ' ').title()}")
            ax.figure.savefig(fig_path, dpi=150, bbox_inches="tight")
            print(f"✓ Saved individual plot: {fig_path}")

    # Print summary table
    print("\n" + "=" * 80)
    print("EXPERIMENT SUMMARY")
    print("=" * 80)
    summary_data = []
    for scenario in scenarios:
        summary_data.append(
            {
                "Scenario": scenario["name"],
                "Beta": f"{scenario['parameters']['beta']:.4f}",
                "Sigma": f"{scenario['parameters']['sigma']:.4f}",
                "Peak Infection": f"{scenario['metrics']['peak_infection']:.6f}",
                "Time to Peak": f"{scenario['metrics']['time_to_peak']:.1f}",
                "Final Recovered": f"{scenario['metrics']['final_recovered']:.6f}",
            }
        )
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
