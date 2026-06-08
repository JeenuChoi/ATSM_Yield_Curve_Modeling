import requests
import pandas as pd

api_key = "5f20038c0a1a07a9bebd3013b53c5ca2"
stdate = "2020-05-11"
eddate = "2025-05-11"


def get_result(api_key: str, stdate: str, eddate: str, series_id: str):
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": api_key,
        "file_type": "json",
        "frequency": "m",
        "observation_start": stdate,
        "observation_end": eddate
    }

    res = requests.get(url, params=params)
    res.raise_for_status()

    df = pd.DataFrame(res.json()["observations"], columns=["date", "value"])
    df.columns = ["date", series_id]

    df["date"] = pd.to_datetime(df["date"])
    df[series_id] = df[series_id].astype(float)

    return df


df_gs05 = get_result(api_key, stdate, eddate, "CPILFESL")
print(df_gs05)