"""Misinformation epidemic model package.

This package implements a deterministic SEIR model for studying misinformation spread
with cognitive and behavioral heterogeneity.

**Core Components:**
- model: SEIR differential equations
- population: Synthetic population generation
- simulation: ODE solver and parameter mapping
- experiments: Intervention scenarios
- analysis: R₀, sensitivity, and epidemiological metrics
- visualization: Plotting utilities

**Quick Start:**
    from src import run_simulation, generate_population, run_all_experiments
    
    # Generate population
    pop = generate_population(5000)
    
    # Run simulation
    results = run_simulation(days=180)
    
    # Run intervention experiments
    scenarios = run_all_experiments()
"""

from .analysis import (
    calculate_r0,
    calculate_attack_rate,
    calculate_epidemic_duration,
    parameter_sensitivity_analysis,
    intervention_effectiveness,
)
from .calibration import (
    estimate_gamma_from_debunk_times,
    estimate_beta_from_media_exposure_survey,
    validate_population_assumptions,
    calibrated_simulation_config,
    print_calibration_summary,
)
from .experiments import (
    baseline,
    education_intervention,
    increased_recovery,
    reduced_exposure,
    run_all_experiments,
)
from .population import generate_population
from .simulation import run_simulation

__all__ = [
    "baseline",
    "calculate_attack_rate",
    "calculate_epidemic_duration",
    "calculate_r0",
    "education_intervention",
    "generate_population",
    "increased_recovery",
    "intervention_effectiveness",
    "parameter_sensitivity_analysis",
    "reduced_exposure",
    "run_all_experiments",
    "run_simulation",
]
