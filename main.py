import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from sklearn.decomposition import PCA

from src.data.gsw_loader import load_gsw_data
from src.model.parameterization import ATSMParams
from src.model.state_space import build_state_space_from_vector
from src.filter.kalman_filter import KalmanFilter
from src.filter.kalman_smoother import KalmanSmoother
from src.estimation.optimizer import ATSMOptimizer, print_parameter_summary
from src.analysis.diagnostics import compute_residuals, calculate_performance_metrics, get_summary_statistics
from src.analysis.plots import plot_yield_fit, plot_factors, plot_residuals, plot_loadings, plot_term_premium, plot_term_premium_surface
from src.analysis.term_premium import decompose_term_premium
from src.analysis.macro_analyzer import run_macro_tp_analysis
from src.analysis.econometrics import run_econometric_analysis
from src.analysis.benchmarking import run_benchmarking

def main():
    print("--- Starting Final ATSM Estimation Pipeline (Golden Configuration) ---")

    # 1. Configuration
    FILE_PATH = "feds200628_clean.csv" 
    N_FACTORS = 3
    MATURITIES = np.array([1, 2, 3, 5, 7, 10, 20, 30], dtype=float)
    N_YIELDS = len(MATURITIES)
    DELTA_T = 1/12.0
    START_DATE = "1990-01-01"
    END_DATE = "2026-02-28"
    X0 = np.zeros(N_FACTORS)
    P0 = np.eye(N_FACTORS) * 0.01 

    # --- 2. Load Data ---
    try:
        df_yields_raw = load_gsw_data(FILE_PATH)
        df_yields = df_yields_raw.loc[START_DATE:END_DATE] if START_DATE else df_yields_raw
        observations = df_yields.values
        dates = df_yields.index
        print(f"Data loaded successfully. Shape: {observations.shape}")
    except Exception as e:
        print(f"Fatal Error: {e}")
        return

    # --- 3. Stage 1: Restore Success Settings ---
    params_template = ATSMParams(n_factors=N_FACTORS, n_yields=N_YIELDS)
    initial_guess_vector = params_template.get_parameter_vector()
    n_lt = params_template._n_lower_tri_params
    
    # KQ
    initial_guess_vector[:n_lt] = 0.0
    initial_guess_vector[0] = np.log(1e-6) # K11
    initial_guess_vector[2] = np.log(0.4)  # K22
    initial_guess_vector[5] = np.log(0.4)  # K33
    initial_guess_vector[4] = -0.8         # K32
    
    # Sigma
    initial_guess_vector[n_lt : 2*n_lt] = 0.0
    initial_guess_vector[n_lt] = np.log(0.005)
    initial_guess_vector[n_lt+2] = np.log(0.005)
    initial_guess_vector[n_lt+5] = np.log(0.005)
    
    # delta0, delta1
    initial_guess_vector[2*n_lt] = 0.03 
    initial_guess_vector[2*n_lt + 1 : 2*n_lt + 4] = [1.0, 1.0, 0.0]
    
    # R
    initial_guess_vector[2*n_lt + 4 : 2*n_lt + 4 + N_YIELDS] = np.log(0.0005)
    
    # Market Price of Risk: Exact Step 40 Golden Initial Guess
    initial_guess_vector[-N_FACTORS*N_FACTORS - N_FACTORS : -N_FACTORS*N_FACTORS] = -0.3
    initial_guess_vector[-N_FACTORS*N_FACTORS:] = -0.01

    # --- Restore Successful Bounds ---
    bounds = []
    bounds.append((-18.0, -10.0)) # K11
    bounds.append((-0.01, 0.01))  # K21
    bounds.append((-2.0, -0.5))   # K22 (Slow)
    bounds.append((-0.01, 0.01))  # K31
    bounds.append((-3.0, -0.1))   # K32
    bounds.append((-2.0, -0.5))   # K33 (Slow)
    
    for i in range(N_FACTORS):
        for j in range(i+1):
            if i == j: bounds.append((-12.0, -4.0))
            else: bounds.append((-0.01, 0.01))
            
    bounds += [(0.005, 0.04)] # delta0
    bounds += [(0.999, 1.001)] + [(0.999, 1.001)] + [(-0.001, 0.001)] # delta1
    bounds += [(-15.0, -7.0)] * N_YIELDS # R
    
    bounds += [(-0.5, -0.1)] * N_FACTORS # Force strong negative lambda0 for positive TP!
    for _ in range(N_FACTORS * N_FACTORS):
        bounds.append((-5.0, 5.0)) # lambda1

    # --- 4. Main Optimization ---
    optimizer = ATSMOptimizer(N_FACTORS, N_YIELDS, MATURITIES, DELTA_T)
    results = optimizer.optimize(observations, initial_guess_vector, bounds=bounds)
    
    final_params = ATSMParams.from_vector(results.x, n_factors=N_FACTORS, n_yields=N_YIELDS)
    print_parameter_summary(final_params)

    # --- 5. Run Filter/Smoother ---
    ss_model = build_state_space_from_vector(final_params.get_parameter_vector(), MATURITIES, DELTA_T, N_FACTORS, N_YIELDS)
    kalman_filter = KalmanFilter(ss_model.Phi, ss_model.Q, ss_model.H, ss_model.R, ss_model.drift, ss_model.intercept)
    X_filtered, P_filtered, X_predicted, P_predicted, log_likelihood = kalman_filter.filter(observations, X0, P0)
    smoother = KalmanSmoother(ss_model.Phi, ss_model.Q)
    X_smoothed, P_smoothed = smoother.smooth(X_filtered, P_filtered, X_predicted, P_predicted)

    # --- 6. Results & Plots ---
    fitted_yields = (ss_model.H @ X_smoothed[..., np.newaxis]).squeeze(-1) + ss_model.intercept.flatten()
    fitted_yields_df = pd.DataFrame(fitted_yields, index=dates, columns=MATURITIES)
    expected_rates_df, term_premiums_df = decompose_term_premium(
        X_smoothed, final_params.KP, final_params.muP, final_params.delta0, final_params.delta1, MATURITIES, fitted_yields_df
    )
    
    # --- 7. Statistics and Report ---
    print("\n7. Saving statistics and report to outputs/...")
    perf = calculate_performance_metrics(observations, fitted_yields, log_likelihood, len(results.x))
    factors_df = pd.DataFrame(X_smoothed, index=dates, columns=['Level', 'Slope', 'Curvature'])
    
    with open("outputs/final_paper_report.txt", "w") as f:
        f.write(f"Log-Likelihood: {perf['log_lik']:.4f}\n")
        f.write(f"Total RMSE: {perf['total_rmse']:.6f}\n\n")
        f.write("--- Summary Statistics: Latent Factors ---\n")
        f.write(get_summary_statistics(factors_df).to_string())
        f.write("\n\n--- Summary Statistics: Term Premium ---\n")
        f.write(get_summary_statistics(term_premiums_df).to_string())

    # Save CSVs
    pd.DataFrame(results.x).to_csv("outputs/best_params_vector.csv", index=False, header=False)
    df_yields.to_csv("outputs/observed_yields.csv")
    fitted_yields_df.to_csv("outputs/fitted_yields.csv")
    expected_rates_df.to_csv("outputs/expected_avg_short_rates.csv")
    term_premiums_df.to_csv("outputs/term_premiums.csv")
    factors_df.to_csv("outputs/smoothed_factors.csv")
    
    # --- 8. Plots ---
    plot_loadings(ss_model.H, MATURITIES, save_path="outputs/factor_loadings.png")
    plot_yield_fit(df_yields, fitted_yields_df, save_path="outputs/observed_vs_fitted.png")
    plot_factors(X_smoothed, P_smoothed, dates, save_path="outputs/latent_factors.png")
    plot_term_premium(fitted_yields_df, expected_rates_df, term_premiums_df, MATURITIES, save_path="outputs/term_premium_decomp.png")
    plot_term_premium_surface(term_premiums_df, MATURITIES, save_path="outputs/term_premium_surface.png")
    
    # --- 9. Phase 3: Macro-TP Analysis ---
    try:
        run_macro_tp_analysis()
        run_econometric_analysis()
        run_benchmarking()
    except Exception as e:
        print(f"Macro/Econometric analysis failed: {e}")

    print("\n--- ATSM Pipeline Finished. Results restored and saved. ---")

if __name__ == "__main__":
    main()
