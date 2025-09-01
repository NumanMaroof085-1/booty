# executor_limit.py
from binance_client import get_binance_client, fetch_live_klines
import risk_management
import time
import csv
from datetime import datetime

# Configuration
SYMBOL = 'BTCUSDT'
TIMEFRAME = '1m'
LENGTH = 1  # channel length
LOG_FILE = "trade_log.csv"

client = get_binance_client()

# ----------------- Logger -----------------
def log_trade(order):
    """
    Logs executed trades.
    Aggregates multiple fills into one entry.
    """
    if not order or 'fills' not in order or not order['fills']:
        return

    total_qty = sum(float(f['qty']) for f in order['fills'])
    avg_price = sum(float(f['price']) * float(f['qty']) for f in order['fills']) / total_qty
    side = order['side']

    log_entry = [datetime.now().strftime("%Y-%m-%d %H:%M:%S"), side, round(avg_price, 2), round(total_qty, 6)]
    
    # Write to CSV
    with open(LOG_FILE, mode='a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(log_entry)
    
    print(f"Logged trade: {log_entry}")

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
    except Exception as e:
        print(f"Error cancelling orders: {e}")

def place_stop_limit_order(side, quantity, stop_price):
    """Place STOP_LIMIT order and log if executed."""
    try:
        if side == 'BUY':
            order = client.create_order(
                symbol=SYMBOL,
                side='BUY',
                type='STOP_LOSS',
                quantity=quantity,
                # price=str(limit_price),      # the limit order price
                stopPrice=str(stop_price),   # the trigger price
                # timeInForce='GTC'            # good till cancelled
            )
            print(f"Placed BUY STOP-LIMIT order: {quantity} BTC, stop={stop_price}")

        elif side == 'SELL':
            order = client.create_order(
                symbol=SYMBOL,
                side='SELL',
                type='STOP_LOSS',
                quantity=quantity,
                # price=str(limit_price),
                stopPrice=str(stop_price),
                # timeInForce='GTC'
            )
            print(f"Placed SELL STOP-LIMIT order: {quantity} BTC, stop={stop_price}")

        else:
            return None

        # If the order is filled immediately (rare for STOP_LIMIT), log it
        # if order.get('status') == 'FILLED':
        #       log_trade(order)
        # return order

    except Exception as e:
        print(f"✗ Error placing STOP-LIMIT {side}: {e}")
        if side == 'BUY':
            order = client.order_market_buy(
                symbol = SYMBOL, quantity = quantity
            )
            print(f"Placed BUY market-buy order : {quantity} BTC, stop={stop_price}")
        elif side == 'SELL':
            order = client.order_market_sell(
                symbol = SYMBOL, quantity = quantity
            )
            print(f"Placed SELL market-buy order : {quantity} BTC, stop={stop_price}")
            
        # log_trade(order)
        # return None
    if order:
        log_trade(order)
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
    # print(candle)
    # print(upbound)
    # print(upbound+1)
    # 3. Decide target price and quantity
    if has_position:
        target_price = downbound - 1
        # limit_price = target_price - 15
        quantity = position_size
        side = 'SELL'
    else:
        target_price = upbound + 1
        # limit_price = target_price + 10
        quantity = risk_management.calculate_position_size1()
        side = 'BUY'
    # 4. Cancel previous orders except target price
    cancel_all_orders_except(price=target_price)

    # 5. Place limit order if it does not already exist
    open_orders = client.get_open_orders(symbol=SYMBOL)
    existing_prices = [float(o['stopPrice']) for o in open_orders]
    if target_price not in existing_prices:
        order = place_stop_limit_order(side=side, quantity=quantity, stop_price=target_price)
        # Log fills if any occurred immediately
        # if order and order.get('status') == 'FILLED':
        #     log_trade(order)
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
