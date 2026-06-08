import pandas as pd
import numpy as np
import warnings

def load_gsw_data(file_path: str) -> pd.DataFrame:
    """
    Loads GSW zero-coupon yield data from a **cleaned** file path.
    Assumes the file has no header rows and the first row is the column names.
    """
    maturities_to_extract = [1, 2, 3, 5, 7, 10, 20, 30]
    maturity_columns = {f"SVENY{maturity:02d}": float(maturity) for maturity in maturities_to_extract}
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        warnings.warn(f"Failed to load data from {file_path}. Error: {e}")
        return pd.DataFrame()

    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date')
    
    columns_to_select = list(maturity_columns.keys())
    if not all(col in df.columns for col in columns_to_select):
        missing_cols = [col for col in columns_to_select if col not in df.columns]
        warnings.warn(f"The following required columns were not found: {missing_cols}")
        columns_to_select = [col for col in columns_to_select if col in df.columns]
        if not columns_to_select:
            return pd.DataFrame()

    df_selected = df[columns_to_select]
    
    df_monthly = df_selected.resample('ME').last()
    df_monthly = df_monthly.replace('NA', np.nan).astype(float).dropna()
    df_monthly = df_monthly.rename(columns=maturity_columns)
    df_monthly = df_monthly / 100.0
    
    return df_monthly

if __name__ == "__main__":
    print("This script is designed to be imported and used with a cleaned CSV file.")
    print("Please provide a path to the 'feds200628_clean.csv' file.")
