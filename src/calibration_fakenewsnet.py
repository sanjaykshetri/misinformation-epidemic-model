"""FakeNewsNet dataset calibration for SEIR model parameter inference.

This module provides specialized functions to calibrate model parameters from
FakeNewsNet cascade data (PolitiFact and GossipCop datasets).

The FakeNewsNet datasets contain real misinformation cascades with tweet IDs
showing how news articles spread through social media. This provides ground truth
for transmission rate (β) estimation.

Dataset Structure:
    - politifact_fake.csv / politifact_real.csv: PolitiFact articles
    - gossipcop_fake.csv / gossipcop_real.csv: GossipCop articles
    
    Each CSV has columns:
    - id: Unique identifier
    - url: Article URL
    - title: Article title
    - tweet_ids: Tab-separated list of tweet IDs sharing the article

Type Annotations:
    All functions use Python 3.10+ type hints for clarity.

References:
    Kai Shu et al. "FakeNewsNet: A Data Repository and News Challenge for
    Misinformation Detection in Social Media." arXiv:1811.04928 (2018)
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import pandas as pd


def load_fakenewsnet_csv(csv_path: str) -> pd.DataFrame:
    """Load FakeNewsNet CSV and parse tweet cascade data.
    
    Reads a FakeNewsNet CSV file and converts tab-separated tweet_ids
    into cascade sizes (number of shares).
    
    Args:
        csv_path: Path to FakeNewsNet CSV file (e.g., 'politifact_fake.csv').
                 Expected columns: id, url, title, tweet_ids
    
    Returns:
        DataFrame with columns:
        - id: Article identifier
        - url: Article URL
        - title: Article title
        - tweet_ids_raw: Original tab-separated tweet IDs (str)
        - cascade_size: Number of tweets sharing this article (int)
        - cascade_size_log: log1p-transformed cascade size (float)
    
    Raises:
        FileNotFoundError: If csv_path does not exist
        ValueError: If required columns missing
    
    Example:
        >>> df = load_fakenewsnet_csv('data/politifact_fake.csv')
        >>> print(f"Loaded {len(df)} articles")
        >>> print(f"Mean cascade size: {df['cascade_size'].mean():.1f}")
    """
    try:
        df: pd.DataFrame = pd.read_csv(csv_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    required_cols: set = {"id", "url", "title", "tweet_ids"}
    missing: set = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    
    # Store original tweet_ids
    df["tweet_ids_raw"] = df["tweet_ids"]
    
    # Parse cascade_size: count number of tweet_ids (tab-separated)
    # Handle various formats: NaN, empty string, single ID, tab-separated list
    def parse_cascade_size(tweet_ids_str: str | float) -> int:
        if pd.isna(tweet_ids_str):
            return 0
        if isinstance(tweet_ids_str, (int, float)):
            return int(tweet_ids_str)
        tweet_ids_str = str(tweet_ids_str).strip()
        if not tweet_ids_str:
            return 0
        # Count tab-separated tweet IDs
        return len(tweet_ids_str.split("\t"))
    
    df["cascade_size"] = df["tweet_ids"].apply(parse_cascade_size).astype(int)
    
    # Log-transform for normality (useful for analysis)
    df["cascade_size_log"] = np.log1p(df["cascade_size"]).astype(float)
    
    return df


def compare_fake_vs_real(
    fake_df: pd.DataFrame,
    real_df: pd.DataFrame,
    source_name: str = "Dataset",
) -> dict[str, float]:
    """Compare cascade statistics between fake and real news.
    
    Computes epidemic-relevant statistics comparing fake news spread
    to real news spread. Differences indicate how misinformation propagates
    differently in social networks.
    
    Args:
        fake_df: DataFrame from load_fakenewsnet_csv(...fake.csv)
        real_df: DataFrame from load_fakenewsnet_csv(...real.csv)
        source_name: Name of dataset (e.g., "PolitiFact", "GossipCop")
    
    Returns:
        Dictionary with comparison metrics:
        - fake_mean_cascade: Mean cascade size for fake news
        - real_mean_cascade: Mean cascade size for real news
        - fake_median_cascade: Median cascade size for fake news
        - real_median_cascade: Median cascade size for real news
        - cascade_ratio: fake_mean / real_mean (> 1 means fake spreads more)
        - fake_max_cascade: Maximum cascade size (fake)
        - real_max_cascade: Maximum cascade size (real)
    
    Example:
        >>> politifact_fake = load_fakenewsnet_csv('politifact_fake.csv')
        >>> politifact_real = load_fakenewsnet_csv('politifact_real.csv')
        >>> comp = compare_fake_vs_real(politifact_fake, politifact_real, "PolitiFact")
        >>> print(f"Fake/Real cascade ratio: {comp['cascade_ratio']:.2f}")
    
    Interpretation:
        - cascade_ratio > 1.0: Fake news spreads MORE than real news
        - cascade_ratio < 1.0: Real news spreads MORE than fake news
        - cascade_ratio ≈ 1.0: Similar spread (surprising if observed)
    """
    fake_mean: float = float(fake_df["cascade_size"].mean())
    real_mean: float = float(real_df["cascade_size"].mean())
    
    fake_median: float = float(fake_df["cascade_size"].median())
    real_median: float = float(real_df["cascade_size"].median())
    
    fake_max: int = int(fake_df["cascade_size"].max())
    real_max: int = int(real_df["cascade_size"].max())
    
    # Avoid division by zero
    cascade_ratio: float = fake_mean / real_mean if real_mean > 0 else 0.0
    
    return {
        "fake_mean_cascade": fake_mean,
        "real_mean_cascade": real_mean,
        "fake_median_cascade": fake_median,
        "real_median_cascade": real_median,
        "cascade_ratio": cascade_ratio,
        "fake_max_cascade": fake_max,
        "real_max_cascade": real_max,
    }


def estimate_beta_from_cascade_size(
    cascade_sizes: np.ndarray | list[int],
    max_cascade: int = 10000,
    scale_factor: float = 0.0001,
) -> float:
    """Estimate transmission rate β from cascade size distribution.
    
    Maps observed cascade sizes (number of shares) to transmission rate parameter.
    
    **Biological Model:**
    - Larger cascades indicate faster, more efficient transmission
    - β represents the rate at which susceptible individuals become exposed
    - Linear approximation: β ≈ scale_factor × mean(cascade_sizes)
    
    **Rationale:**
    - Articles with large cascades had high β (many people saw them)
    - Mean cascade size reflects population-level transmission efficiency
    
    Args:
        cascade_sizes: Array of cascade sizes (number of tweet shares per article)
        max_cascade: Cap on cascade size (to handle outliers). Default 10000.
        scale_factor: Empirical scaling constant. Default 0.0001.
                     Adjust based on population size and time horizon.
    
    Returns:
        Transmission rate β ∈ (0, 1) (1/time units, normalized)
    
    Example:
        >>> cascades = np.array([10, 50, 100, 200, 150, 75])
        >>> beta = estimate_beta_from_cascade_size(cascades)
        >>> print(f"β = {beta:.4f}")
        β = 0.0122 (1/per day)
    
    Notes:
        - scale_factor = 0.0001 assumes 10,000-person population, 1-day unit
        - Adjust based on your population and time granularity
        - Cascade size is a PROXY for R (number of people exposed)
    """
    cascade_array: np.ndarray = np.asarray(cascade_sizes, dtype=float)
    
    # Cap outliers
    cascade_array = np.minimum(cascade_array, max_cascade)
    
    mean_cascade: float = float(np.mean(cascade_array))
    
    # Linear scaling: β ∝ cascade size
    beta: float = float(scale_factor * mean_cascade)
    
    # Ensure β is reasonable (0.01 to 1.0 typical range)
    beta = np.clip(beta, 0.01, 1.0)
    
    return beta


def estimate_sigma_from_fake_vs_real(
    fake_cascades: np.ndarray | list[int],
    real_cascades: np.ndarray | list[int],
) -> float:
    """Estimate adoption rate σ from fake vs real news ratio.
    
    The adoption rate σ represents how quickly people believe/share the information.
    If fake news has larger cascades, it suggests faster adoption (higher σ).
    
    **Model:**
    - σ = base_adoption × (fake_cascade_ratio)
    - Fake news adopts faster when cascade_ratio > 1
    
    Args:
        fake_cascades: Array of fake news cascade sizes
        real_cascades: Array of real news cascade sizes
    
    Returns:
        Adoption rate σ ∈ (0, 1) (1/time units)
    
    Example:
        >>> fake = np.array([100, 200, 150])
        >>> real = np.array([50, 80, 90])
        >>> sigma = estimate_sigma_from_fake_vs_real(fake, real)
        >>> print(f"σ = {sigma:.4f}")
    
    Interpretation:
        - Higher σ means faster belief adoption
        - Fake news with σ > real_news_σ suggests rapid adoption
    """
    fake_array: np.ndarray = np.asarray(fake_cascades, dtype=float)
    real_array: np.ndarray = np.asarray(real_cascades, dtype=float)
    
    mean_fake: float = float(np.mean(fake_array))
    mean_real: float = float(np.mean(real_array))
    
    # Ratio of fake-to-real adoption
    cascade_ratio: float = mean_fake / mean_real if mean_real > 0 else 1.0
    
    # Base adoption rate
    base_sigma: float = 0.15
    
    # Scale by cascade ratio
    sigma: float = base_sigma * cascade_ratio
    sigma = float(np.clip(sigma, 0.05, 0.50))
    
    return sigma


def print_fakenewsnet_comparison(
    politifact_fake: pd.DataFrame,
    politifact_real: pd.DataFrame,
    gossipcop_fake: pd.DataFrame | None = None,
    gossipcop_real: pd.DataFrame | None = None,
) -> None:
    """Print formatted comparison of cascade statistics across sources.
    
    Args:
        politifact_fake: Fake news DataFrame from PolitiFact
        politifact_real: Real news DataFrame from PolitiFact
        gossipcop_fake: Fake news DataFrame from GossipCop (optional)
        gossipcop_real: Real news DataFrame from GossipCop (optional)
    """
    print("=" * 100)
    print("FAKENEWSNET CASCADE ANALYSIS")
    print("=" * 100)
    
    # PolitiFact comparison
    print("\n📰 POLITIFACT:")
    print("-" * 100)
    pf_comp = compare_fake_vs_real(politifact_fake, politifact_real, "PolitiFact")
    
    print(f"Fake News (n={len(politifact_fake)}):")
    print(f"  Mean cascade size: {pf_comp['fake_mean_cascade']:.1f} shares/article")
    print(f"  Median cascade size: {pf_comp['fake_median_cascade']:.1f}")
    print(f"  Max cascade size: {pf_comp['fake_max_cascade']}")
    
    print(f"\nReal News (n={len(politifact_real)}):")
    print(f"  Mean cascade size: {pf_comp['real_mean_cascade']:.1f} shares/article")
    print(f"  Median cascade size: {pf_comp['real_median_cascade']:.1f}")
    print(f"  Max cascade size: {pf_comp['real_max_cascade']}")
    
    ratio_str: str = f"{pf_comp['cascade_ratio']:.2f}x"
    print(f"\n⚠️  Fake/Real Cascade Ratio: {ratio_str}")
    if pf_comp['cascade_ratio'] > 1.0:
        pct: float = (pf_comp['cascade_ratio'] - 1) * 100
        print(f"   → Fake news spreads {pct:.1f}% MORE than real news")
    else:
        pct: float = (1 - pf_comp['cascade_ratio']) * 100
        print(f"   → Real news spreads {pct:.1f}% MORE than fake news")
    
    # GossipCop comparison (if provided)
    if gossipcop_fake is not None and gossipcop_real is not None:
        print("\n" + "=" * 100)
        print("🎬 GOSSIPCOP:")
        print("-" * 100)
        gc_comp = compare_fake_vs_real(gossipcop_fake, gossipcop_real, "GossipCop")
        
        print(f"Fake News (n={len(gossipcop_fake)}):")
        print(f"  Mean cascade size: {gc_comp['fake_mean_cascade']:.1f} shares/article")
        print(f"  Median cascade size: {gc_comp['fake_median_cascade']:.1f}")
        print(f"  Max cascade size: {gc_comp['fake_max_cascade']}")
        
        print(f"\nReal News (n={len(gossipcop_real)}):")
        print(f"  Mean cascade size: {gc_comp['real_mean_cascade']:.1f} shares/article")
        print(f"  Median cascade size: {gc_comp['real_median_cascade']:.1f}")
        print(f"  Max cascade size: {gc_comp['real_max_cascade']}")
        
        ratio_str: str = f"{gc_comp['cascade_ratio']:.2f}x"
        print(f"\n⚠️  Fake/Real Cascade Ratio: {ratio_str}")
    
    print("\n" + "=" * 100)


def extract_seir_parameters_from_fakenewsnet(
    fake_cascades: np.ndarray | list[int],
    real_cascades: np.ndarray | list[int],
    gamma: float = 0.10,
) -> dict[str, float]:
    """Extract all SEIR parameters from FakeNewsNet cascade data.
    
    Combines cascade analysis to produce a complete set of parameters
    for run_simulation().
    
    Args:
        fake_cascades: Cascade sizes from fake news articles
        real_cascades: Cascade sizes from real news articles
        gamma: Recovery rate (assumed constant, from fact-check data or default)
    
    Returns:
        Dictionary with SEIR parameters:
        - beta: Transmission rate (from fake news cascade mean)
        - sigma: Adoption rate (from fake/real cascade ratio)
        - gamma: Recovery rate (provided as input)
    
    Example:
        >>> politifact_fake = load_fakenewsnet_csv('politifact_fake.csv')
        >>> politifact_real = load_fakenewsnet_csv('politifact_real.csv')
        >>> params = extract_seir_parameters_from_fakenewsnet(
        ...     politifact_fake['cascade_size'].values,
        ...     politifact_real['cascade_size'].values
        ... )
        >>> from src.simulation import run_simulation
        >>> ts = run_simulation(**params, days=180)
    """
    beta: float = estimate_beta_from_cascade_size(fake_cascades)
    sigma: float = estimate_sigma_from_fake_vs_real(fake_cascades, real_cascades)
    
    return {
        "beta": beta,
        "sigma": sigma,
        "gamma": float(gamma),
    }
