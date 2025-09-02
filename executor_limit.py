# executor_limit.py
from binance_client import get_binance_client, fetch_live_klines
import risk_management
import time
import csv
from datetime import datetime
import os

# Configuration
SYMBOL = 'BTCUSDT'
TIMEFRAME = '1m'
LENGTH = 1  # channel length
LOG_FILE = "trade_log.csv"

client = get_binance_client()

# ----------------- Logger -----------------
def log_trade(order, side=None, stop_price=None, quantity=None):
    """Logs an order (STOP_LOSS, MARKET, LIMIT, etc) to CSV file."""

    fields = [
        "time", "symbol", "side", "type", "status",
        "orderId", "price", "stopPrice", "executedQty", "origQty"
    ]

    # Fallback values if Binance response misses some fields
    row = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": order.get("symbol", ""),
        "side": order.get("side", side if side else ""),
        "type": order.get("type", ""),
        "status": order.get("status", ""),
        "orderId": order.get("orderId", ""),
        "price": order.get("price", ""),  # LIMIT/MARKET orders
        "stopPrice": order.get("stopPrice", stop_price if stop_price else ""),
        "executedQty": order.get("executedQty", ""),
        "origQty": order.get("origQty", quantity if quantity else "")
    }

    # Write to CSV
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, mode="a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

    # print(f"✓ Order logged: {row}")
    
# ----------------- Utility Functions -----------------
def get_open_position():
    """Check current BTC position."""
    try:
        account = client.get_account()
        for balance in account['balances']:
            if balance['asset'] == 'BTC':
                btc_balance = float(balance['free']) + float(balance['locked'])
                if btc_balance >= 0.00015:
                    return round(btc_balance, 4), 'LONG'
        return 0, 'NONE'
    except Exception as e:
        print(f"Error checking position: {e}")
        return 0, 'NONE'

def cancel_all_orders_except(price):
    """Cancel all open orders except the one at the target price."""
    try:
        open_orders = client.get_open_orders(symbol=SYMBOL)
        for order in open_orders:
            if float(order['stopPrice']) != float(price):
                client.cancel_order(symbol=SYMBOL, orderId=order['orderId'])
                print(f"Cancelled order {order['orderId']} at {order['stopPrice']}")
                return True
    except Exception as e:
        print(f"Error cancelling orders: {e}")
    return False

def cancel_all_orders(symbol):
    """Cancel all open orders for a given symbol."""
    try:
        open_orders = client.get_open_orders(symbol=symbol)
        if not open_orders:
            print(f"No open orders for {symbol}")
            return []

        cancelled = []
        for order in open_orders:
            order_id = order["orderId"]
            client.cancel_order(symbol=symbol, orderId=order_id)
            cancelled.append(order_id)
            print(f"✓ Cancelled order {order_id} for {symbol}")

        return cancelled
    except Exception as e:
        print(f"✗ Error cancelling orders: {e}")
        return None

def place_stop_order(side, quantity, stop_price):
    """Place STOP_LIMIT order and log if executed."""
    order = None
    try:
        if side == 'BUY':
            order = client.create_order(
                symbol=SYMBOL,
                side='BUY',
                type='STOP_LOSS',
                quantity=quantity,
                stopPrice=str(stop_price),  
            )
            print(f"Placed BUY STOP-LIMIT order: {quantity} BTC, stop={stop_price}")
        elif side == 'SELL':
            order = client.create_order(
                symbol=SYMBOL,
                side='SELL',
                type='STOP_LOSS',
                quantity=quantity,
                stopPrice=str(stop_price),
            )
            print(f"Placed SELL STOP-LIMIT order: {quantity} BTC, stop={stop_price}")
        else:
            return None
    except Exception as e:
        ex = f"✗ Error placing STOP {side}: {e}"
        print(ex)
        with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([ex])
        if "Stop price would trigger immediately" in str(e):
            if side == 'BUY':
                # ⚠ optional: cancel only buy-stop orders, not everything
                balance = client.get_asset_balance(asset="BTC")
                held = float(balance["free"]) + float(balance["locked"])
                if held >= 0.0001:
                    print("⚠ Already in Buy trade, skipping fallback market order.")
                else:
                    order = client.order_market_buy(symbol=SYMBOL, quantity=quantity)
                    print(f"⚠ Fallback BUY MARKET order: {quantity} BTC @ {stop_price}")

            elif side == 'SELL':
                balance = client.get_asset_balance(asset="BTC")
                held = float(balance["free"]) + float(balance["locked"])
                if held >= 0.0001:
                    order = client.order_market_sell(symbol=SYMBOL, quantity=held)
                    print(f"⚠ Fallback SELL MARKET order: {held} BTC @ {stop_price}")
                else:
                    print("⚠ No BTC left to sell, skipping fallback market order.")

    if order:
        log_trade(order, side=side, stop_price=stop_price, quantity=quantity)
    return order

# ----------------- Strategy Execution -----------------
def execute_strategy_limit():
    """Main limit-order executor."""
    print(f"\n--- Checking at {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
    
    # 1. Check position
    position_size, current_side = get_open_position()
    has_position = position_size > 0

    # 2. Fetch candle data
    try:
        data = fetch_live_klines(SYMBOL, TIMEFRAME, limit=5)  # last candle
        candle = data.tail(1)
        upbound = float(candle['upBound'].values[0])  
        downbound = float(candle['downBound'].values[0]) 
    except Exception as e:
        print(f"✗ Error fetching candle data: {e}")
        return
    
    # 3. Decide target price and quantity
    if has_position:
        target_price = downbound - 0.5
        quantity = position_size
        side = 'SELL'
    else:
        target_price = upbound + 0.5
        quantity = risk_management.calculate_position_size1()
        side = 'BUY'
    # 4. Cancel previous orders except target price
    cancel_all_orders_except(price=target_price)

    # 5. Place limit order if it does not already exist
    open_orders = client.get_open_orders(symbol=SYMBOL)
    existing_prices = [float(o['stopPrice']) for o in open_orders]
    if target_price not in existing_prices:
        place_stop_order(side=side, quantity=quantity, stop_price=target_price)
    else:
        print(f"Order already exists at {target_price}, no new order placed.")

# ----------------- Main Loop -----------------
if __name__ == "__main__":
    print("Starting Smart Channel Limit Bot with Logger...")
    print("Bot configured with dynamic position sizing")
    print("Symbol:", SYMBOL)
    print("Timeframe:", TIMEFRAME)
    print("Channel Length:", LENGTH)
    print("-" * 50)

    # Example: single run
    execute_strategy_limit()

    # Uncomment for live loop
    # while True:
    #     try:
    #         execute_strategy_limit()
    #         time.sleep(30)
    #     except KeyboardInterrupt:
    #         print("\nBot stopped by user")
    #         break
    #     except Exception as e:
    #         print(f"Unexpected error: {e}")
    #         time.sleep(60)
