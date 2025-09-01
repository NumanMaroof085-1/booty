from binance.client import Client
import os

# Replace these with your actual keys from the testnet page
api_key = os.environ.get('BINANCE_TESTNET_API_KEY')
api_secret = os.environ.get('BINANCE_TESTNET_SECRET_KEY')


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
# cancel_order = client.cancel_order(symbol='BTCUSDT', orderId=17751159)
# print(cancel_order)

# order = client.order_market_sell(symbol= 'BTCUSDT',quantity = 0.5023)
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

# order = client.create_order(
#     symbol="BTCUSDT",
#     side="BUY",
#     type="STOP_LOSS",
#     quantity=0.01,
#     stopPrice="109600"  # trigger when price hits 26k
# )
# order = client.create_order(
#     symbol="BTCUSDT",
#     side="SELL",
#     type="STOP_LOSS",
#     quantity=0.001,
#     stopPrice="108840"  # trigger when price hits 26k
# )
open_orders = client.get_open_orders(symbol='BTCUSDT')
print(open_orders)

