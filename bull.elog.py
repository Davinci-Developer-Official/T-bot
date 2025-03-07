import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    mt5.shutdown()
    exit()

# Define the time range
end_time = datetime.now()
start_time = end_time - timedelta(days=30)

# Fetch trade history
trades = mt5.history_deals_get(start_time, end_time)

if trades is None:
    print("No trade history found")
    mt5.shutdown()
    exit()

# 🔹 Check what fields exist in the retrieved data
first_trade = trades[0]._asdict() if trades else {}
print("Trade Fields:", first_trade.keys())  # 🔍 Inspect column names

# Convert trade history to Pandas DataFrame dynamically
df = pd.DataFrame([trade._asdict() for trade in trades])

# Save to CSV
df.to_csv("mt5_trade_bull_history.csv", index=False)
print("Trade history saved to mt5_trade_history.csv")

# Shutdown MT5
mt5.shutdown()
