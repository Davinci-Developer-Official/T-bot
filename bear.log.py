import pandas as pd

# Load the dataset (Replace with your actual file path if needed)
df = pd.read_csv("mt5_trade_history.csv")

# Filter only bearish trades (profit < 0)
bearish_trades = df[df['profit'] < 0]

# Save to a new CSV file
bearish_trades.to_csv("bearish_trades.csv", index=False)

print("Bearish trades have been saved to bearish_trades.csv")
