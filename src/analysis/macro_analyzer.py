import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import statsmodels.api as sm
from src.data.macro_loader import fetch_macro_data, process_inflation_uncertainty

def run_regression(df, y_col, x_cols, title="Regression Results"):
    """Helper function to run OLS regression and print summary."""
    y = df[y_col]
    X = df[x_cols]
    X = sm.add_constant(X)
    
    model = sm.OLS(y, X).fit()
    print(f"\n--- {title} ---")
    print(model.summary())
    return model

def run_macro_tp_analysis(tp_csv_path="outputs/term_premiums.csv", output_dir="outputs"):
    """
    Integrates Term Premium data with Macro variables and performs regression analysis.
    Designed to be called as part of the main pipeline.
    """
    print("\n--- Starting Macro-TP Analysis (Phase 3 Integration) ---")
    
    # 1. Load Term Premium data
    if not os.path.exists(tp_csv_path):
        print(f"Error: {tp_csv_path} not found. Skipping macro analysis.")
        return
    
    tp_df = pd.read_csv(tp_csv_path, index_col=0, parse_dates=True)
    # Target 10Y Term Premium
    target_col = '10.0' if '10.0' in tp_df.columns else tp_df.columns[-1]
    tp_series = tp_df[target_col].rename('Term_Premium')
    
    # 2. Fetch Macro Data (Uses internal caching)
    start_date = tp_df.index.min().strftime("%Y-%m-%d")
    macro_df = fetch_macro_data(start_date=start_date)
    
    if macro_df is None:
        print("Failed to fetch or load macro data. Skipping macro analysis.")
        return
    
    # 3. Process Uncertainty, Levels, and Growths
    macro_df = process_inflation_uncertainty(macro_df)
    
    # Add Growth rates for M2 and INDPRO (Year-over-Year)
    if 'M2' in macro_df.columns:
        macro_df['M2_GROWTH'] = macro_df['M2'].pct_change(12)
    if 'INDPRO' in macro_df.columns:
        macro_df['INDPRO_GROWTH'] = macro_df['INDPRO'].pct_change(12)
    
    # 4. Merge Data
    merged = pd.merge(tp_series, macro_df, left_index=True, right_index=True, how='inner')
    
    # 5. Apply Lags (Information available with a delay)
    for col in macro_df.columns:
        merged[f"{col}_lag1"] = merged[col].shift(1)
    
    merged = merged.dropna()
    
    # 6. Save merged data
    merged_path = os.path.join(output_dir, "macro_tp_merged.csv")
    merged.to_csv(merged_path)
    print(f"Analysis data saved to {merged_path}")
    
    # 7. Regression Analysis - Expanded with M2 and INDPRO
    x_cols = ['INF_LEVEL_lag1', 'INF_UNCERTAIN_lag1', 'UNRATE_lag1', 'M2_GROWTH_lag1', 'INDPRO_GROWTH_lag1']
    full_model = run_regression(merged, 'Term_Premium', x_cols, "Full Sample Regression (Expanded)")
    
    # Regime Split
    covid_split = pd.Timestamp("2020-01-01")
    pre_covid = merged[merged.index < covid_split]
    post_covid = merged[merged.index >= covid_split]
    
    pre_model = None
    post_model = None
    if len(pre_covid) > 10 and len(post_covid) > 10:
        pre_model = run_regression(pre_covid, 'Term_Premium', x_cols, "Pre-COVID Sample")
        post_model = run_regression(post_covid, 'Term_Premium', x_cols, "Post-COVID Sample")
    
    # 8. Visualizations
    # Plot 1: Uncertainty vs Term Premium
    plt.figure(figsize=(12, 6))
    ax1 = plt.gca()
    ax2 = ax1.twinx()
    
    lns1 = ax1.plot(merged.index, merged['Term_Premium'] * 100, color='red', label='10Y Term Premium (%)')
    lns2 = ax2.plot(merged.index, merged['INF_UNCERTAIN_lag1'], color='blue', label='Inflation Uncertainty (Lag1)')
    
    ax1.set_ylabel('Term Premium (%)')
    ax2.set_ylabel('Inflation Uncertainty')
    plt.title('Inflation Uncertainty vs. 10Y Term Premium')
    ax1.grid(True, linestyle=':', alpha=0.6)
    lns = lns1 + lns2
    labs = [l.get_label() for l in lns]
    ax1.legend(lns, labs, loc='upper left')
    plt.savefig(os.path.join(output_dir, "uncertainty_vs_tp.png"))
    plt.close()
    
    # 9. Update Report
    report_path = os.path.join(output_dir, "final_paper_report.txt")
    with open(report_path, "a") as f:
        f.write("\n\n" + "="*50 + "\n")
        f.write("PHASE 3: MACRO-TP ANALYSIS RESULTS\n")
        f.write("="*50 + "\n")
        f.write(f"Sample Period: {merged.index.min().date()} to {merged.index.max().date()}\n")
        f.write(f"Full Sample R-squared: {full_model.rsquared:.4f}\n")
        if pre_model and post_model:
            f.write(f"Pre-COVID R-squared: {pre_model.rsquared:.4f}\n")
            f.write(f"Post-COVID R-squared: {post_model.rsquared:.4f}\n")
            f.write("\n--- Post-COVID Regression Coefficients ---\n")
            f.write(post_model.params.to_string())
            
    print(f"Macro analysis completed. Report updated at {report_path}")

if __name__ == "__main__":
    # Allow standalone run for testing
    run_macro_tp_analysis()
