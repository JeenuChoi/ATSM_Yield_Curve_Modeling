import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt
from src.data.gsw_loader import load_gsw_data
from src.model.parameterization import ATSMParams
from src.model.state_space import build_state_space_from_vector
from src.filter.kalman_filter import KalmanFilter
from src.filter.kalman_smoother import KalmanSmoother
from src.estimation.optimizer import ATSMOptimizer
from src.analysis.forecasting import run_oos_evaluation

def main6():
    print("\n" + "="*60)
    print("--- [MAIN6] OOS YIELD FORECASTING PIPELINE ---")
    print("="*60)

    # 1. Configuration
    FILE_PATH = "feds200628_clean.csv" 
    N_FACTORS = 3
    MATURITIES = np.array([1, 2, 3, 5, 7, 10, 20, 30], dtype=float)
    N_YIELDS = len(MATURITIES)
    DELTA_T = 1/12.0
    START_DATE = "1990-01-01"
    TRAIN_END_DATE = "2018-12-31" 
    
    # 2. Load and Split Data
    df_yields_raw = load_gsw_data(FILE_PATH).loc[START_DATE:"2026-02-28"]
    if df_yields_raw.empty:
        print("Error: Yield data is empty. Check data/feds200628_clean.csv path.")
        return
    df_train = df_yields_raw.loc[:TRAIN_END_DATE]
    
    print(f"Training on: {df_train.index.min()} to {df_train.index.max()}")

    # 3. MLE Re-optimization (Purely on In-sample data)
    print("\n--- Step 1: Re-estimating Model (Blind to 2019-2026) ---")
    
    # --- EXACT GOLDEN INITIAL GUESS ---
    params_template = ATSMParams(n_factors=N_FACTORS, n_yields=N_YIELDS)
    initial_guess_vector = params_template.get_parameter_vector()
    n_lt = params_template._n_lower_tri_params
    
    initial_guess_vector[:n_lt] = 0.0
    initial_guess_vector[0] = np.log(1e-6) # K11
    initial_guess_vector[2] = np.log(0.4)  # K22
    initial_guess_vector[5] = np.log(0.4)  # K33
    initial_guess_vector[4] = -0.8         # K32
    initial_guess_vector[n_lt : 2*n_lt] = 0.0
    initial_guess_vector[n_lt] = np.log(0.005)
    initial_guess_vector[n_lt+2] = np.log(0.005)
    initial_guess_vector[n_lt+5] = np.log(0.005)
    initial_guess_vector[2*n_lt] = 0.03 
    initial_guess_vector[2*n_lt + 1 : 2*n_lt + 4] = [1.0, 1.0, 0.0]
    initial_guess_vector[2*n_lt + 4 : 2*n_lt + 4 + N_YIELDS] = np.log(0.0005)
    initial_guess_vector[-N_FACTORS*N_FACTORS - N_FACTORS : -N_FACTORS*N_FACTORS] = -0.3
    initial_guess_vector[-N_FACTORS*N_FACTORS:] = -0.01

    # --- EXACT GOLDEN BOUNDS ---
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
    bounds += [(-0.5, -0.1)] * N_FACTORS # lambda0
    for _ in range(N_FACTORS * N_FACTORS):
        bounds.append((-5.0, 5.0)) # lambda1

    optimizer = ATSMOptimizer(N_FACTORS, N_YIELDS, MATURITIES, DELTA_T)
    print("Optimization in progress...")
    results = optimizer.optimize(df_train.dropna().values, initial_guess_vector, bounds=bounds)
    
    if len(results.x) == 0:
        print("Critical Error: Optimizer failed. Using initial guess as fallback.")
        final_params = ATSMParams.from_vector(initial_guess_vector, n_factors=N_FACTORS, n_yields=N_YIELDS)
    else:
        final_params = ATSMParams.from_vector(results.x, n_factors=N_FACTORS, n_yields=N_YIELDS)
        print("In-sample re-estimation successful.")
    
    # 4. Generate Factors for the whole period using OOS Parameters
    ss_model = build_state_space_from_vector(final_params.get_parameter_vector(), MATURITIES, DELTA_T, N_FACTORS, N_YIELDS)
    kalman_filter = KalmanFilter(ss_model.Phi, ss_model.Q, ss_model.H, ss_model.R, ss_model.drift, ss_model.intercept)
    X_filtered, P_filtered, X_predicted, P_predicted, _ = kalman_filter.filter(df_yields_raw.values, np.zeros(N_FACTORS), np.eye(N_FACTORS)*0.01)
    smoother = KalmanSmoother(ss_model.Phi, ss_model.Q)
    X_smoothed, _ = smoother.smooth(X_filtered, P_filtered, X_predicted, P_predicted)
    
    # 5. Perform 1-Step Ahead Yield Forecasting (OOS Period)
    forecast_yields = []
    dates_oos = df_yields_raw.index[df_yields_raw.index > TRAIN_END_DATE]
    start_idx = len(df_train) - 1
    
    for i in range(start_idx, len(df_yields_raw) - 1):
        x_t = X_smoothed[i].reshape(-1, 1)
        x_next_pred = ss_model.Phi @ x_t + ss_model.drift
        y_next_pred = (ss_model.H @ x_next_pred + ss_model.intercept).flatten()
        forecast_yields.append(y_next_pred)
        
    df_forecast = pd.DataFrame(forecast_yields, index=dates_oos, columns=MATURITIES)
    df_actual = df_yields_raw.loc[dates_oos]
    df_rw = df_yields_raw.shift(1).loc[dates_oos] 

    if os.path.exists("outputs/oos_yield_report.txt"):
        os.remove("outputs/oos_yield_report.txt")

    # 6. Evaluation for 10Y Yield
    run_oos_evaluation(df_actual[10.0], df_forecast[10.0], df_rw[10.0], title="10Y Yield")
    
    # 7. Evaluation for 2Y Yield
    run_oos_evaluation(df_actual[2.0], df_forecast[2.0], df_rw[2.0], title="2Y Yield")

    # 8. Save TRUE OOS Forecasts for Benchmarking
    df_forecast.to_csv("outputs/true_oos_forecasts.csv")
    print("\n[SUCCESS] True OOS forecasts saved to outputs/true_oos_forecasts.csv")

    print("\n" + "="*60)
    print("--- [MAIN6] YIELD OOS PIPELINE FINISHED ---")
    print("="*60)

if __name__ == "__main__":
    main6()
