"""Synthetic population generator for misinformation spread experiments.

This module generates realistic synthetic populations with cognitive and media consumption
characteristics for epidemiological modeling.

Key Features:
    - Realistic feature distributions (CRT scores, media exposure hours)
    - Derived susceptibility based on psychological factors
    - Reproducible via seeding for experimental consistency
    
The generated populations serve as baseline features for SEIR parameter inference
via the aggregate_parameters_from_population mapping.
"""

from typing import Optional

import numpy as np
import pandas as pd


def generate_population(n: int, seed: int = 42) -> pd.DataFrame:
    """Generate a synthetic population with cognitive and media features.
    
    Creates a synthetic population with realistic distributions of:
    - Cognitive Reflection Test (CRT) scores: indicator of critical thinking ability
    - Media exposure: daily hours consuming media
    - Susceptibility: susceptibility to misinformation (derived from CRT and media)
    
    These individual-level features are then aggregated to obtain population-level
    SEIR parameters via aggregate_parameters_from_population().
    
    Distribution Specifications:
    
    CRT Score:
        - Uniform on integers {0, 1, 2, 3, 4, 5}
        - Represents 0-5 correct answers on Frederick (2005) test
        - Literature: Mean ≈ 1.6-2.0 in general populations
        
    Media Exposure:
        - Normal distribution: μ = 3.5 hours/day, σ = 1.75 hours/day
        - Clipped to [0, 12] hours/day (valid range)
        - Realistic: US average ≈ 4-5 hours/day according to Pew Research
        
    Susceptibility (derived):
        - Combination of CRT (negatively weighted) and media exposure (positively weighted)
        - Formula: s = 0.65·(5-CRT)/5 + 0.35·media/12, clipped to [0, 1]
        - Interpretation: CRT is more influential (65% vs 35%) in model
    
    Args:
        n: Number of synthetic individuals to generate.
           Typical values: 1000-50000. Default typical: 5000.
        seed: Random seed for numpy.random.default_rng() for reproducibility.
              Same seed always produces same population. Default 42 (arbitrary but fixed).
    
    Returns:
        DataFrame with n rows and columns:
        - id: Unique identifier (1 to n), int64
        - crt_score: Cognitive Reflection Test score ∈ {0, 1, 2, 3, 4, 5}, int64
        - media_exposure: Daily hours consuming media ∈ [0, 12], float64
        - susceptibility: Derived susceptibility ∈ [0, 1], float64
    
    Raises:
        ValueError: If n <= 0 (must be positive).
    
    Example:
        >>> pop = generate_population(n=1000, seed=42)
        >>> print(pop.shape)  # (1000, 4)
        >>> print(pop[['crt_score', 'media_exposure']].describe())
    
    References:
        - Frederick, S. (2005). Cognitive reflection and decision making. 
          Journal of Economic Literature, 42(4), 1-12.
        - Pew Research Center: Media consumption trends in US
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    rng: np.random.Generator = np.random.default_rng(seed)

    crt_score: np.ndarray = rng.integers(0, 6, size=n)
    media_exposure: np.ndarray = np.clip(rng.normal(loc=3.5, scale=1.75, size=n), 0, 12)

    # Lower CRT implies higher susceptibility; higher media exposure increases it.
    crt_component: np.ndarray = (5 - crt_score) / 5
    media_component: np.ndarray = media_exposure / 12
    susceptibility: np.ndarray = np.clip(0.65 * crt_component + 0.35 * media_component, 0, 1)

    return pd.DataFrame(
        {
            "id": np.arange(1, n + 1),
            "crt_score": crt_score,
            "media_exposure": media_exposure,
            "susceptibility": susceptibility,
        }
    )
