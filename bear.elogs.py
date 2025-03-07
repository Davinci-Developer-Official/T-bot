import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta

# Initialize MT5
if not mt5.initialize():
    print("MT5 initialization failed")
    mt5.shutdown()
    exit()

# Define the time range (last 30 days)
end_time = datetime.now()
start_time = end_time - timedelta(days=30)

# Fetch trade history
trades = mt5.history_deals_get(start_time, end_time)

if trades is None or len(trades) == 0:
    print("No trade history found")
    mt5.shutdown()
    exit()

# Convert trade history to Pandas DataFrame
df = pd.DataFrame([trade._asdict() for trade in trades])

# 🔹 Filter bearish trades (profit < 0)
bearish_trades = df[df['profit'] < 0]

# Save to CSV
bearish_trades.to_csv("mt5_bearish_trades.csv", index=False)
print("Bearish trade history saved to mt5_bearish_trades.csv")

# Shutdown MT5
mt5.shutdown()
