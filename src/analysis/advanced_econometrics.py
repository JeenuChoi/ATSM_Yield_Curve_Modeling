import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.api import VAR
from scipy import stats

def run_granger_causality(df, target_col='Term_Premium', max_lag=12):
    """
    Performs Granger Causality tests to see if Macro variables predict TP.
    """
    print(f"\n--- [1] Granger Causality Test (Target: {target_col}) ---")
    results = []
    
    # We use differenced data for Granger because it requires stationarity
    df_diff = df.diff().dropna()
    
    for col in df.columns:
        if col == target_col:
            continue
        
        print(f"Testing: {col} -> {target_col}")
        # Test if 'col' Granger-causes 'target_col'
        test_res = grangercausalitytests(df_diff[[target_col, col]], maxlag=max_lag, verbose=False)
        
        # Get the p-value for the best lag (using SSR based F-test)
        min_p = min([test_res[i+1][0]['ssr_ftest'][1] for i in range(max_lag)])
        
        results.append({
            "Cause": col,
            "Target": target_col,
            "Min P-Value": f"{min_p:.4f}",
            "Significant?": "YES" if min_p < 0.05 else "NO"
        })
        
    res_df = pd.DataFrame(results)
    print(res_df)
    return res_df

def run_variance_decomposition(df, output_dir="outputs", periods=24):
    """
    Calculates Forecast Error Variance Decomposition (FEVD).
    Shows how much of TP's variance is explained by each macro shock.
    """
    print("\n--- [2] Variance Decomposition (FEVD) ---")
    df_diff = df.diff().dropna()
    model = VAR(df_diff)
    results = model.fit(maxlags=12, ic='aic')
    
    fevd = results.fevd(periods=periods)
    
    # Plot FEVD for Term_Premium
    fig = fevd.plot(figsize=(10, 6))
    plt.title(f"FEVD: Proportion of Variance Explained for Term Premium")
    plt.savefig(os.path.join(output_dir, "fevd_term_premium.png"))
    plt.close()
    
    # Summary for the report (at the end of the horizon)
    tp_idx = df_diff.columns.get_loc('Term_Premium')
    final_decomp = fevd.decomp[tp_idx][-1] # Decomposition at the last period
    
    decomp_dict = {col: f"{val*100:.2f}%" for col, val in zip(df_diff.columns, final_decomp)}
    print("Variance Decomposition at 24-month horizon:")
    print(decomp_dict)
    return decomp_dict

def run_chow_test(df, break_date="2020-01-01", target_col='Term_Premium'):
    """
    Performs a Chow Test to detect a structural break at the given date.
    """
    print(f"\n--- [3] Structural Break Test (Chow Test at {break_date}) ---")
    
    df['const'] = 1
    x_cols = ['const', 'INF_LEVEL_lag1', 'INF_UNCERTAIN_lag1', 'UNRATE_lag1', 'M2_GROWTH_lag1']
    x_cols = [c for c in x_cols if c in df.columns]
    
    # 1. Full Model
    full_model = sm.OLS(df[target_col], df[x_cols]).fit()
    rss_pooled = full_model.ssr
    
    # 2. Split Data
    pre_break = df[df.index < break_date]
    post_break = df[df.index >= break_date]
    
    if len(pre_break) < len(x_cols) or len(post_break) < len(x_cols):
        print("Not enough data points for Chow Test.")
        return None
        
    model_pre = sm.OLS(pre_break[target_col], pre_break[x_cols]).fit()
    model_post = sm.OLS(post_break[target_col], post_break[x_cols]).fit()
    
    rss_pre = model_pre.ssr
    rss_post = model_post.ssr
    
    # 3. F-statistic Calculation
    k = len(x_cols)
    n = len(df)
    f_stat = ((rss_pooled - (rss_pre + rss_post)) / k) / ((rss_pre + rss_post) / (n - 2*k))
    p_value = 1 - stats.f.cdf(f_stat, k, n - 2*k)
    
    print(f"Chow F-statistic: {f_stat:.4f}")
    print(f"P-value: {p_value:.4e}")
    
    result = {
        "F-statistic": f_stat,
        "P-value": p_value,
        "Break Detected?": "YES" if p_value < 0.05 else "NO"
    }
    return result

def run_all_advanced_analysis(merged_csv="outputs/macro_tp_merged.csv", output_dir="outputs"):
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found.")
        return

    df = pd.read_csv(merged_csv, index_col=0, parse_dates=True)
    # Core variables for testing
    core_cols = ['Term_Premium', 'INF_LEVEL', 'INF_UNCERTAIN', 'UNRATE', 'M2_GROWTH']
    core_cols = [c for c in core_cols if c in df.columns]
    df_core = df[core_cols].dropna()

    # 1. Granger
    granger_res = run_granger_causality(df_core)
    
    # 2. FEVD
    fevd_res = run_variance_decomposition(df_core, output_dir)
    
    # 3. Chow Test
    chow_res = run_chow_test(df)

    # 4. Save to Report
    report_path = os.path.join(output_dir, "advanced_econometric_report.txt")
    with open(report_path, "w") as f:
        f.write("="*60 + "\n")
        f.write("PHASE 6: ADVANCED ECONOMETRIC RIGOR (SCI/SCOPUS LEVEL)\n")
        f.write("="*60 + "\n\n")
        
        f.write("--- [1] Granger Causality Test Results ---\n")
        f.write(granger_res.to_string(index=False))
        f.write("\n\n--- [2] Variance Decomposition (at 24 months) ---\n")
        for k, v in fevd_res.items():
            f.write(f"{k:20}: {v}\n")
            
        f.write("\n--- [3] Structural Break (Chow Test: 2020-01-01) ---\n")
        if chow_res:
            f.write(f"F-statistic: {chow_res['F-statistic']:.4f}\n")
            f.write(f"P-value    : {chow_res['P-value']:.4e}\n")
            f.write(f"Result     : {chow_res['Break Detected?']}\n")
            
    print(f"\nAdvanced analysis complete. Report saved to: {report_path}")
    print("FEVD plot saved to outputs/fevd_term_premium.png")

if __name__ == "__main__":
    run_all_advanced_analysis()
