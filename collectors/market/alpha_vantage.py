import os
import requests

# ======================
# API KEY
# ======================

ALPHA_VANTAGE_KEY = os.getenv(
    "ALPHA_VANTAGE_KEY"
)

# ======================
# 实时行情
# ======================

def get_realtime_price(symbol):

    url = (
        "https://www.alphavantage.co/query"
        f"?function=GLOBAL_QUOTE"
        f"&symbol={symbol}"
        f"&apikey={ALPHA_VANTAGE_KEY}"
    )

    try:

        response = requests.get(
            url,
            timeout=20
        )

        data = response.json()

        # ======================
        # API限制检测
        # ======================

        if "Note" in data:

            print("ALPHA API LIMIT REACHED")

            return None

        quote = data.get("Global Quote", {})

        if not quote:

            print("NO DATA RETURNED")

            return None

        return {

            "symbol": symbol,

            "price": float(
                quote["05. price"]
            ),

            "change_percent": quote[
                "10. change percent"
            ]
        }

    except Exception as e:

        print(f"ALPHA ERROR: {e}")

        return None