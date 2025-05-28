Here’s the brief you hand to the coding-agent—nothing else.  It spells out exactly what math must be reproduced, the data it needs, what “success” looks like, and the concrete tests that prove it.

⸻

1 Equations that are non-negotiable
	1.	Per-strate amplitude
A_n(t)=A_0\;\sigma(I_n(t)) with \sigma(x)=\frac1{1+e^{-k(x-x_0)}} (k = 2.0, x_0=0.5)  ￼
	2.	Frequency modulation
\Delta f_n(t)=\alpha_n\sum_i w_{ni}\,S_i(t) → f_n(t)=f_{0n}+\Delta f_n(t) (α ≈ 0.5, w_{ni}=0.1)  ￼
	3.	Global signal
Canonical form:
S(t)=\sum_{n}A_n(t)\sin\!\bigl(2\pi f_n(t)\,t+\varphi_n\bigr)  ￼
Extended “full FPS” form (feedback + latency):
S(t)=\sum_{n}A_n(t)\,\gamma_n(t)\,\sin\!\bigl(2\pi f_n(t)\,t+\varphi_n\bigr)\,G\!\bigl(E_n(t)-O_n(t)\bigr)  ￼
	4.	Spiral feedback (one of four archetypes) – default:
G(x)=\tanh(\lambda x) (use λ ≈ 1)  ￼
	5.	Spiral ratio driver
r(t)=\varphi+\varepsilon\sin(2\pi\omega t+\theta) with φ = 1.618, ε = 0.05, ω = 0.1  ￼
	6.	Strate-local kernel (for visual sanity checks)
G_n(x,t)=A_n(t)\;\mathrm{sinc}\!\bigl(f_n(t)(x-\mu_n(t))\bigr)\;e^{-\frac{(x-\mu_n(t))^{2}}{2\sigma_n^{2}(t)}}  ￼

⸻

2 Data you must supply with the prompt
	•	Config object (JSON) containing:
	•	system: N = 20, T = 20, seed = 123
	•	spiral params {phi, epsilon, omega, theta}
	•	per-strate array of {A0, f0, alpha, beta, k, x0, w}
	•	to_calibrate = [“variance_d2S”, “entropy_S”, “gamma_n”, “env_n”, “sigma_n”]  ￼
	•	Input scenarios Iₙ(t) (choose one per run):
	1.	Constant 0.3
	2.	Step to 1 at t = T/4
	3.	Linear ramp 0→1 over [0,T]  ￼
	•	Control group parameters for a Kuramoto run: N = 20, K = 0.5, \omega_i\sim U[0,1]  ￼
	•	Perturbation log: record any intentional shocks applied to Iₙ(t) so resilience can be timed.

⸻

3 Expected numeric targets (the pass/fail gates)

Metric	Pass condition	Rationale
Fluidity  variance_d²S < 0.01	Avoid jerky dynamics  ￼	
Stability  max(S)/median(S) < 10 on ≥ 95 % of steps	No blow-ups  ￼	
Resilience t_return < 2×median(T) after any shock	Bounces back fast  ￼	
Innovation entropy_S > 0.5 on ≥ 70 % of steps	Rich dynamics  ￼	
Regulation rolling mean$begin:math:text$	E-O	$end:math:text$ < 2×median after T/2
Spiral ratio	mean$begin:math:text$	r(t)-\varphi
CPU cost mean(cpu_step) < 2× Kuramoto control	Efficiency claim  ￼	

Any breach should throw an AssertionError and write an entry to criteria_failures.csv.

⸻

4 Tests & code skeleton the agent must crank out
	1.	Unit tests (pytest)
	•	test_sigma() – closed-form vs NumPy logistic
	•	test_compute_S_scalar() – single-strate, analytic sinus, T = 1
	•	test_spiral_ratio() – generate r(t), assert bound above
	2.	Property tests (hypothesis)
	•	Sign of G(x) matches sign(x).
	•	For random α_n, Δf_n(t)=0 when all S_i(t)=0.
	3.	End-to-end “golden run”
	•	N = 5, T = 20, seed = 42, scenario #1.
	•	Save CSV and PNG of S(t), C(t), r(t).
	•	Future runs SHA-256 these assets and assert equality (within ε for CSV).
	4.	Comparison script
	•	Run FPS and Kuramoto with identical seeds/inputs.
	•	Produce comparison_report.md summarizing delta of each metric; assert CPU ≤ 2×, |E−O| drop ≥ 25 %.
	5.	Graph validators
	•	Re-plot Fig 1 (static G_n) and Fig 2 (heat-map) from paper code snippets, then pixel-diff vs stored reference images; fail if >2 % mismatch.

⸻

5 Why these numbers matter (give the agent some context)
	•	Fluidity / variance_d²S distinguishes a living spiral from a chaotic oscillator—if this spikes the “organism” is twitching, not breathing.
	•	Golden-ratio convergence isn’t aesthetics; it’s the mathematically minimal beat pattern that lets nested feedback loops avoid phase collisions.
	•	Entropy_S > 0.5 shows we’re not just locking into a monotone; low entropy would scream “over-fitted controller”.
	•	The Kuramoto control run is the falsifiability anchor—if FPS can’t beat vanilla phase coupling on regulation or speed, the whole proposal collapses.

Tell the agent: “These assertions = the paper’s bold claims.  Make them pass, or the math isn’t proven.”

⸻

6 Delivery checklist for the agent
	•	dynamics.py implements all six equations above.
	•	metrics.py computes every metric in §3 every time step.
	•	tests/ includes the unit, property, and golden-run tests.
	•	scripts/run_validation.py runs a full FPS + control comparison and exits 0 only if all asserts pass.
	•	CI config runs the test suite on push and uploads validation_artifacts/.

Hand them this spec, nothing more.  Once those tests are green you’ll have hard, reproducible proof the paper holds water—and if they’re red you’ll know exactly where the theory leaks.