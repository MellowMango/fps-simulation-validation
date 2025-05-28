# FPS STUDY — QUICK-SCAN MARKDOWN PRIMER
_Brief: copy-paste this into the agent’s prompt so it “gets” the paper before crunching numbers._

---

## 1 What the study is about
**Fractal-Phase Spiral (FPS)** is a multi-strate oscillator framework pitched as a smarter, lighter alternative to classic Kuramoto-style synchronisation.  
The paper argues that by injecting a golden-ratio driver and a non-linear feedback kernel, FPS achieves:

1. **Ultra-smooth global signals** (low jerk / variance of second derivative).  
2. **Fast self-healing** after external shocks.  
3. **High entropy** (rich dynamics, no dead modes).  
4. **Lower compute cost** than a tuned Kuramoto network at similar quality.  

In short: “beautiful maths → nicer waveforms → cheaper CPUs.”

---

## 2 Core hypotheses to validate

| ID | Claim | Metric that proves or kills it |
|----|-------|--------------------------------|
| H1 | Spiral ratio converges on **φ = 1.618** | `mean(|r(t)-φ|)` in last ¼ run < ε/2 |
| H2 | **Fluidity**: movement is continuous, not jittery | `variance_d²S < 0.01` |
| H3 | **Stability**: no run-away amplitudes | `max(S)/median(S) < 10` on ≥95 % steps |
| H4 | **Resilience**: recovers from shocks fast | `t_return < 2×median(T)` |
| H5 | **Innovation**: system stays information-rich | `entropy_S > 0.5` on ≥70 % steps |
| H6 | Beats control on **regulation accuracy** | rolling mean |E-O| at T/2 < Kuramoto ×0.75 |
| H7 | **Efficiency**: CPU ≤ 2× control | wall-clock per step |

All other maths supports these seven.

---

## 3 Model anatomy (equations in plain English)

1. **Amplitude gating**  
   `A_n(t) = A0 × logistic(I_n(t))`  
   A stratum’s loudness follows its local input.

2. **Frequency modulation**  
   `f_n(t) = base + α * Σ_w * S(t)`  
   Each stratum nudges its own pitch by listening to everyone else.

3. **Global signal constructor**  
   `S(t) = Σ A_n(t) · γ_n(t) · sin(2π f_n(t) t + φ_n) · G(E_n-O_n)`  
   Add all sinewaves, multiply by a feedback gain, then warp with a non-linear gate.

4. **Feedback gate archetype** (default)  
   `G(x) = tanh(λx)` — compresses big errors, amplifies subtle ones.

5. **Golden-ratio driver**  
   `r(t) = φ + ε sin(ωt + θ)` — tiny oscillation around φ to avoid mode lock-in.

6. **Visual sanity kernel**  
   `G_n(x,t) = A_n sinc(f_n(x-μ_n)) e^{-(x-μ_n)²/2σ²}` — used only for plotting heat-maps.

---

## 4 Data the agent must receive

* **Config.json:** `N, T, seed, spiral{φ,ε,ω,θ},` plus per-stratum params (`A0,f0,α,k,x0,w`).  
* **Input scenarios:** constant 0.3, step at T/4 to 1, or linear ramp 0→1.  
* **Control setup:** Kuramoto with `N=20, K=0.5, ω_i∼U[0,1]`.  
* **Perturbations:** list of time-stamped shocks to `I_n(t)`.

---

## 5 Validation funnel (what “success” means operationally)

1. **Unit & property tests pass** → formulas copied correctly.  
2. **Golden-run hash matches reference files** → simulation is deterministic.  
3. **Seven metrics >= thresholds** for every production run → paper’s numbers hold.  
4. **Comparison report** shows FPS beats Kuramoto on CPU & |E-O| → practical edge proven.  
5. **Pixel-diff** of recreated figures < 2 % → visuals identical to manuscript.

If any gate fails, the study’s claim is unresolved.

---

## 6 Typical failure signatures & likely causes

| Symptom | Usual culprit |
|---------|---------------|
| σ spike / jerkiness | mis-copied logistic constants `k` or `x0` |
| r(t) sticks near 1.0 or 2.0 | golden-ratio driver missing / ε set to 0 |
| Entropy flatlines | feedback gate saturating (λ too high) |
| CPU blows past 2× | unnecessary Python loops in hot path |
| Pixel-diff > 2 % | axis scaling or colormap mismatch |

---

## 7 Hand-off checklist for the coding agent

- Implement all six equations _exactly_.  
- Compute & assert seven metrics every step.  
- Provide CLI scripts: `run_validation`, `compare_vs_control`.  
- Ship `tests/` with unit + property + golden tests.  
- CI must break on **any** red.

> **Bottom line:** green CI = paper validated. Anything red = back to debugging.