# Modeling the Spread of Misinformation as an Infectious Process

This project implements a deterministic SEIR (Susceptible, Exposed, Infected, Recovered) model to simulate population-level spread of misinformation.

The pipeline combines:

- Mechanistic modeling (ODE-based SEIR dynamics)
- Synthetic population generation
- Behavioral and cognitive features (CRT score, media exposure)
- Intervention experiments and visualization

The goal is to provide a reproducible, interpretable modeling framework for understanding misinformation dynamics.

## Core Objectives

- Implement deterministic SEIR dynamics with differential equations
- Simulate misinformation spread through time
- Incorporate heterogeneity via:
  - Cognitive Reflection Test (CRT) score
  - Social media exposure
- Generate a synthetic population dataset
- Evaluate interventions by modifying model parameters:
  - Reduce exposure rate (beta)
  - Reduce adoption rate (sigma)
  - Increase recovery rate (gamma)
- Compare intervention outcomes using summary metrics and plots

## Model Specification

Compartments:

- `S`: Susceptible (unaware)
- `E`: Exposed (seen misinformation)
- `I`: Infected (believes misinformation)
- `R`: Recovered (corrected/resistant)

Governing equations:

- `dS/dt = -beta * S * I`
- `dE/dt = beta * S * I - sigma * E`
- `dI/dt = sigma * E - gamma * I`
- `dR/dt = gamma * I`

Parameters:

- `beta`: exposure rate
- `sigma`: adoption rate
- `gamma`: recovery rate

## Project Structure

```text
misinformation-epidemic-model/
|
|- data/
|  ├── .gitkeep
|  └── (generated CSV outputs)
|
|- src/
|  ├── __init__.py
|  ├── model.py
|  ├── simulation.py
|  ├── population.py
|  ├── experiments.py
|  ├── visualization.py
|  └── cli.py
|
|- tests/
|  ├── conftest.py
|  ├── test_model.py
|  ├── test_simulation.py
|  ├── test_population.py
|  └── test_experiments.py
|
|- notebooks/
|  ├── .gitkeep
|  └── baseline_vs_interventions.ipynb
|
|- reports/
|  ├── .gitkeep
|  └── (generated plots)
|
|- requirements.txt
|- README.md
```

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

Run baseline simulation:

```python
from src.simulation import run_simulation

results = run_simulation()
print(results.head())
```

Generate synthetic population:

```python
from src.population import generate_population

population = generate_population(1000)
print(population.head())
```

Run all intervention experiments:

```python
from src.experiments import run_all_experiments

scenarios = run_all_experiments(population_size=10000)
for scenario in scenarios:
    print(scenario["name"], scenario["metrics"])
```

Plot SEIR trajectories:

```python
from src.simulation import run_simulation
from src.visualization import plot_seir

results = run_simulation()
ax = plot_seir(results)
```

Compare intervention scenarios:

```python
from src.experiments import run_all_experiments
from src.visualization import plot_intervention_comparison

scenarios = run_all_experiments()
ax = plot_intervention_comparison(scenarios, compartment="I")
```

## Running Experiments via CLI

The command-line interface provides a convenient way to run all experiments and automatically generate outputs:

```bash
python -m src.cli --population-size 10000 --days 180
```

Options:

- `--population-size`: Number of synthetic individuals (default: 10000)
- `--days`: Simulation duration in days (default: 180)
- `--gamma`: Recovery rate (default: 0.10)
- `--data-dir`: Output directory for CSV files (default: `data/`)
- `--report-dir`: Output directory for plots (default: `reports/`)
- `--no-plots`: Skip plot generation

Example output:

```bash
$ python -m src.cli --population-size 5000 --days 180

Running experiments with population_size=5000, days=180, gamma=0.1...
✓ Saved time series: data/baseline_timeseries.csv
✓ Saved metrics: data/baseline_metrics.txt
✓ Saved comparison plot (I): reports/intervention_comparison_I.png
✓ Saved individual plot: reports/baseline_seir.png
...
```

The CLI generates:

- **CSV time series** for each scenario (`S`, `E`, `I`, `R` compartments)
- **Metrics summaries** (peak infection, time-to-peak, burden)
- **PNG plots** comparing scenarios and individual SEIR trajectories

