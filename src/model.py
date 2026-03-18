"""Core SEIR model equations for misinformation diffusion.

Implements the deterministic SEIR (Susceptible-Exposed-Infected-Recovered) compartmental model
for misinformation spread as an infectious process.

Mathematical Model:
    dS/dt = -β·S·I  (susceptible exposed)
    dE/dt = β·S·I - σ·E  (exposed to infected)
    dI/dt = σ·E - γ·I  (infected to recovered)
    dR/dt = γ·I  (cumulative recovered)

Key Parameters:
    β (beta): Exposure rate [1/time]
    σ (sigma): Adoption rate [1/time]
    γ (gamma): Recovery rate [1/time]

Assumptions:
    1. Well-mixed population (homogeneous contacts)
    2. Exponential transition rates (memoryless)
    3. No demographics (births/deaths negligible)
    4. Recovered individuals cannot be reinfected

References:
    Kermack, W. O., & McKendrick, A. G. (1927). A contribution to the mathematical theory
    of epidemics. Proceedings of the Royal Society A, 115(772), 700–721.
"""

from typing import List, Sequence


def seir_model(
    y: Sequence[float],
    t: float,
    beta: float,
    sigma: float,
    gamma: float,
) -> List[float]:
    """Compute time derivatives for the SEIR system.

    Implements the ODE system for use with scipy.integrate.odeint.

    Mathematical Form:
        dS/dt = -β·S·I
        dE/dt = β·S·I - σ·E
        dI/dt = σ·E - γ·I
        dR/dt = γ·I

    Population Conservation:
        d(S+E+I+R)/dt = 0 at all times.

    Args:
        y: Current state [S, E, I, R] where each value ∈ [0, 1].
        t: Current time in days (unused, required for ODE solver).
        beta: Exposure rate (β > 0) in 1/time units.
        sigma: Progression rate (σ > 0) in 1/time units.
        gamma: Recovery rate (γ > 0) in 1/time units.

    Returns:
        List[float]: Derivatives [dS/dt, dE/dt, dI/dt, dR/dt].
    """
    s: float
    e: float
    i: float
    r: float
    s, e, i, r = y

    d_sdt: float = -beta * s * i
    d_edt: float = beta * s * i - sigma * e
    d_idt: float = sigma * e - gamma * i
    d_rdt: float = gamma * i

    return [d_sdt, d_edt, d_idt, d_rdt]
