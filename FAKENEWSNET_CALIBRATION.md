# FakeNewsNet Calibration Guide

## Overview

This guide explains how to use the **FakeNewsNet dataset** to calibrate SEIR model parameters with real misinformation cascade data.

## Dataset Information

**FakeNewsNet** is a comprehensive benchmark for misinformation detection published by Carnegie Mellon researchers:

- **Paper**: [FakeNewsNet: A Data Repository and News Challenge for Misinformation Detection in Social Media](https://arxiv.org/abs/1811.04928) (Shu et al. 2018)
- **GitHub**: https://github.com/sanjaykshetri/Misinformation-Detection-ML-Model2/tree/main/FakeNewsNet
- **Coverage**: ~36,000 articles across 2 domains with real cascade data

### Dataset Composition

| Domain | Total Articles | Fake | Real | Data |
|--------|---|---|---|---|
| **PolitiFact** | 13,707 | 6,835 | 8,872 | HTML + JSON |
| **GossipCop** | 22,012 | 7,485 | 14,527 | HTML + JSON |

### CSV Format

The calibration pipeline expects CSV files with these columns:
- `id`: Unique article identifier
- `url`: Article URL
- `title`: Article title
- `tweet_ids`: Tab-separated IDs of tweets sharing this article

Example row:
```
id,url,title,tweet_ids
12345,https://politifact.com/...,Claim about X,123\t456\t789\t...
```

## Setup

### Step 1: Get the FakeNewsNet Data

Option A: **Clone the repository**
```bash
cd /path/to/workspace
git clone https://github.com/sanjaykshetri/Misinformation-Detection-ML-Model2
```

Option B: **Use existing local copy** (your case)
```bash
# If already downloaded, copy to misinformation-epidemic-model
cp -r /path/to/Misinformation-Detection-ML-Model2/FakeNewsNet \
      /path/to/misinformation-epidemic-model/data/fakenewsnet
```

### Step 2: Verify CSV Structure

Ensure the FakeNewsNet folder contains:
```
data/fakenewsnet/
  ├── politifact_fake.csv
  ├── politifact_real.csv
  ├── gossipcop_fake.csv
  └── gossipcop_real.csv
```

### Step 3: Run the Calibration Notebook

```python
# Option A: Interactive (recommended)
jupyter notebook notebooks/fakenewsnet_calibration.ipynb

# Option B: Command line
python -c "
from src.calibration_fakenewsnet import load_fakenewsnet_csv
df = load_fakenewsnet_csv('data/fakenewsnet/politifact_fake.csv')
print(f'Loaded {len(df)} articles')
"
```

## API Reference

### Core Functions

#### `load_fakenewsnet_csv(csv_path: str) -> pd.DataFrame`

Load and parse a FakeNewsNet CSV file.

**Args:**
- `csv_path` (str): Path to CSV file

**Returns:**
- DataFrame with columns:
  - `id`, `url`, `title`: Metadata
  - `tweet_ids_raw`: Original tweet IDs
  - `cascade_size`: Number of tweets sharing this article
  - `cascade_size_log`: log₁-transformed cascade size

**Example:**
```python
from src.calibration_fakenewsnet import load_fakenewsnet_csv

pf_fake = load_fakenewsnet_csv('data/fakenewsnet/politifact_fake.csv')
print(f"Mean cascade: {pf_fake['cascade_size'].mean():.1f}")
print(f"Max cascade: {pf_fake['cascade_size'].max()}")
```

---

#### `compare_fake_vs_real(fake_df, real_df, source_name="Dataset") -> dict`

Compare cascade statistics between fake and real news.

**Args:**
- `fake_df` (DataFrame): Fake news DataFrame from `load_fakenewsnet_csv()`
- `real_df` (DataFrame): Real news DataFrame
- `source_name` (str): Name for output (default: "Dataset")

**Returns:**
- Dictionary with metrics:
  - `fake_mean_cascade`, `real_mean_cascade`: Mean cascade size
  - `cascade_ratio`: `fake_mean / real_mean` (>1 = fake spreads more)
  - Other statistics (median, max)

**Example:**
```python
comparison = compare_fake_vs_real(pf_fake, pf_real, "PolitiFact")
print(f"Fake/Real ratio: {comparison['cascade_ratio']:.2f}x")

# Interpretation:
# 1.5x → Fake news spreads 50% MORE than real news
# 0.8x → Real news spreads 20% MORE than fake news
```

---

#### `estimate_beta_from_cascade_size(cascade_sizes, max_cascade=10000, scale_factor=0.0001) -> float`

Estimate SEIR transmission rate β from cascade sizes.

**Args:**
- `cascade_sizes`: Array of cascade sizes
- `max_cascade` (int): Cap on cascade size to handle outliers
- `scale_factor` (float): Empirical scaling constant

**Returns:**
- Transmission rate β ∈ (0, 1)

**Example:**
```python
from src.calibration_fakenewsnet import estimate_beta_from_cascade_size

beta = estimate_beta_from_cascade_size(pf_fake['cascade_size'].values)
print(f"β = {beta:.4f}")
```

**Scale Factor Tuning:**
- Default `0.0001` assumes: 10,000-person population, 1-day time unit
- Adjust based on population size:
  - Larger population → increase scale_factor
  - Smaller population → decrease scale_factor
- Example: 100,000-person population → `scale_factor = 0.001`

---

#### `estimate_sigma_from_fake_vs_real(fake_cascades, real_cascades) -> float`

Estimate SEIR adoption rate σ from fake/real cascade comparison.

**Args:**
- `fake_cascades`: Array of fake news cascade sizes
- `real_cascades`: Array of real news cascade sizes

**Returns:**
- Adoption rate σ ∈ (0, 1)

**Example:**
```python
from src.calibration_fakenewsnet import estimate_sigma_from_fake_vs_real

sigma = estimate_sigma_from_fake_vs_real(
    pf_fake['cascade_size'].values,
    pf_real['cascade_size'].values
)
print(f"σ = {sigma:.4f}")
```

---

#### `extract_seir_parameters_from_fakenewsnet(fake_cascades, real_cascades, gamma=0.10) -> dict`

Extract complete SEIR parameters from FakeNewsNet data.

**Args:**
- `fake_cascades`: Array of fake news cascade sizes
- `real_cascades`: Array of real news cascade sizes
- `gamma` (float): Recovery rate (from fact-check data or default)

**Returns:**
- Dictionary with keys: `beta`, `sigma`, `gamma`

**Example:**
```python
from src.calibration_fakenewsnet import extract_seir_parameters_from_fakenewsnet
from src.simulation import run_simulation

params = extract_seir_parameters_from_fakenewsnet(
    pf_fake['cascade_size'].values,
    pf_real['cascade_size'].values,
    gamma=0.10
)

# Run model with calibrated parameters
results = run_simulation(**params, days=180)
```

---

#### `print_fakenewsnet_comparison(politifact_fake, politifact_real, gossipcop_fake=None, gossipcop_real=None) -> None`

Print formatted comparison across sources.

**Args:**
- `politifact_fake`, `politifact_real`: DataFrames from `load_fakenewsnet_csv()`
- `gossipcop_fake`, `gossipcop_real`: Optional GossipCop DataFrames

**Example:**
```python
from src.calibration_fakenewsnet import print_fakenewsnet_comparison

print_fakenewsnet_comparison(pf_fake, pf_real, gc_fake, gc_real)
```

Output:
```
════════════════════════════════════════════════════════════════════════════════
FAKENEWSNET CASCADE ANALYSIS
════════════════════════════════════════════════════════════════════════════════

📰 POLITIFACT:
────────────────────────────────────────────────────────────────────────────────
Fake News (n=6835):
  Mean cascade size: 156.3 shares/article
  Median cascade size: 42.1
  Max cascade size: 9847

Real News (n=8872):
  Mean cascade size: 89.2 shares/article
  Median cascade size: 18.5
  Max cascade size: 8923

⚠️  Fake/Real Cascade Ratio: 1.75x
   → Fake news spreads 75% MORE than real news
```

## Calibration Workflow

### Quick Start (Recommended)

```python
from src.calibration_fakenewsnet import (
    load_fakenewsnet_csv,
    extract_seir_parameters_from_fakenewsnet,
)
from src.simulation import run_simulation

# 1. Load data
fake = load_fakenewsnet_csv('data/fakenewsnet/politifact_fake.csv')
real = load_fakenewsnet_csv('data/fakenewsnet/politifact_real.csv')

# 2. Extract parameters
params = extract_seir_parameters_from_fakenewsnet(
    fake['cascade_size'].values,
    real['cascade_size'].values,
    gamma=0.10
)

# 3. Run model
results = run_simulation(**params, days=180, population=10000)

# 4. Analyze
print(f"Peak infected: {results['I'].max():.0f}")
print(f"Attack rate: {100 * results['R'][-1] / 10000:.1f}%")
```

### Advanced: Custom Scale Factor

```python
from src.calibration_fakenewsnet import (
    estimate_beta_from_cascade_size,
    estimate_sigma_from_fake_vs_real,
)

# Use population-specific scale factor
population = 50000
scale_factor = 0.0005  # Increased for larger population

beta = estimate_beta_from_cascade_size(
    fake['cascade_size'].values,
    scale_factor=scale_factor
)
sigma = estimate_sigma_from_fake_vs_real(
    fake['cascade_size'].values,
    real['cascade_size'].values
)
```

## Understanding the Results

### Cascade Ratio Interpretation

- **cascade_ratio > 1.0**: Fake news spreads MORE than real news
  - Suggests: Misinformation is more contagious
  - Model implication: Higher β, higher σ needed

- **cascade_ratio ≈ 1.0**: Similar spread rates (rare in practice)
  - Suggests: Fake and real news equally contagious
  - Model implication: Baseline parameters may be adequate

- **cascade_ratio < 1.0**: Real news spreads MORE than fake news (unusual)
  - Suggests: Misinformation has natural resistance
  - Model implication: Lower transmission coefficients

### Parameter Meanings

| Parameter | Range | Meaning | Typical Value |
|-----------|-------|---------|---|
| **β** | (0.01, 1.0) | Transmission rate | 0.3-0.5 |
| **σ** | (0.05, 0.50) | Adoption rate (E→I) | 0.10-0.25 |
| **γ** | (0.05, 0.20) | Recovery rate (I→R) | 0.10 |

## Caveats and Limitations

1. **Cascade Size ≠ True Infections**
   - Tweet count is a proxy for information exposure
   - Not all reaches result in belief adoption
   - Scale factor is empirical and needs tuning

2. **Temporal Dynamics**
   - FakeNewsNet cascades occur over weeks/months
   - SEIR model assumes days
   - Cascade times should be normalized to consistent units

3. **Bot Activity and Bots**
   - Social media cascades may include automated sharing
   - Affects cascade size estimates
   - Consider bot filtering in preprocessing

4. **Selection Bias**
   - Dataset focuses on fact-checkable claims
   - May not represent all misinformation types
   - Results specific to PolitiFact/GossipCop domains

5. **Network Structure**
   - SEIR assumes homogeneous mixing
   - Real social networks have clustering, assortativity
   - Model may underestimate or overestimate spread

## Validation

### Cross-Domain Validation

Compare parameters extracted from multiple sources:

```python
# PolitiFact vs GossipCop
pf_params = extract_seir_parameters_from_fakenewsnet(
    pf_fake['cascade_size'].values,
    pf_real['cascade_size'].values
)

gc_params = extract_seir_parameters_from_fakenewsnet(
    gc_fake['cascade_size'].values,
    gc_real['cascade_size'].values
)

# Should be similar
print(f"PolitiFact β: {pf_params['beta']:.4f}")
print(f"GossipCop β:  {gc_params['beta']:.4f}")
print(f"Difference: {abs(pf_params['beta'] - gc_params['beta']):.4f}")
```

### Sensitivity Analysis

Test parameter robustness:

```python
from src.analysis import parameter_sensitivity_analysis

# Vary β ±20%
base_params = params.copy()
for beta_mult in [0.8, 0.9, 1.0, 1.1, 1.2]:
    params['beta'] = base_params['beta'] * beta_mult
    results = run_simulation(**params, days=180)
    attack_rate = 100 * results['R'][-1] / 10000
    print(f"β × {beta_mult:.1f}: Attack rate = {attack_rate:.1f}%")
```

## References

- Shu et al. (2018): [FakeNewsNet: A Data Repository for Misinformation Detection](https://arxiv.org/abs/1811.04928)
- Vosoughi et al. (2018): [The Spread of True and False News Online](https://science.sciencemag.org/content/359/6380/1146)
- Sunstein (2002): [The Law of Group Polarization](https://ssrn.com/abstract=297181)

## Support

For issues or questions:
1. Check the Jupyter notebook: `notebooks/fakenewsnet_calibration.ipynb`
2. Review docstrings: `help(load_fakenewsnet_csv)`
3. See full module: `src/calibration_fakenewsnet.py`
