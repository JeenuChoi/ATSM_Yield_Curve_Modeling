import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
import os

def run_rolling_beta_analysis(merged_csv="outputs/macro_tp_merged.csv", output_dir="outputs"):
    print("\n--- Running Rolling Beta Analysis (Verification) ---")
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found.")
        return

    df = pd.read_csv(merged_csv, index_col=0, parse_dates=True)
    
    # Target: Term_Premium
    # Features: INF_UNCERTAIN_lag1 (and others if needed)
    y = df['Term_Premium']
    X = sm.add_constant(df[['INF_UNCERTAIN_lag1', 'INF_LEVEL_lag1', 'UNRATE_lag1', 'M2_GROWTH_lag1']])
    
    # 48-month rolling window as mentioned in the report
    window = 48
    rols = RollingOLS(y, X, window=window)
    rres = rols.fit()
    
    # Get the coefficients and t-stats for INF_UNCERTAIN_lag1
    betas = rres.params['INF_UNCERTAIN_lag1']
    # t-stats calculation: params / bse
    t_stats = rres.params['INF_UNCERTAIN_lag1'] / rres.bse['INF_UNCERTAIN_lag1']
    
    print(f"Latest Rolling Beta (INF_UNCERTAIN): {betas.iloc[-1]:.4f}")
    print(f"Latest t-stat (INF_UNCERTAIN): {t_stats.iloc[-1]:.4f}")
    print(f"Peak Rolling Beta: {betas.max():.4f} at {betas.idxmax()}")
    
    # Plotting
    plt.figure(figsize=(12, 6))
    plt.plot(betas, label='Rolling Beta (Inflation Uncertainty)', color='tab:blue', linewidth=2)
    plt.axhline(0, color='black', linestyle='--', alpha=0.3)
    
    # Significance threshold (approx 2 for 95%)
    # plt.fill_between(betas.index, 0, betas, where=(t_stats.abs() > 2), color='green', alpha=0.1, label='Significant (|t| > 2)')
    
    plt.title(f'Rolling Regression Beta: Inflation Uncertainty -> 10Y Term Premium ({window}-Month Window)')
    plt.ylabel('Regression Coefficient (Beta)')
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    save_path = os.path.join(output_dir, "rolling_risk_shift_VERIFIED.png")
    plt.savefig(save_path)
    print(f"Verified plot saved to {save_path}")

if __name__ == "__main__":
    run_rolling_beta_analysis()
