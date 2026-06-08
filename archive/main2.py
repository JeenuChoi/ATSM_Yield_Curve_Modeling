import pandas as pd
import numpy as np
import os
from src.analysis.macro_analyzer import run_macro_tp_analysis
from src.analysis.econometrics import run_econometric_analysis
from src.analysis.benchmarking import run_benchmarking

def main2():
    """
    Fixed-Data Pipeline: Skips MLE optimization and uses existing 'Golden' CSVs.
    Perfect for running advanced analysis on already-validated results.
    """
    print("\n" + "="*60)
    print("--- [MAIN2] FIXED-DATA ANALYSIS PIPELINE (Bypassing Optimization) ---")
    print("="*60)

    # 1. Verify existence of golden CSVs
    required_files = ["term_premiums.csv", "fitted_yields.csv", "expected_avg_short_rates.csv"]
    output_dir = "outputs"
    
    missing = [f for f in required_files if not os.path.exists(os.path.join(output_dir, f))]
    
    if missing:
        print(f"Error: Missing required golden CSVs: {missing}")
        print("Please ensure you've restored them to the 'outputs' directory.")
        return

    # 2. Phase 3: Macro-TP Analysis (Integrates TP with Macro)
    print("\n--- Phase 3: Macro-TP Integration ---")
    try:
        run_macro_tp_analysis()
    except Exception as e:
        print(f"Macro analysis failed: {e}")

    # 3. Phase 4: Econometric Rigor (VAR/VECM/IRF/ADF)
    print("\n--- Phase 4: Econometric Analysis (VAR/VECM) ---")
    try:
        run_econometric_analysis()
    except Exception as e:
        print(f"Econometric analysis failed: {e}")

    # 4. Phase 5: Benchmarking (ACM/NBER)
    print("\n--- Phase 5: Benchmarking (ACM/NBER) ---")
    try:
        run_benchmarking()
    except Exception as e:
        print(f"Benchmarking analysis failed: {e}")

    print("\n" + "="*60)
    print("--- [MAIN2] PIPELINE FINISHED. RESULTS REFRESHED. ---")
    print("="*60)

if __name__ == "__main__":
    main2()
