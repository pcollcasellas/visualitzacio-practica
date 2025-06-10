import requests
import json
import pandas as pd
from datetime import datetime, timedelta

url = "https://castellscat.cat/api/actuacions"


def get_intervals():
    intervals = []
    start = datetime(1926, 1, 1)
    first_end = datetime(1995, 1, 1)
    intervals.append((start, first_end))
    current_start = first_end
    today = datetime.today()
    while current_start < today:
        next_end = min(
            current_start.replace(year=current_start.year + 5), today + timedelta(days=1)
        )
        intervals.append((current_start, next_end))
        current_start = next_end
    return intervals


columns = [
    "id",
    "date",
    "ronda",
    "intent",
    "position",
    "diada_name",
    "show_longitude",
    "show_latitude",
    "colla_is_university",
    "colla_is_training",
    "colla_is_discontinuous",
    "colla_is_international",
    "colla_id_string",
    "colla_name",
    "colla_pantone",
    "colla_active",
    "castell_type_name",
    "castell_type_name_short",
    "castell_type_estructura",
    "castell_type_alcada",
    "castell_result_name",
    "city_name",
    "city_country_id",
]

headers = {"User-Agent": "curl/7.68.0"}

all_dfs = []


def log(msg):
    print(f"[{datetime.now().isoformat(sep=' ', timespec='seconds')}] {msg}")


for date_start, date_end in get_intervals():
    params = {
        "api_token_id": "XXXXX",
        "api_token_key": "XXXXX",
        "date_start": date_start.strftime("%Y-%m-%d"),
        "date_end": date_end.strftime("%Y-%m-%d"),
        "json": "true",
    }
    log(f"Fetching {params['date_start']} to {params['date_end']}")
    response = requests.get(url, params=params, headers=headers)
    log(f"Response status code: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            if "results" in data and data["results"]:
                df_results = pd.json_normalize(data["results"], sep="_")
                df = df_results[columns].copy()
                all_dfs.append(df)
        except ValueError:
            log("Response is not JSON:")
            log(response.text)
    else:
        log(f"Request failed with status code {response.status_code}")
        log(response.text)

if all_dfs:
    final_df = pd.concat(all_dfs, ignore_index=True)
    final_df.to_csv("actuacions_completes.csv", index=False, encoding="utf-8")
    log("Desat a actuacions_completes.csv")
else:
    log("No data fetched.")
