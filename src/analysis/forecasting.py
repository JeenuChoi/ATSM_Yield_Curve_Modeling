import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from scipy.stats import norm

def diebold_mariano_test(actual, forecast_a, forecast_b, h=1):
    """
    Performs the Diebold-Mariano test to compare two forecast models.
    Null Hypothesis: Both models have the same forecast accuracy.
    """
    e_a = (actual - forecast_a).values
    e_b = (actual - forecast_b).values
    
    # Loss differential (Squared Error)
    d = e_a**2 - e_b**2
    d_mean = np.mean(d)
    
    # Auto-covariance for h-step ahead (Hansen's correction)
    def autocovariance(xi, k):
        n = len(xi)
        if n <= k: return 0
        return np.mean((xi[:n-k] - xi.mean()) * (xi[k:] - xi.mean()))

    n = len(d)
    var_d = np.var(d) / n
    if h > 1:
        for i in range(1, h):
            var_d += 2 * autocovariance(d, i) / n
            
    dm_stat = d_mean / np.sqrt(max(var_d, 1e-12))
    p_value = 2 * (1 - norm.cdf(np.abs(dm_stat)))
    
    return dm_stat, p_value

def run_oos_evaluation(actual_series, model_forecast, rw_forecast, title="10Y Yield", output_dir="outputs"):
    """
    Evaluates OOS performance of the model against Random Walk for a specific maturity.
    """
    print(f"\n--- [Phase 8] OOS Evaluation: {title} ---")
    
    # Align indices
    common_idx = actual_series.index.intersection(model_forecast.index).intersection(rw_forecast.index)
    actual = actual_series.loc[common_idx]
    forecast = model_forecast.loc[common_idx]
    rw = rw_forecast.loc[common_idx]
    
    # 1. Calculate Metrics (in Basis Points for readability)
    rmse_ours = np.sqrt(np.mean((actual - forecast)**2)) * 10000
    rmse_rw = np.sqrt(np.mean((actual - rw)**2)) * 10000
    
    # 2. Diebold-Mariano Test
    dm_stat, p_val = diebold_mariano_test(actual, rw, forecast)
    
    print(f"Our Model RMSE: {rmse_ours:.2f} bps")
    print(f"Random Walk RMSE: {rmse_rw:.2f} bps")
    print(f"DM Statistic: {dm_stat:.4f}, P-value: {p_val:.4f}")
    
    # 3. Visualization
    plt.figure(figsize=(12, 6))
    plt.plot(actual.index, actual * 100, label=f'Actual {title} (%)', color='black', linewidth=1.5)
    plt.plot(forecast.index, forecast * 100, label='Model Forecast (t+1|t)', color='blue', linestyle='--', alpha=0.8)
    plt.plot(rw.index, rw * 100, label='Random Walk (Y_t)', color='red', linestyle=':', alpha=0.8)
    plt.title(f"Out-of-Sample Forecast: {title}")
    plt.ylabel("Yield (%)")
    plt.legend()
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.savefig(os.path.join(output_dir, f"oos_forecast_{title.replace(' ', '_')}.png"))
    plt.close()
    
    # 4. Save Report
    report_path = os.path.join(output_dir, "oos_yield_report.txt")
    with open(report_path, "a") as f:
        f.write(f"--- Maturity: {title} ---\n")
        f.write(f"Forecast Period: {common_idx.min().date()} to {common_idx.max().date()}\n")
        f.write(f"Our Model RMSE: {rmse_ours:.2f} bps\n")
        f.write(f"Random Walk RMSE: {rmse_rw:.2f} bps\n")
        f.write(f"Diebold-Mariano Stat: {dm_stat:.4f}, P-value: {p_val:.4f}\n")
        status = "BETTER" if (rmse_ours < rmse_rw and p_val < 0.05) else "NOT SIGNIFICANTLY BETTER"
        f.write(f"Conclusion: Model is {status} than Random Walk.\n\n")
            
    return {"rmse_ours": rmse_ours, "p_value": p_val}

if __name__ == "__main__":
    pass
