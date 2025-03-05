import MetaTrader5 as mt5
import time



# import datetime

import backtrader as bt

class TestStrategy(bt.Strategy):
    def next(self):
        print(f"Current price: {self.data.close[0]}")

# # Create a backtest engine
# cerebro = bt.Cerebro()
# data = bt.feeds.PandasData(dataname=pd.DataFrame({'close': [100, 102, 101, 105, 110]}))
# cerebro.adddata(data)
# cerebro.addstrategy(TestStrategy)
# cerebro.run()

# connection info ie demo info
ACCOUNT = 90554773
PASSWORD = "G-KoM0Or"
SERVER = "MetaQuotes-Demo" #"TrDyK*E8"

active=False

# checking account balance
account_info = mt5.account_info()
if account_info is not None:
    print(f"💰 Free Margin: {account_info.margin_free}")
    if account_info.margin_free < 10:  # adjust according to the amount you consider required by you or your broker
        print("❌ Not enough free margin to place a trade!")

 #initializing metatrader 5;
if  mt5.initialize():
    print("success while initializing MT5")
    # login()
    # quit()
else:
    print("Failed while initializing MT5: {mt5.last_error()}")
    quit()

# Trading parameters
symbol = "EURUSD"
spread_percentage = 0.05 # adjustable
lot_size= 0.01 # adjustable

# getting the spread
def get_spread():
    print("loading....")
    """bid and ask prices for EURO/USD"""
    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        print(f"failed to get tick data: {mt5.last_error()}")
        return
    # data
    bid = tick.bid
    ask = tick.ask
    spread = ask - bid
    print(spread)
    return  bid,ask,spread

 # login function
def login():
    check = mt5.login(ACCOUNT,password=PASSWORD,server=SERVER)
    if check:
        print("logged in successfully")
        #print(mt5.symbol_info_tick("EURUSD"))
        get_spread()
    else:
        print("failed to log in ")
        quit()
login()



# # making orders
# def place_orders():
#     """place buy and sell limit orders based on spread"""
#     bid,ask,spread = get_spread()
#
#     buy_price = round(bid-(spread * spread_percentage),5)
#     sell_price = round(bid-(spread*spread_percentage),5)
#
#     print(f"EUR/USD | Bid: {bid} | Ask: {ask} | Spread: {spread}")
#     print(f"placing Buy Limit at {buy_price} ")
#     print(f"placing sell limit at {sell_price} ")
#
#     # Buy Limit Order
#     buy_order = {
#         "action": mt5.TRADE_ACTION_PENDING,
#         "symbol": symbol,
#         "volume": lot_size,
#         "type": mt5.ORDER_TYPE_BUY_LIMIT,
#         "price": buy_price,
#         "sl": ask - 0.0010,  # Stop Loss (10 pip SL)
#         "tp": ask + 0.0020,  # Take Profit (20 pip TP)
#         "deviation": 10,
#         "magic": 1001,
#         "comment": "Market Maker Buy",
#         "type_time": mt5.ORDER_TIME_GTC,  # Good-Till-Cancelled
#         "type_filling": mt5.ORDER_FILLING_IOC,
#     }
#
#     # Sell Limit Order
#     sell_order = {
#         "action": mt5.TRADE_ACTION_PENDING,
#         "symbol": symbol,
#         "volume": lot_size,
#         "type": mt5.ORDER_TYPE_SELL_LIMIT,
#         "price": sell_price,
#         "sl": 0,
#         "tp": 0,
#         "deviation": 10,
#         "magic": 1002,
#         "comment": "Market Maker Sell",
#         "type_time": mt5.ORDER_TIME_GTC,
#         "type_filling": mt5.ORDER_FILLING_IOC,
#     }
#
#     # Send Orders
#     mt5.order_send(buy_order)
#     mt5.order_send(sell_order)


# --- Run Market Maker ---
# while True:
#     try:
#         place_orders()
#         time.sleep(10)  # Adjust frequency
#     except KeyboardInterrupt:
#         print("🛑 Stopping bot.")
#         break

# place_orders()



# place dynamic orders
trade_count = 0
max_trades_per_session = 5
current_session = time.strftime("%Y-%m-%d", time.localtime())