## Running Unit Tests

Comprehensive tests cover model equations, parameter mapping, population generation, and experiment scenarios.

Run all tests:

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_model.py -v
```

Run tests with coverage:

```bash
pytest tests/ --cov=src --cov-report=html
```

Test coverage includes:

- **46 unit tests** covering:
  - SEIR differential equations conservation and dynamics
  - Population generation and feature distributions
  - Parameter mapping and simulation configuration
  - Baseline and intervention scenario validation
  - Summary metrics computation

## Interactive Notebook

Explore the model visually with a comprehensive Jupyter notebook:

```bash
jupyter notebook notebooks/baseline_vs_interventions.ipynb
```

The notebook includes:

1. **Population visualization**: Distributions of CRT scores, media exposure, and susceptibility
2. **Experiment execution**: Run all four scenarios with configurable population size and duration
3. **SEIR dynamics plots**: Visualize compartment trajectories over time
4. **Intervention comparison**: Side-by-side plots of infection curves across scenarios
5. **Effectiveness analysis**: Quantitative reduction in peak infection and disease burden
6. **Key insights**: Interpretation and implications of model findings

The notebook is self-contained and provides a complete walkthrough from population generation through intervention effectiveness assessment.

## Parameter Mapping

Population features are mapped to model parameters in `src/simulation.py`:

- `beta = f(media_exposure)` where higher exposure increases `beta`
- `sigma = f(crt_score)` where higher CRT lowers `sigma`
- `gamma` is constant by default but can be modified by interventions

## Experiments Included

Implemented in `src/experiments.py`:

- `baseline()`
- `reduced_exposure()`
- `increased_recovery()`
- `education_intervention()`

Each scenario returns:

- Time-series output (`S`, `E`, `I`, `R`)
- Peak infection and time-to-peak
- Final recovered fraction and infection burden summary

## Dependencies

- numpy
- pandas
- scipy
- matplotlib
- seaborn

## Future Extensions

- Network-based diffusion models
- Agent-based simulation
- Calibration against empirical datasets
- Bayesian parameter estimation

## Design Philosophy

This project prioritizes:

- Clarity over complexity
- Reproducibility
- Interpretability

The objective is not only prediction, but understanding system behavior and intervention leverage points.

---

## Documentation & References

### Project Documentation

- **[METHODOLOGY.md](METHODOLOGY.md)** – Complete mathematical foundations
  - ODE system derivation and parameter definitions
  - Model assumptions with validity discussion
  - Sensitivity analysis methodology
  - Parameter estimation techniques
  - Extensions and limitations
  - Full bibliography of scientific references
  
- **[MODEL_ASSUMPTIONS.md](MODEL_ASSUMPTIONS.md)** – Quick reference guide
  - 8 core model assumptions
  - When assumptions are valid/invalid
  - Real-world impact of each assumption
  - Validation checklist
  - Parameter sensitivity ranking

### Academic References

#### Epidemiological Modeling

1. **Kermack, W. O., & McKendrick, A. G.** (1927). "A contribution to the mathematical theory of epidemics." *Proceedings of the Royal Society of London*, 115(772), 700–721. [Foundational SEIR model]

2. **Anderson, R. M., & May, R. M.** (1991). *Infectious Diseases of Humans: Dynamics and Control*. Oxford University Press. [Mathematical epidemiology textbook]

3. **Vynnycky, E., & White, R.** (2010). *An Introduction to Infectious Disease Modelling*. Oxford University Press. [Applied mathematical epidemiology]

4. **Keeling, M. J., & Rohani, P.** (2008). *Modeling Infectious Diseases in the Context of Global Health*. Blackwell Publishing. [Networks and stochasticity]

#### Misinformation Dynamics

5. **Vosoughi, S., Roy, D., & Aral, S.** (2018). "The spread of true and false news online." *Science*, 359(6380), 1146–1151. [Empirical misinformation spread on Twitter]

6. **Broniatowski, D. A., Jamison, A. M., Qi, S., et al.** (2018). "Weaponized health communication: Twitter bots and Russian trolls amplifying the vaccine autism hypothesis." *American Journal of Public Health*, 108(10), 1378–1384. [Misinformation coordination]

7. **Del Vicario, M., Bessi, A., Zollo, F., et al.** (2016). "The spreading of misinformation by social bots." *Communications Physics*, 1(1), 90. [Network spread analysis]

#### Cognitive Science & Critical Thinking

8. **Frederick, S.** (2005). "Cognitive reflection and decision making." *Journal of Economic Literature*, 42(4), 1–12. [CRT development and validation; used in population model]

9. **Pennycook, G., & Rand, D. G.** (2021). "The psychology of fake news." *Trends in Cognitive Sciences*, 25(5), 388–402. [Belief adoption mechanisms]

10. **Lewandowsky, S., Ecker, U. K., & Cook, J.** (2017). "Beyond misinformation: Understanding and coping with the "post-truth" era." *Journal of Applied Research in Memory and Cognition*, 6(4), 353–369. [Corrections and cognitive mechanisms]

### Model Innovations

This project extends standard epidemiological SEIR models to information contexts by:

- **Mapping psychological factors** (CRT scores, media exposure) to epidemiological parameters
- **Quantifying intervention mechanisms** (exposure reduction, recovery acceleration, education)
- **Computing sensitivity metrics** to identify high-leverage intervention targets
- **Validating against compartmental constraints** (population conservation)

See METHODOLOGY.md Section 3 (Key Assumptions) and Section 8 (Epidemiological Metrics) for theoretical justification.

### Technical Implementation Notes

- **Language**: Python 3.12
- **ODE Solver**: `scipy.integrate.odeint` (Adams method, RK45 fallback)
- **Type Hints**: Full PEP 484 compliance with explicit annotations
- **Testing**: 46 unit tests covering dynamics, parameters, and scenarios
- **Visualization**: Matplotlib/Seaborn with publication-quality formatting

### Reproducibility

All results are reproducible via:
- Fixed random seed (42) in population generation
- Deterministic ODE solver settings
- CI/CD testing on each commit
- Version-pinned dependencies (see `requirements.txt`)

---

## New Analysis Tools (v2.0)

For stronger academic rigor, this version adds:

### New Analysis Module: `src/analysis.py`

- **`calculate_r0(beta, gamma)`** – Basic reproduction number
- **`calculate_attack_rate(results)`** – Final proportion infected
- **`calculate_epidemic_duration(results, threshold)`** – Time to elimination
- **`parameter_sensitivity_analysis(...)`** – ±20% parameter variation impact
- **`intervention_effectiveness(...)`** – Quantitative comparison of strategies

### New Notebook: `notebooks/academic_analysis.ipynb`

Interactive demonstration of:
1. R₀ calculation for each scenario
2. Sensitivity analysis with elasticity metrics
3. Epidemiological metrics summary
4. Visual comparison of all interventions
5. Key findings and policy implications

---

## Using This Project for Research/Employment

### For Hiring Managers

This portfolio demonstrates:
- **Mathematical rigor**: Compartmental ODE modeling with solid theoretical foundation
- **Python proficiency**: Type hints, idiomatic code, comprehensive testing
- **Domain expertise**: Epidemiological modeling, sensitivity analysis, parameter inference
- **Communication**: Clear documentation linking code to underlying mathematics
- **Empirical mindset**: Validation testing and sensitivity analysis built-in

See `METHODOLOGY.md` and `MODEL_ASSUMPTIONS.md` for evidence of thoughtful, nuanced modeling.

### For Researchers

This codebase provides:
- **Extensible framework**: Easy to add network effects, stochasticity, or new interventions
- **Calibration pipeline**: Synthetic population → parameter inference → validation
- **Reproducible toolkit**: Fixed seeds, deterministic solvers, CI/CD testing
- **Academic foundations**: All assumptions and limitations explicitly documented

See Section 11 of `METHODOLOGY.md` for suggested extensions (network SEIR, agent-based, Bayesian inference).

### For Educators

This project illustrates:
- **Applied mathematical modeling**: From real-world problem to ODE system
- **Interdisciplinary thinking**: Epidemiology + psychology + information science
- **Model validation**: Sensitivity analysis, assumption checking, limitation discussion
- **Best practices**: Type hints, comprehensive docstrings, unit tests, documentation

Use the Jupyter notebooks as teaching material for dynamical systems or public health informatics courses.
