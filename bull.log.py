import pandas as pd

df = pd.read_csv("mt5_trade_history.csv",)

bullish_trades = df[df["profit"]>0]

bullish_trades.to_csv("bullish_trades.csv", index=False)

print("bullish logs are saved as bullish_trades.csv")

