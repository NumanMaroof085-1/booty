from binance.client import Client
import os

# Replace these with your actual keys from the testnet page
api_key = os.environ.get('BINANCE_TESTNET_API_KEY')
api_secret = os.environ.get('BINANCE_TESTNET_SECRET_KEY')
# api_key = "D7jUfM1q8pzN8403xK6NiRKdJKifJXWUB1SeodY1R4H8LcEIABUtJxUwNvJ1100I"
# api_secret = "odgBguZ8VUIkF6ahADOVpfOgPWBtwS3psjGeIkmvu7pwtnPA0yR46Puo2ztCCI52"
# api_key = "JfnT3XkD4EEiZRv52mOp9EuU46FsGd74wgOgs3BEueB43htM4fijw7CuF50Wd8vr"
# api_secret = "oWQ8xvddWipUyBlLJvmHExmOAzlz7Y1GqORtqPvxS1IJJztS33zxVezg46mJFhMX"
# api_key = "sdQoABZMq6R2Q1uYWcYYnbWtpCTANxnMqppZdJWJXRMkTn9mKvRXEmJU9aRygh51"
# api_secret = "LPpE8VGtxCXsRQtViPhsNO5fJLrU8xk3kaxa2mFGpL9lNzOCl5x28zrOaK5IRAxL"

print(os.environ.get('BINANCE_TESTNET_API_KEY'))
print(os.environ.get('BINANCE_TESTNET_SECRET_KEY'))

# The 'testnet=True' flag is crucial! It points the client to the testnet URL.
client = Client(api_key, api_secret, testnet=True)

# Make a simple API call to get account information
account_info = client.get_account()
# print("Account Balances:")
# for balance in account_info['balances']:
#     if float(balance['free']) > 0 or float(balance['locked']) > 0:
#         print(f"  {balance['asset']}: Free = {balance['free']}, Locked = {balance['locked']}")

# order_book = client.get_order_book(symbol='BTCUSDT')
# print(order_book)

# client.create_test_order(
#     symbol='BTCUSDT',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_MARKET,
#     quantity=0.001)
# print("Test order was successful!")

# order = client.create_order(
#     symbol='BTCUSDT',
#     side=Client.SIDE_BUY,
#     type=Client.ORDER_TYPE_LIMIT,
#     timeInForce='GTC',
#     quantity=0.001,
#     price=40000)
# print(order)

# # Get all open orders for a symbol
# client.order_limit_buy(symbol='BTCUSDT',
#                 quantity=0.1,
#                 price="108900")


# Cancel an order using its ID
# cancel_order = client.cancel_order(symbol='BTCUSDT', orderId=17788655)
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
# print(cancel_all_orders('BTCUSDT'))
# print(cancel_order)

# order = client.order_market_sell(symbol= 'BTCUSDT',quantity = 0.9199)
# print(f"Market sell order placed successfully: {order}")

# Filter for only BTC and USDT
target_assets = ['BTC', 'USDT']

for balance in account_info['balances']:
    if balance['asset'] in target_assets:
        free_balance = float(balance['free'])
        locked_balance = float(balance['locked'])
        
        # Print regardless of whether the balance is zero or not
        print(f"  {balance['asset']}: Free = {free_balance:.8f}, Locked = {locked_balance:.8f}")

# order = client.create_order(
#     symbol="BTCUSDT",
#     side="BUY",
#     type="STOP_LOSS_LIMIT",
#     quantity=0.01,
#     price="109070",     # limit price (slightly above stop to guarantee fill)
#     stopPrice="109055", # trigger price
#     timeInForce="GTC"
# )
# try:
#     order = client.create_order(
#         symbol="BTCUSDT",
#         side="BUY",
#         type="STOP_LOSS",
#         quantity=0.01,
#         stopPrice="108900"  # trigger when price hits 26k
#     )
# except Exception as e:
#     print(e)

# order = client.create_order(
#     symbol="BTCUSDT",
#     side="SELL",
#     type="TAKE_PROFIT",
#     quantity=1,
#     stopPrice="109100"  # trigger when price hits 26k
# )
open_orders = client.get_open_orders(symbol='BTCUSDT')
print(open_orders)

