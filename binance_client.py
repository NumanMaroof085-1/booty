# binance_client.py
from binance.client import Client
import pandas as pd
import requests
import os

api_key_live = "Mf7g8cYyWuHJT0MPwHVzioCDaiyhXJJvP4Xp8p7m4rhov0IXzFzTbiAaztdp9e4W"  # from Binance app
def get_binance_client():
    """
    Creates and returns an authenticated Binance Client instance connected to the TESTNET.
    Reads API keys from environment variables.
    """
    api_key = os.environ.get('BINANCE_TESTNET_API_KEY')
    api_secret = os.environ.get('BINANCE_TESTNET_SECRET_KEY')

    if not api_key or not api_secret:
        raise ValueError("Could not find Binance API keys in environment variables. "
                         "Please set 'BINANCE_TESTNET_API_KEY' and 'BINANCE_TESTNET_SECRET_KEY'.")

    # The 'testnet=True' flag is crucial to point to the testnet environment
    return Client(api_key, api_secret, testnet=True)

def fetch_live_klines(symbol, interval, limit=500, api_key_live=None):
    """
    Fetches live kline (OHLCV) data from Binance using a live account API key
    and returns a cleaned pandas DataFrame.

    Args:
        symbol (str): Trading symbol, e.g., 'BTCUSDT'
        interval (str): Kline interval, e.g., '1m', '5m', '1h'
        limit (int): Number of candles to fetch (max 1000)
        api_key (str): Your Binance API key

    Returns:
        pd.DataFrame: DataFrame with columns ['timestamp', 'open', 'high', 'low', 'close', 'volume']
    """
    
    url = "https://api.binance.com/api/v3/klines"
    params = {
        "symbol": symbol.upper(),
        "interval": interval,
        "limit": limit
    }
    headers = {}
    if api_key_live:
        headers["X-MBX-APIKEY"] = api_key_live

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()  # Raise error if request failed
    klines = response.json()

    # Create DataFrame
    columns = [
        'timestamp', 'open', 'high', 'low', 'close', 'volume',
        'close_time', 'quote_asset_volume', 'number_of_trades',
        'taker_buy_base_asset_volume', 'taker_buy_quote_asset_volume', 'ignore'
    ]
    df = pd.DataFrame(klines, columns=columns)
    # Convert relevant columns to numeric
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = pd.to_numeric(df[col])

    # Convert timestamp to datetime in Pakistan timezone
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms') \
                        .dt.tz_localize('UTC') \
                        .dt.tz_convert('Asia/Karachi')

    df['upBound'] = df['high'].rolling(window=1).max().shift(1)
    df['downBound'] = df['low'].rolling(window=1).min().shift(1)

    # Return only essential columns
    return df[['timestamp', 'open', 'high', 'low', 'close', 'volume','upBound','downBound']]


# Example usage and test function
if __name__ == "__main__":
    # Test the connection and data fetch
    try:
        print("Testing connection to Binance Testnet...")
        client = get_binance_client()
        # A simple API call to test connectivity
        server_time = client.get_server_time()
        print(f"✓ Connection successful. Server time: {server_time['serverTime']}")

        print("\nFetching recent BTCUSDT 1m klines...")
        # Fetch data for the strategy
        df = fetch_live_klines(symbol='BTCUSDT', interval='1m', limit=10)
        print(f"✓ Successfully fetched {len(df)} candles.")
        print("\nLatest candles:")
        print(df.tail(10))

        # Quick check of account balance (optional)
        print("\nChecking USDT balance...")
        account_info = client.get_account()
        for balance in account_info['balances']:
            if balance['asset'] == 'USDT':
                print(f"USDT Balance: {balance['free']}")
                break

    except Exception as e:
        print(f"✗ An error occurred: {e}")