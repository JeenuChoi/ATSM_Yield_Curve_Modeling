import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.api import VAR, VECM
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.stats.stattools import durbin_watson

def check_stationarity(df, cols):
    """Performs Augmented Dickey-Fuller (ADF) test."""
    print("\n--- [1] ADF Unit Root Test (Stationarity Check) ---")
    results = []
    for col in cols:
        res = adfuller(df[col].dropna())
        is_stationary = res[1] < 0.05
        results.append({
            "Variable": col,
            "ADF Statistic": f"{res[0]:.4f}",
            "p-value": f"{res[1]:.4f}",
            "Stationary?": "YES" if is_stationary else "NO"
        })
    print(pd.DataFrame(results))
    return results

def test_cointegration(df, det_order=0, k_ar_diff=1):
    """
    Performs Johansen Cointegration Test.
    det_order: -1 (no det), 0 (constant), 1 (constant + trend)
    """
    print("\n--- [2] Johansen Cointegration Test ---")
    res = coint_johansen(df, det_order, k_ar_diff)
    
    # Trace Statistic and Critical Values (95%)
    trace_stat = res.lr1
    crit_vals = res.cvt[:, 1] # 95% level
    
    rank = 0
    for i in range(len(trace_stat)):
        if trace_stat[i] > crit_vals[i]:
            rank += 1
            
    print(f"Cointegration Rank (95% confidence): {rank}")
    print("Trace Statistic vs Critical Value (95%):")
    for i in range(len(trace_stat)):
        print(f"r <= {i}: {trace_stat[i]:.2f} vs {crit_vals[i]:.2f}")
    
    return rank

def run_econometric_analysis(merged_csv="outputs/macro_tp_merged.csv", output_dir="outputs"):
    """
    Advanced workflow: ADF -> Cointegration -> [VECM or VAR] -> IRF
    """
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found. Please wait for the main pipeline to finish.")
        return

    # 1. Load Data
    df = pd.read_csv(merged_csv, index_col=0, parse_dates=True)
    core_cols = ['Term_Premium', 'INF_UNCERTAIN', 'UNRATE', 'M2_GROWTH']
    core_cols = [c for c in core_cols if c in df.columns]
    df_core = df[core_cols].dropna()
    
    # 2. Check Stationarity (Levels)
    check_stationarity(df_core, core_cols)
    
    # 3. Cointegration Test (Using Level Data)
    rank = test_cointegration(df_core)
    
    report_path = os.path.join(output_dir, "econometric_report.txt")
    with open(report_path, "w") as f:
        f.write("="*60 + "\n")
        f.write("PHASE 4: ADVANCED ECONOMETRIC ANALYSIS (VAR vs VECM)\n")
        f.write("="*60 + "\n")
        f.write(f"Cointegration Rank: {rank}\n\n")

        # --- Case A: VECM (Long-term Equilibrium exists) ---
        if rank > 0:
            print(f"\n--- [3-A] Estimating VECM (Rank={rank}) ---")
            vecm_model = VECM(df_core, k_ar_diff=2, coint_rank=rank, deterministic='co').fit()
            
            # IRF for VECM
            print("Generating VECM IRF plots...")
            irf = vecm_model.irf(24)
            fig = irf.plot(impulse='INF_UNCERTAIN', response='Term_Premium', figsize=(10, 6))
            plt.title(f"VECM IRF: Response of TP to Inflation Uncertainty (Rank={rank})")
            
            os.makedirs(output_dir, exist_ok=True)
            v_plot_path = os.path.join(output_dir, "irf_vecm_uncertainty_to_tp.png")
            plt.savefig(v_plot_path)
            plt.close()
            print(f"VECM IRF saved to: {v_plot_path}")
            
            f.write("--- VECM Estimation Results ---\n")
            f.write("Status: Long-term equilibrium relationship detected and modeled.\n")
            f.write(f"Selected Rank: {rank}\n")
            
        # --- Case B: VAR (Short-term Shock Analysis on Differenced Data) ---
        print("\n--- [3-B] Estimating VAR (First Differenced Data) ---")
        df_diff = df_core.diff().dropna()
        var_model = VAR(df_diff)
        best_lag = var_model.select_order(maxlags=12).aic
        var_results = var_model.fit(best_lag)
        
        # Diagnostic: DW on VAR Residuals
        dw_stats = durbin_watson(var_results.resid)
        
        # IRF for VAR
        print("Generating VAR IRF plots...")
        irf_var = var_results.irf(24)
        fig_var = irf_var.plot(impulse='INF_UNCERTAIN', response='Term_Premium', orth=True, figsize=(10, 6))
        plt.title("VAR IRF: Short-term Response of TP to Uncertainty Shock")
        
        os.makedirs(output_dir, exist_ok=True)
        var_plot_path = os.path.join(output_dir, "irf_var_uncertainty_to_tp.png")
        plt.savefig(var_plot_path)
        plt.close()
        print(f"VAR IRF saved to: {var_plot_path}")
        
        f.write("\n--- VAR (Short-term) Results ---\n")
        f.write(f"Optimal Lag: {best_lag}\n")
        f.write("Durbin-Watson Statistics (After VAR):\n")
        for i, col in enumerate(core_cols):
            f.write(f"  {col:20}: {dw_stats[i]:.4f}\n")
            
    print(f"\nAnalysis complete. Results and IRF plots saved to {output_dir}/")
    print(f"Report: {report_path}")

if __name__ == "__main__":
    run_econometric_analysis()