def dynamic_order():
    global trade_count, current_session

    # Check if a new session has started
    new_session = time.strftime("%Y-%m-%d", time.localtime())
    if new_session != current_session:
        trade_count = 0
        current_session = new_session

    if trade_count >= max_trades_per_session:
        print("🚫 Trade limit reached for this session.")
        return
    if trade_count >= max_trades_per_session:
        trade_count = 0  # Reset trade count
        current_session = time.strftime("%Y-%m-%d")  # Start new session

        # Check if there are active trades
    existing_trades = mt5.positions_get(symbol=symbol)
    if existing_trades and len(existing_trades) >= max_trades_per_session:
        print("🚫 Max active trades reached. No new trade placed.")
        return
    bid, ask, spread = get_spread()

    if spread is None:
        return
    else:
        print(f"The spread is: {spread:.5f}")

    # Default values
    order_type = None
    price = None

    if spread <= 0.2:
        print("📌 Using Market Order (Lower Spread)")
        # print()
        order_type = mt5.ORDER_TYPE_BUY
        price = ask  # Market Order uses ask price

    elif spread <= 0.5:  # FIXED CONDITION
        print("📌 Using Buy Limit (Medium Spread)")
        order_type = mt5.ORDER_TYPE_BUY_LIMIT
        price = bid - (spread * 0.5)  # Buy limit at a slight discount

    else:
        print("❌ Spread too high; no trade placed.")
        return  # Stop execution if no trade is made

    # Ensure order_type and price are set before sending the order
    if order_type is not None and price is not None:
        order_request = {
            "action": mt5.TRADE_ACTION_PENDING if order_type != mt5.ORDER_TYPE_BUY else mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type,
            "price": price,
            "sl": ask - 0.0002, # stop loss at 2 pips
            "tp": ask + 0.0005, # take profit at 5 pips
            "deviation": 10,
            "magic": 1001,
            "comment": "Spread-Based Entry",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(order_request)
        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✅ Order placed successfully at {price}")
            trade_count += 1 # increases trades per every successful order
        else:
            print(f"❌ Order failed: {result}")


def count_active_trades(symbol="EURUSD"):
    positions = mt5.positions_get(symbol=symbol)
    return len(positions) if positions else 0


def get_market_data(symbol="EURUSD"):
    """Fetch price and volume data"""
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 50)  # Get last 50 candles
    if rates is None:
        print("❌ Failed to fetch market data.")
        return None
    return rates

# Ensure these functions are defined somewhere
def get_market_data(symbol):
    """Fetch market data for the given symbol."""
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M5, 0, 20)
    if rates is None:
        print(f"❌ No market data retrieved for {symbol}")
        return None
    return [{"close": r["close"], "tick_volume": r["tick_volume"]} for r in rates]

def get_spread():
    """Retrieve current bid, ask, and spread for the symbol."""
    tick = mt5.symbol_info_tick("EURUSD")
    if tick is None:
        print("❌ Failed to retrieve spread data.")
        return None, None, None
    spread = tick.ask - tick.bid
    return tick.bid, tick.ask, spread

def analyze_market_phase(symbol="EURUSD"):
    """Determine if the market is in accumulation or distribution"""
    data = get_market_data(symbol)
    if data is None:
        return None

    close_prices = [bar["close"] for bar in data]
    volumes = [bar["tick_volume"] for bar in data]

    if len(close_prices) < 10 or len(volumes) < 10:
        print("❌ Not enough data points.")
        return None

    recent_close = close_prices[-1]
    recent_volume = volumes[-1]

    avg_volume = sum(volumes[-10:]) / 10  # Last 10 bars avg
    avg_price_change = sum([abs(close_prices[i] - close_prices[i - 1]) for i in range(-10, 0)]) / 10

    print(f"🔍 Recent Close: {recent_close}, Recent Volume: {recent_volume}")
    print(f"📊 Avg Volume: {avg_volume}, Avg Price Change: {avg_price_change}")

    # Accumulation Phase: Rising volume & price stability
    if recent_volume > avg_volume * 1.2 and avg_price_change < (recent_close * 0.002):
        print("✅ Accumulation detected - GOOD for BUY")
        return "BUY"

    # Distribution Phase: Rising volume & price failing to break highs
    if recent_volume > avg_volume * 1.2 and avg_price_change > (recent_close * 0.004):
        print("❌ Distribution detected - AVOID BUY")
        return "SELL"

    print("⚠️ No clear phase detected - WAIT")
    return "HOLD"

def dynamic_orders(symbol="EURUSD", lot_size=0.1):
    global trade_count

    phase = analyze_market_phase(symbol)
    if phase is None or phase == "HOLD":
        print("🚫 No trade signal found.")
        return

    if phase == "SELL":
        print("🚫 Distribution detected. Skipping Buy.")
        return

    bid, ask, spread = get_spread()
    if spread is None:
        return

    print(f"📊 Bid: {bid}, Ask: {ask}, Spread: {spread}")

    order_request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": mt5.ORDER_TYPE_BUY,
        "price": ask,
        "sl": ask - 0.0005,  # Stop loss (5 pips)
        "tp": ask + 0.0010,  # Take profit (10 pips)
        "deviation": 10,
        "magic": 1001,
        "comment": "Volume-Based Buy Entry",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(order_request)
    if result is None:
        print("❌ Order execution failed: No response from server.")
        return

    if result.retcode == mt5.TRADE_RETCODE_DONE:
        print(f"✅ Order placed successfully at {ask}")
        trade_count += 1
    else:
        print(f"❌ Order failed. Error Code: {result.retcode}, Comment: {result.comment}")

# Initialize trading session
trade_count = 0
# Run algorithm in loop
while True:
    active_trades = count_active_trades("EURUSD")  # Adjust symbol if needed

    if active_trades < 5:  # If fewer than 5 trades, allow a new one
        trade_count = active_trades  # Sync trade count with MT5
        dynamic_orders()
    else:
        print(f"🚫 {active_trades}/5 trades active. No new trade placed.")

    time.sleep(10)  # Adjust as needed
