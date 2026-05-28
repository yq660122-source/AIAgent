from collectors.market.alpha_vantage import (
    get_realtime_price
)

print("TESTING ALPHA VANTAGE...")

data = get_realtime_price("SPY")

print(data)