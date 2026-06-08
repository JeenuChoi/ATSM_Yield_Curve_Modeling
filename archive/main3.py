import os
from src.analysis.advanced_econometrics import run_all_advanced_analysis

def main3():
    """
    Advanced Statistical Testing Pipeline.
    Focuses on Granger Causality, Variance Decomposition, and Structural Breaks.
    Uses existing 'Golden' merged data to maintain scientific integrity.
    """
    print("\n" + "="*60)
    print("--- [MAIN3] ADVANCED ECONOMETRIC TESTING PIPELINE ---")
    print("="*60)

    # Path to the merged data (Golden Data)
    merged_csv = "outputs/macro_tp_merged.csv"
    
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found.")
        print("Please run main2.py first to generate the merged dataset.")
        return

    # Run the advanced tests
    try:
        run_all_advanced_analysis(merged_csv=merged_csv)
    except Exception as e:
        print(f"Advanced analysis failed: {e}")

    print("\n" + "="*60)
    print("--- [MAIN3] ADVANCED PIPELINE FINISHED ---")
    print("="*60)

if __name__ == "__main__":
    main3()
