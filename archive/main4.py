import os
from src.analysis.robustness import run_all_robustness

def main4():
    """
    Robustness Checks & Economic Narrative Pipeline.
    Focuses on GARCH alternative proxy, Lag sensitivity, and Rolling correlations.
    """
    print("\n" + "="*60)
    print("--- [MAIN4] ROBUSTNESS & NARRATIVE PIPELINE ---")
    print("="*60)

    # Path to the merged data (Golden Data)
    merged_csv = "outputs/macro_tp_merged.csv"
    
    if not os.path.exists(merged_csv):
        print(f"Error: {merged_csv} not found.")
        print("Please run main2.py/main3.py first.")
        return

    # Run the robustness tests
    try:
        run_all_robustness(merged_csv=merged_csv)
    except Exception as e:
        print(f"Robustness analysis failed: {e}")

    print("\n" + "="*60)
    print("--- [MAIN4] ROBUSTNESS PIPELINE FINISHED ---")
    print("="*60)

if __name__ == "__main__":
    main4()
