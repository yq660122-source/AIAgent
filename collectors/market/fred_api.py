import os
import json
import requests
from datetime import datetime

# ======================
# API KEY
# ======================

FRED_API_KEY = "2bac9607b4b2e991e610838fae24637c"
CACHE_DIR = "data/cache"

print("FRED_API_KEY =", FRED_API_KEY)
#
def save_cache(series_id, data):

    try:

        os.makedirs(CACHE_DIR, exist_ok=True)

        cache_file = os.path.join(
            CACHE_DIR,
            f"{series_id}.json"
        )

        with open(
            cache_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(data, f)

    except Exception as e:

        print(f"CACHE SAVE ERROR: {e}")


def load_cache(series_id):

    try:

        cache_file = os.path.join(
            CACHE_DIR,
            f"{series_id}.json"
        )

        if not os.path.exists(cache_file):
            return None

        with open(
            cache_file,
            "r",
            encoding="utf-8"
        ) as f:

            return json.load(f)

    except Exception as e:

        print(f"CACHE LOAD ERROR: {e}")

        return None

# ======================
# FRED 数据抓取
# ======================

def get_fred_latest(series_id, limit=90):

    url = (
        f"https://api.stlouisfed.org/fred/series/observations"
        f"?series_id={series_id}"
        f"&api_key={FRED_API_KEY}"
        f"&file_type=json"
        f"&sort_order=desc"
        f"&limit={limit}"
    )

    try:

        resp = requests.get(
            url,
            timeout=20
        ).json()

        obs = [
            o for o in resp.get("observations", [])
            if o["value"] != "."
        ]
        #只保留最近90天的数据，避免过多历史数据导致性能问题
        obs = obs[:limit]

        if not obs:
            return None, None, [], None

        history = [
            (o["date"], float(o["value"]))
            for o in obs
        ]

        history.reverse()

        fetch_time = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cache_data = {

    "date": obs[0]["date"],

    "value": float(obs[0]["value"]),

    "history": history,

    "fetch_time": fetch_time

}

        save_cache(series_id, cache_data)

        return (
            obs[0]["date"],
            float(obs[0]["value"]),
            history,
            fetch_time
        )

    except Exception as e:

      print(f"FRED ERROR: {e}")

    cache = load_cache(series_id)

    if cache:

        print(f"USING CACHE: {series_id}")

        return (

            cache["date"],

            cache["value"],

            cache["history"],

            cache["fetch_time"]

        )

    return None, None, [], None