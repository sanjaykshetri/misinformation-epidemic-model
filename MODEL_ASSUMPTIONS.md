# SEIR Model Assumptions: Quick Reference

## Core Assumptions

### 1. **Compartmental Structure (S → E → I → R)**
**Assumption:** Individuals pass through distinct states: Susceptible → Exposed (latent) → Infected (actively spreading) → Recovered (immune).

**Rationale:** Misinformation adoption involves belief formation delay (exposure) before active sharing (infected).

**When Valid:** ✅
- Information spread follows predictable state transitions
- Belief formation has latency period
- Recovery reflects fact-checking or skepticism

**When Invalid:** ❌
- Multiple belief systems competing simultaneously
- Belief oscillation (recovered individuals reacquire beliefs)
- Permanent skepticism (not captured as recovery)

---

### 2. **Homogeneous Mixing (Well-Mixed Population)**
**Assumption:** Every infected person is equally likely to contact any susceptible person (mass action principle: contact rate ∝ S·I).

**Formula Implication:** Transmission term = β·S·I (product of compartment sizes).

**Rationale:** Simplifies tractable mathematics; reasonable for average behavior.

**When Valid:** ✅
- Analyzing broad population-level trends
- Homogeneous contact networks (rare but theoretical baseline)
- Early/late stages when prevalence is extreme

**When Invalid:** ❌
- Network structure matters (friend groups, communities, echo chambers)
- Geographic clustering (isolated communities reach information later)
- Selective exposure (people seek out confirming sources)

**Real-World Impact:** Networks can increase R₀ by 30-100% via hubs; this model provides *lower bound* on spread.

---

### 3. **Exponential State Durations**
**Assumption:** Time in each state (E, I) follows exponential distribution with constant rate (σ for E→I, γ for I→R).

**Implication:** Transition probability = rate × dt (memoryless Poisson process).

**Rationale:** Analytically tractable; consistent with chemical reaction kinetics.

**When Valid:** ✅
- Aggregate behavior of heterogeneous underlying processes
- Steady-state dynamics (long time scales)
- Absence of delays or seasonality

**When Invalid:** ❌
- Fixed latency periods (e.g., exactly 5-day incubation)
- Aging effects (older beliefs harder to change)
- Seasonal patterns in media consumption

**Real-World Impact:** Slight model mismatch; sensitivity analysis shows σ and γ are least sensitive parameters (Section 2.4 of METHODOLOGY.md).

---

### 4. **No Reinfection**
**Assumption:** Individuals recovered (R compartment) cannot acquire the same belief again.

**Rationale:** Once corrected, assume skepticism or fact-checking memory persists.

**When Valid:** ✅
- Factual claims (verifiable; correction is permanent)
- Individual skepticism increases after disconfirmation

**When Invalid:** ❌
- Misinformation presented with different framing
- Forgetting effects (corrections fade over months)
- Multiple narratives (people accept different false claims)

**Real-World Impact:** Model OVERESTIMATES epidemic control. Allowing reinfection would increase R₀ and attack rate by ~30%.

---

### 5. **Constant Parameters**
**Assumption:** β, σ, γ remain constant throughout simulation (no time-dependence or intervention dynamics).

**Rationale:** Enables deterministic ODE solution; rapid intervention response unrealistic.

**When Valid:** ✅
- Short-term predictions (weeks)
- Interventions at constant steady-state level
- Absence of learning/adaptation

**When Invalid:** ❌
- Long-term dynamics (population learns over months)
- Adaptive responses (platforms change algorithms in real-time)
- Seasonal or cyclical patterns

**Real-World Impact:** Model valid for 6-month horizons; less accurate for year+ timescales. METHODOLOGY.md Section 8 discusses extensions to time-varying parameters.

---

### 6. **No Vital Dynamics**
**Assumption:** Population size constant (no births, deaths, migration).

**Rationale:** Simplification; epidemics typically fast relative to population turnover.

**When Valid:** ✅
- Acute information crises (weeks to months)
- Constant population size
- No demographic change

**When Invalid:** ❌
- Long information wars (>1 year)
- Demographic shifts (immigration, cohort effects)
- Generational replacement

**Impact:** Not critical for 180-day horizon; sensitivity < 5%.

---

### 7. **Single Narrative**
**Assumption:** One monolithic piece of misinformation dominates.

**Rationale:** Avoids multi-strain complexity; focus on single epidemic curve.

**When Valid:** ✅
- Dominant false narrative (e.g., election fraud claims)
- Homogeneous messaging
- Single correction strategy

**When Invalid:** ❌
- Multiple competing narratives
- Evolving narratives (conspiracy mutates to avoid corrections)
- Fragmented information landscape

**Impact:** Overestimates effectiveness of unified corrections. Real ecosystems need multiple intervention strategies.

---

### 8. **Parameter Clarity**
**Assumption:** β, σ, γ can be meaningfully estimated from population features (CRT scores, media hours).

**Rationale:** Psychological measures correlate with belief adoption (empirical foundation in METHODOLOGY.md).

**Limitations:** 
- Correlations are weak-to-moderate (r² ≈ 0.3-0.5)
- Causality not established (may confound)
- Parameter estimates are uncertain

**Recommendations:**
- Treat point estimates as rough approximations
- Run sensitivity analysis (see METHODOLOGY.md Section 6)
- Calibrate with real data from platform/survey studies

---

## Model Validation Checklist

Use this checklist to determine if SEIR is appropriate for your information context:

| Factor | ✅ Apply SEIR | ❌ Extended Model Needed |
|--------|---|---|
| **Timeline** | < 1 year | > 1 year |
| **Network** | Homogeneous | Highly clustered/modular |
| **Beliefs** | Single clear narrative | Multiple competing stories |
| **Intervention** | Single strategy | Multi-pronged approach |
| **Correction** | Permanent | Subject to forgetting |
| **Population** | Stable | High mobility/generational change |

---

## Parameter Uncertainty & Sensitivity

From METHODOLOGY.md Section 6, sensitivity ranking (most to least influential):

| Parameter | Sensitivity | Interpretation |
|-----------|-------------|-----------------|
| **β (transmission)** | HIGH (1.2-1.5) | Most critical for outcomes; focus interventions here |
| **γ (recovery)** | MEDIUM (0.6-0.9) | Important but less versatile than β reduction |
| **σ (adoption)** | LOW (0.2-0.4) | Less influential; long-term target |

**Implication:** Reducing exposure (lower β) is *most effective* intervention per unit effort.

---

## Key Limitations Summary

1. **Homogeneity bias:** Underestimates spread in network-structured populations
2. **Single-narrative assumption:** Overstates correction effectiveness
3. **No reinfection:** Exaggerates long-term epidemic control
4. **Constant parameters:** Unrealistic for sustained interventions
5. **Parameter uncertainty:** METHODOLOGY.md Table 2 shows ±30% typical ranges

**Recommendation:** Use this model for **strategic insights** (which interventions rank best), not precise predictions. Always validate with real-world data before policy decisions.

---

## Further Reading

- Full mathematical model & derivations: [METHODOLOGY.md](METHODOLOGY.md)
- Sensitivity analysis details: METHODOLOGY.md Section 6
- Model extensions & future work: METHODOLOGY.md Section 11
- Epidemiological background: References in METHODOLOGY.md

