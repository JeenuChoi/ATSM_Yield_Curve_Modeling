import os
from src.analysis.zlb_analysis import run_zlb_workflow

def main5():
    """
    Zero Lower Bound (ZLB) & Shadow Rate Discussion Pipeline.
    Identifies ZLB periods and tests model robustness across regimes.
    """
    print("\n" + "="*60)
    print("--- [MAIN5] ZLB & SHADOW RATE ANALYSIS PIPELINE ---")
    print("="*60)

    # Path to the merged data (Golden Data)
    merged_csv = "outputs/macro_tp_merged.csv"
    
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found. Please run previous main scripts first.")
        return

    # Run the ZLB impact analysis
    try:
        run_zlb_workflow(merged_csv=merged_csv)
    except Exception as e:
        print(f"ZLB analysis failed: {e}")

    print("\n" + "="*60)
    print("--- [MAIN5] ZLB PIPELINE FINISHED ---")
    print("="*60)

if __name__ == "__main__":
    main5()
