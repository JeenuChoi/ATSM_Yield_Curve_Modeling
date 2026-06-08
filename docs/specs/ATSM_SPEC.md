You are an AI coding agent working inside a local repository.

============================================================
PROJECT: UST Macro-Finance ATSM (Gaussian 3-factor, Kalman MLE)
DATA: Federal Reserve GSW zero-coupon yields
FREQUENCY: Monthly (end-of-month)
PHASE 1 ONLY: lambda_t = 0  (P = Q for debugging / MVP)
============================================================

GOAL
Implement a research-quality Python codebase for a no-arbitrage affine term structure model (ATSM) of the U.S. Treasury yield curve using GSW zero-coupon yields.

We will start with a stable MVP:
- Gaussian 3-factor continuous-time OU state dynamics under Q
- Exponential-affine bond pricing via Riccati ODEs
- State-space representation with diagonal measurement error R to avoid stochastic singularity
- Kalman filter log-likelihood + L-BFGS-B MLE
- Diagnostics: fitted vs observed yields, residuals/innovations, factor time series (smoothed)

IMPORTANT: Implement only Phase 1 (lambda = 0). Do NOT implement risk premium phases yet.

------------------------------------------------------------
MODEL SPECIFICATION (Phase 1 / MVP)
------------------------------------------------------------

Latent state:
X_t ∈ R^3

Risk-neutral dynamics (continuous-time OU):
dX_t = K_Q (θ_Q − X_t) dt + Σ dW_t^Q

Short rate:
r_t = δ0 + δ1' X_t

Zero-coupon bond price (exponential-affine):
P(t, τ) = exp(A(τ) − B(τ)' X_t)

Riccati ODEs:
dB/dτ = −K_Q' B + δ1,     B(0)=0
dA/dτ = −(K_Q θ_Q)' B + 0.5 B' ΣΣ' B − δ0,     A(0)=0

Model-implied yield:
y(t,τ) = −A(τ)/τ + (B(τ)'/τ) X_t

------------------------------------------------------------
DATA REQUIREMENTS (GSW)
------------------------------------------------------------

Use Federal Reserve GSW zero-coupon yields (daily).
Select maturities in YEARS:
[0.25, 0.5, 1, 2, 3, 5, 7, 10, 20, 30]

Convert daily to MONTHLY end-of-month (EOM).
Output DataFrame:
- index: month-end datetime
- columns: maturities as strings or floats (consistent)
- values: yields in DECIMAL (not percent) OR in percent, but consistent everywhere.
Pick one convention and document it (recommended: decimal, e.g., 0.045).

Handle missing values robustly:
- Drop months with too many missing maturities
- Or forward-fill within a limited window (document choice)
Prefer simple, deterministic cleaning for MVP.

------------------------------------------------------------
STATE-SPACE FORM (Monthly)
------------------------------------------------------------

We work in discrete time with step Δ = 1/12 year (monthly).

Transition:
X_t = Φ X_{t−1} + c + ε_t,    ε_t ~ N(0, Q)

OU discretization:
Φ = exp(−K_Q Δ)
c = (I − Φ) θ_Q
Q = ∫_0^Δ exp(−K_Q s) ΣΣ' exp(−K_Q' s) ds

For MVP compute Q via numerical quadrature with enough steps to be stable.
Avoid fragile formulas; prefer robust computation.

Measurement:
y_t = a + H X_t + η_t,     η_t ~ N(0, R)

Where for each maturity τ_i:
a_i = −A(τ_i)/τ_i
H_i = (B(τ_i)'/τ_i)  (row vector)

R is diagonal, with positive variances to avoid stochastic singularity.

------------------------------------------------------------
IDENTIFICATION / PARAMETER CONSTRAINTS (Canonical-style)
------------------------------------------------------------

To reduce observation equivalence and improve stability:

K_Q: lower triangular, diag positive
Σ: lower triangular (Cholesky), diag positive
R: diagonal, positive

Implement parameter transforms:
- For positive diagonals/variances: exp(raw)
- Keep off-diagonal lower-triangular elements unconstrained (raw)

Add small variance floors if needed (e.g., min 1e-8) to keep S_t PD.

------------------------------------------------------------
ESTIMATION
------------------------------------------------------------

Implement Kalman filter with prediction error decomposition.

At time t:
v_t = y_t − y_hat_t
S_t = H P_pred H' + R

Log-likelihood:
ℓ_t = −0.5 [ m log(2π) + log|S_t| + v_t' S_t^{-1} v_t ]

Total loglik = Σ_t ℓ_t

Optimization:
- minimize negative loglik via L-BFGS-B
- provide reasonable initial parameters
- implement failure handling: if S_t not PD, return large penalty

After MLE:
- implement RTS smoother to get X_{t|T}
- produce plots and saved outputs

------------------------------------------------------------
NUMERICAL STABILITY RULES
------------------------------------------------------------

- Never use explicit matrix inverse for S_t. Use solve() / Cholesky.
- Ensure S_t is positive definite; add jitter if needed (document).
- Keep P symmetric: enforce (P+P.T)/2 if needed.
- Use tight tolerances for Riccati ODE (rtol, atol).
- Log determinant via Cholesky to avoid det() instability.

------------------------------------------------------------
DELIVERABLES (Phase 1)
------------------------------------------------------------

1) Working project structure with modules
2) Runnable pipeline: python main.py --start 1990-01 --end 2025-12
3) Saved outputs in outputs/:
   - fitted_yields.csv (observed vs fitted for all maturities)
   - factors_smoothed.csv (X_{t|T})
   - residuals.csv (innovations v_t)
   - plots: observed_vs_fitted.png, factors.png, residuals.png
4) Basic diagnostics printed to console:
   - final negative log-likelihood
   - parameter summary (transformed values)
   - simple RMSE per maturity

------------------------------------------------------------
PROJECT STRUCTURE (Create exactly)
------------------------------------------------------------

project_root/
  README.md
  pyproject.toml (or requirements.txt)
  main.py
  src/
    data/
      gsw_loader.py
    model/
      riccati.py
      ou_discretization.py
      state_space.py
      parameterization.py
    filter/
      kalman_filter.py
      kalman_smoother.py
    estimation/
      likelihood.py
      optimizer.py
    analysis/
      diagnostics.py
      plots.py
  outputs/   (gitignored or kept empty)
  tests/
    test_gsw_loader.py
    test_riccati.py
    test_kalman_basic.py

------------------------------------------------------------
IMPLEMENTATION ORDER (Strict)
------------------------------------------------------------

Step 0: Create structure + README with run instructions
Step 1: Implement gsw_loader.py + test
Step 2: Implement riccati.py + test
Step 3: Implement ou_discretization.py + test
Step 4: Implement state_space.py (build a,H,Φ,c,Q,R)
Step 5: Implement kalman_filter.py + likelihood.py + tests
Step 6: Implement optimizer.py + parameterization.py
Step 7: Implement kalman_smoother.py + diagnostics/plots + main.py integration

Do not jump ahead. Each step must include a minimal test or runnable example.

------------------------------------------------------------
IMPORTANT SCOPE LIMIT
------------------------------------------------------------

PHASE 1 ONLY:
- lambda_t = 0
- no macro variables yet
- no UKF/PF yet
- no square-root KF yet (optional later)

Once Phase 1 works and diagnostics look reasonable, we will extend.
============================================================