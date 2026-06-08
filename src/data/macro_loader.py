'''
api key = 5f20038c0a1a07a9bebd3013b53c5ca2
'''

import pandas as pd
import numpy as np
import datetime
import requests
import os

def fetch_macro_data(start_date="1990-01-01", end_date=None, cache_path="data/raw_macro_cache.csv"):
    """
    Fetches key macro variables from FRED using the official JSON API.
    Includes local caching logic for reliability.
    """
    api_key = "5f20038c0a1a07a9bebd3013b53c5ca2"
    
    # Series mapping: Display Name -> FRED ID
    series_map = {
        'INDPRO': 'INDPRO',
        'M2': 'M2SL',
        'CPI': 'CPIAUCSL',
        'UNRATE': 'UNRATE',
        'NBER_REC': 'USREC'     
    }
    
    if end_date is None:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # --- Check Cache First ---
    if os.path.exists(cache_path):
        df_cache = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        # Check if ALL required columns are present in cache
        if all(col in df_cache.columns for col in series_map.keys()):
            print(f"All series found in cache: {list(series_map.keys())}")
            mask = (df_cache.index >= pd.to_datetime(start_date)) & (df_cache.index <= pd.to_datetime(end_date))
            return df_cache.loc[mask]
        else:
            print("Cache is outdated (missing series). Forcing API refresh...")

    print(f"Fetching macro data from FRED API: {list(series_map.keys())}...")
    
    all_series = []
    url = "https://api.stlouisfed.org/fred/series/observations"
    
    api_success = True
    for name, fred_id in series_map.items():
        params = {
            "series_id": fred_id,
            "api_key": api_key,
            "file_type": "json",
            "observation_start": start_date,
            "observation_end": end_date
        }
        
        # Series like ACMTP10 might not support 'frequency=m'
        if name not in ['ACM_TP10', 'NBER_REC']:
            params["frequency"] = "m"
            
        try:
            res = requests.get(url, params=params, timeout=10)
            if res.status_code != 200:
                print(f"Error fetching {name} ({fred_id}): HTTP {res.status_code} - {res.text}")
                api_success = False
                continue 
            
            data = res.json().get("observations", [])
            if not data:
                print(f"Warning: No data found for {name} ({fred_id})")
                continue
                
            df_temp = pd.DataFrame(data)[["date", "value"]]
            df_temp.columns = ["DATE", name]
            df_temp["DATE"] = pd.to_datetime(df_temp["DATE"])
            df_temp[name] = pd.to_numeric(df_temp[name], errors='coerce')
            df_temp.set_index("DATE", inplace=True)
            
            # Resample to monthly if it was a daily series
            if name in ['ACM_TP10', 'NBER_REC']:
                df_temp = df_temp.resample('ME').last()
                
            all_series.append(df_temp)
            print(f"Successfully fetched {name} ({fred_id})")
            
        except Exception as e:
            print(f"Failed to fetch {name} ({fred_id}): {e}")
            api_success = False
            break # Exit loop to trigger fallback if any series fails
            
    if all_series:
        # Merge whatever we successfully fetched
        df = pd.concat(all_series, axis=1)
        df.index = df.index + pd.offsets.MonthEnd(0)
        df = df[~df.index.duplicated(keep='last')].sort_index()
        df = df.dropna(how='all')
        
        # Save to cache (update existing cache if present)
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        if os.path.exists(cache_path):
            existing_cache = pd.read_csv(cache_path, index_col=0, parse_dates=True)
            df = df.combine_first(existing_cache) # Keep new, fill with old
            
        df.to_csv(cache_path)
        print(f"Macro data updated and cached to {cache_path}")
        
        if api_success:
            return df
        else:
            print("API fetch was incomplete, but successful series were cached.")

    # Fallback to cache if no new data fetched
    print("Attempting to load macro data from local cache...")
    if os.path.exists(cache_path):
        df_cache = pd.read_csv(cache_path, index_col=0, parse_dates=True)
        # Filter by requested dates
        mask = (df_cache.index >= pd.to_datetime(start_date)) & (df_cache.index <= pd.to_datetime(end_date))
        df_filtered = df_cache.loc[mask]
        if not df_filtered.empty:
            print(f"Successfully loaded cached data (Shape: {df_filtered.shape})")
            return df_filtered
        else:
            print("Cache exists but is empty for the requested date range.")
    else:
        print("No local cache found.")
        
    return None

def process_inflation_uncertainty(macro_df, window=12):
    """
    Calculates inflation level (YoY change) and uncertainty (rolling std of monthly changes).
    """
    if 'CPI' not in macro_df.columns:
        print("Warning: 'CPI' column not found. Skipping uncertainty calculation.")
        return macro_df
        
    # 1. Inflation Level (Year-over-Year % change)
    # Using log-diff for better statistical properties or simple pct_change
    macro_df['INF_LEVEL'] = macro_df['CPI'].pct_change(12)
    
    # 2. Inflation Uncertainty (Rolling volatility of monthly log-changes)
    # Typically uncertainty is defined as the rolling std of the shock to inflation
    monthly_inf = np.log(macro_df['CPI']).diff()
    macro_df['INF_UNCERTAIN'] = monthly_inf.rolling(window=window).std()
    
    return macro_df

if __name__ == "__main__":
    # Test script
    test_df = fetch_macro_data(start_date="2015-01-01")
    if test_df is not None:
        test_df = process_inflation_uncertainty(test_df)
        print("\n--- Test Result Summary ---")
        print(test_df.tail())
        print(f"\nShape: {test_df.shape}")
    else:
        print("Test failed.")
