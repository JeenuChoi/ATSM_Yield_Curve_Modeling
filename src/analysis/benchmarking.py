import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from src.data.macro_loader import fetch_macro_data

def run_benchmarking(tp_csv_path="outputs/term_premiums.csv", output_dir="outputs"):
    """
    Compares our model's Term Premium with NY Fed ACM model (local CSVs for multiple maturities) 
    and NBER recession dates.
    """
    print("\n--- [Phase 5] Starting Multi-Maturity Benchmarking & Recession Analysis ---")
    
    # 1. Load Our Term Premium Data
    if not os.path.exists(tp_csv_path):
        tp_csv_path = "Desktop/ATSM_Project/outputs/term_premiums.csv"
        if not os.path.exists(tp_csv_path):
            print(f"Error: {tp_csv_path} not found.")
            return

    our_tp_df = pd.read_csv(tp_csv_path, index_col=0, parse_dates=True)
    
    # 2. Load Local ACM Data for available maturities (2Y to 10Y)
    maturities = [2, 3, 4, 5, 6, 7, 8, 9, 10] 
    acm_data_list = []
    
    for m in maturities:
        # Using relative path from project root
        acm_path = f"data/THREEFYTP{m}.csv"
        if os.path.exists(acm_path):
            print(f"Loading local ACM {m}Y data from {acm_path}...")
            df = pd.read_csv(acm_path, index_col=0, parse_dates=True)
            df = df.resample('ME').last()
            df = df.rename(columns={f'THREEFYTP{m}': f'ACM_TP_{m}Y'})
            acm_data_list.append(df)
        else:
            # Try alternate path if not found (for standalone execution)
            alt_path = f"Desktop/ATSM_Project/data/THREEFYTP{m}.csv"
            if os.path.exists(alt_path):
                print(f"Loading local ACM {m}Y data from {alt_path}...")
                df = pd.read_csv(alt_path, index_col=0, parse_dates=True)
                df = df.resample('ME').last()
                df = df.rename(columns={f'THREEFYTP{m}': f'ACM_TP_{m}Y'})
                acm_data_list.append(df)
            else:
                print(f"Warning: Local ACM file {acm_path} not found. Skipping {m}Y.")

    # 3. Fetch NBER Recession Data
    start_date = our_tp_df.index.min().strftime("%Y-%m-%d")
    macro_df = fetch_macro_data(start_date=start_date)
    
    # 4. Merge and Analyze Correlations
    report_path = os.path.join(output_dir, "benchmarking_report.txt")
    with open(report_path, "w") as f:
        f.write("="*60 + "\n")
        f.write("PHASE 5: MULTI-MATURITY BENCHMARKING (OURS vs ACM)\n")
        f.write("="*60 + "\n")
        f.write(f"Sample Period: {our_tp_df.index.min().date()} to {our_tp_df.index.max().date()}\n\n")
        f.write(f"{'Maturity':<10} | {'Correlation':<12}\n")
        f.write("-" * 25 + "\n")

        # Correlation Table
        correlations = {}
        for m in maturities:
            col_name = f"{m}.0"
            acm_col = f"ACM_TP_{m}Y"
            
            if col_name in our_tp_df.columns and any(acm_col in df.columns for df in acm_data_list):
                # Find the specific ACM df
                target_acm_df = next(df for df in acm_data_list if acm_col in df.columns)
                
                # Merge individual maturity
                merged_m = pd.DataFrame(our_tp_df[col_name]).join(target_acm_df, how='inner')
                
                # Scale check
                ours = merged_m[col_name]
                if ours.abs().mean() < 0.1: ours *= 100
                
                # IMPORTANT: Local ACM files have opposite sign (-0.97 correlation)
                # Multiply by -1 to align with our model's positive TP definition
                acm = -1.0 * merged_m[acm_col]
                if acm.abs().mean() < 0.1: acm *= 100
                
                corr = ours.corr(acm)
                correlations[m] = corr
                f.write(f"{m:>8}Y | {corr:>11.4f}\n")
                print(f"Maturity {m}Y Correlation: {corr:.4f}")

        # 5. Detailed Plot for 10Y (Standard Benchmark)
        if 10 in correlations:
            target_10y_acm = next(df for df in acm_data_list if 'ACM_TP_10Y' in df.columns)
            merged_final = pd.DataFrame(our_tp_df['10.0']).join(target_10y_acm, how='inner')
            
            if macro_df is not None and 'NBER_REC' in macro_df.columns:
                merged_final = merged_final.join(macro_df['NBER_REC'], how='inner')
            
            # Shifting to Percentages for Plotting
            if merged_final['10.0'].abs().mean() < 0.1: merged_final['10.0'] *= 100
            
            # Align sign for ACM
            merged_final['ACM_TP_10Y'] = -1.0 * merged_final['ACM_TP_10Y']
            if merged_final['ACM_TP_10Y'].abs().mean() < 0.1: merged_final['ACM_TP_10Y'] *= 100

            plt.figure(figsize=(14, 7))
            plt.plot(merged_final.index, merged_final['10.0'], label='Our Model (10Y TP)', color='blue', linewidth=2)
            plt.plot(merged_final.index, merged_final['ACM_TP_10Y'], label='NY Fed ACM (10Y TP)', color='red', linestyle='--', alpha=0.7)
            
            if 'NBER_REC' in merged_final.columns:
                rec_starts = merged_final.index[merged_final['NBER_REC'].diff() == 1]
                rec_ends = merged_final.index[merged_final['NBER_REC'].diff() == -1]
                if merged_final['NBER_REC'].iloc[0] == 1: rec_starts = rec_starts.insert(0, merged_final.index[0])
                if merged_final['NBER_REC'].iloc[-1] == 1: rec_ends = rec_ends.append(pd.Index([merged_final.index[-1]]))
                for i, (s, e) in enumerate(zip(rec_starts, rec_ends)):
                    plt.axvspan(s, e, color='gray', alpha=0.2, label='NBER Recession' if i == 0 else "")

            plt.title('10Y Term Premium Benchmarking with NBER Recessions', fontsize=14)
            plt.ylabel('Term Premium (%)')
            plt.legend(loc='best')
            plt.grid(True, linestyle=':', alpha=0.6)
            plt.savefig(os.path.join(output_dir, "benchmarking_acm_nber.png"))
            plt.close()
            
            # Recession Stats for 10Y
            if 'NBER_REC' in merged_final.columns:
                f.write("\n--- 10Y Term Premium Stats: Recession vs Expansion ---\n")
                f.write(merged_final.groupby('NBER_REC')['10.0'].describe().to_string())

    print(f"\nAnalysis complete. Results saved to {output_dir}/")
    print(f"Report: {report_path}")
        
    print(f"Benchmarking report saved to: {report_path}")

if __name__ == "__main__":
    run_benchmarking()
