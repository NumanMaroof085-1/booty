# performance_testnet.py
import requests
import time
import hmac
import hashlib
import pandas as pd
import os

# Replace these with your Spot Testnet API keys
API_KEY = os.environ.get('BINANCE_TESTNET_API_KEY')
API_SECRET = os.environ.get('BINANCE_TESTNET_SECRET_KEY')

BASE_URL = "https://testnet.binance.vision/api/v3"

def get_trade_history(symbol='BTCUSDT', limit=500):
    """Fetch recent trade history for a symbol from Spot Testnet."""
    endpoint = "/myTrades"
    timestamp = int(time.time() * 1000)
    params = f"symbol={symbol}&limit={limit}&timestamp={timestamp}"
    signature = hmac.new(API_SECRET.encode(), params.encode(), hashlib.sha256).hexdigest()
    url = f"{BASE_URL}{endpoint}?{params}&signature={signature}"

    headers = {"X-MBX-APIKEY": API_KEY}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def calculate_pnl(symbol='BTCUSDT'):
    """Calculates realized PnL per trade for Spot Testnet."""
    trades = get_trade_history(symbol)
    df = pd.DataFrame(trades)

    if df.empty:
        return pd.DataFrame()

    # Convert numeric columns
    df['price'] = pd.to_numeric(df['price'])
    df['qty'] = pd.to_numeric(df['qty'])
    df['quoteQty'] = pd.to_numeric(df['quoteQty'])
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    # Sort oldest first
    df = df.sort_values('time')

    position = 0
    entry_price = 0
    trade_history = []

    for _, trade in df.iterrows():
        if trade['isBuyer']:
            # Buy trade
            if position == 0:
                entry_price = trade['price']
                position = trade['qty']
            else:
                # Weighted average entry
                entry_price = (position * entry_price + trade['qty'] * trade['price']) / (position + trade['qty'])
                position += trade['qty']
            pnl = 0  # No PnL for buys
            trade_type = "BUY"
        else:
            # Sell trade
            if position > 0:
                pnl = (trade['price'] - entry_price) * trade['qty']
                position -= trade['qty']
            else:
                pnl = 0
            trade_type = "SELL"

        trade_history.append({
            'Time': trade['time'],
            'Type': trade_type,
            'Price': trade['price'],
            'Quantity': trade['qty'],
            'PnL': pnl,
            'Position': position
        })

    return pd.DataFrame(trade_history)

def show_performance_summary(symbol='BTCUSDT'):
    """Displays trade history and PnL summary for Spot Testnet."""
    print(f"Fetching trade history for {symbol} on Spot Testnet...")
    pnl_df = calculate_pnl(symbol)

    if pnl_df.empty:
        print("No trades found.")
        return

    print("\n" + "="*80)
    print("TRADE HISTORY & PnL PER TRADE")
    print("="*80)
    print(pnl_df.tail(35))  # Show last trades

    print("\n" + "="*80)
    print("PERFORMANCE SUMMARY")
    print("="*80)
    total_realized_pnl = pnl_df['PnL'].sum()
    total_closed_trades = len(pnl_df[pnl_df['Type'] == 'SELL'])
    winning_trades = len(pnl_df[pnl_df['PnL'] > 0])

    print(f"Total Trades: {len(pnl_df)}")
    print(f"Closed Trades: {total_closed_trades}")
    print(f"Final Realized PnL: {total_realized_pnl:.2f} USDT")
    if total_closed_trades > 0:
        win_rate = (winning_trades / total_closed_trades) * 100
        print(f"Win Rate: {win_rate:.1f}%")
    print(f"Current Position: {pnl_df['Position'].iloc[-1]:.6f} {symbol.replace('USDT','')}")

# Run to see PnL per trade
if __name__ == "__main__":
    show_performance_summary()

#                        Time  Type      Price  Quantity         PnL  Position    
# 465 2025-08-30 20:51:12.118   BUY  108906.88   0.00147    0.000000   0.52523    
# 466 2025-08-30 20:51:12.118   BUY  108906.90   0.00100    0.000000   0.52623    
# 467 2025-08-30 20:51:12.118   BUY  108917.52   0.00022    0.000000   0.52645    
# 468 2025-08-30 20:51:12.118   BUY  108920.44   0.00001    0.000000   0.52646    
# 469 2025-08-30 20:51:12.118   BUY  108932.98   0.00022    0.000000   0.52668    
# 470 2025-08-30 20:51:12.118   BUY  108900.00   0.00499    0.000000   0.53167    
# 471 2025-08-30 20:51:12.118   BUY  108857.88   0.00147    0.000000   0.53314    
# 472 2025-08-30 20:51:12.118   BUY  108860.00   0.04619    0.000000   0.57933    
# 473 2025-08-30 20:51:12.118   BUY  108853.74   0.00100    0.000000   0.58033    
# 474 2025-08-30 20:51:12.118   BUY  108759.87   0.00147    0.000000   0.58180    
# 475 2025-08-30 20:51:12.118   BUY  108762.88   0.07362    0.000000   0.65542    
# 476 2025-08-30 20:51:12.118   BUY  108766.87   0.00147    0.000000   0.65689    
# 477 2025-08-30 20:51:12.118   BUY  108773.87   0.00147    0.000000   0.65836    
# 478 2025-08-30 20:51:12.118   BUY  108776.64   0.00965    0.000000   0.66801    
# 479 2025-08-30 20:51:12.118   BUY  108778.35   0.01417    0.000000   0.68218    
# 480 2025-08-30 20:51:12.118   BUY  108855.67   0.00022    0.000000   0.68240
# 481 2025-08-30 20:51:12.118   BUY  108793.81   0.00022    0.000000   0.68262
# 482 2025-08-30 20:51:12.118   BUY  108808.87   0.00147    0.000000   0.68409
# 483 2025-08-30 20:51:12.118   BUY  108780.87   0.00147    0.000000   0.68556
# 484 2025-08-30 20:51:12.118   BUY  108815.88   0.00147    0.000000   0.68703
# 485 2025-08-30 20:51:12.118   BUY  108822.88   0.00147    0.000000   0.68850
# 486 2025-08-30 20:51:12.118   BUY  108824.74   0.00022    0.000000   0.68872
# 487 2025-08-30 20:51:12.118   BUY  108829.88   0.00147    0.000000   0.69019
# 488 2025-08-30 20:51:12.118   BUY  108836.88   0.00147    0.000000   0.69166
# 489 2025-08-30 20:51:12.118   BUY  108840.20   0.00022    0.000000   0.69188
# 490 2025-08-30 20:51:12.118   BUY  108841.67   0.00500    0.000000   0.69688
# 491 2025-08-30 20:51:12.118   BUY  108843.88   0.00147    0.000000   0.69835
# 492 2025-08-30 20:51:12.118   BUY  108850.88   0.00147    0.000000   0.69982
# 493 2025-08-30 20:51:12.118   BUY  108809.27   0.00022    0.000000   0.70004


#                        Time  Type      Price  Quantity           PnL  Position
# 465 2025-08-31 13:34:16.574  SELL  103837.83   0.00100   -194.824414   0.34142
# 466 2025-08-31 13:34:16.574  SELL  103544.34   0.04015  -7833.983857   0.30127
# 467 2025-08-31 13:34:16.574  SELL  103523.77   0.00024    -46.833234   0.30103
# 468 2025-08-31 13:34:16.574  SELL  104379.33   0.00019    -36.913754   0.30084
# 469 2025-08-31 13:34:16.574  SELL  103472.97   0.00100   -195.189274   0.29984
# 470 2025-08-31 13:34:16.574  SELL  103372.31   0.00024    -46.869584   0.29960
# 471 2025-08-31 13:34:16.574  SELL  103292.04   0.00019    -37.120339   0.29941
# 472 2025-08-31 13:34:16.574  SELL  103108.10   0.00100   -195.554144   0.29841
# 473 2025-08-31 13:34:16.574  SELL  102799.83   0.00024    -47.006979   0.29817
# 474 2025-08-31 13:34:16.574  SELL  102743.24   0.00100   -195.919004   0.29717
# 475 2025-08-31 13:34:16.574  SELL  102730.10   0.00024    -47.023715   0.29693
# 476 2025-08-31 13:34:16.574  SELL  102649.43   0.00024    -47.043075   0.29669
# 477 2025-08-31 13:34:16.574  SELL  103453.55   0.00024    -46.850087   0.29645
# 478 2025-08-31 13:34:16.574  SELL  104567.56   0.00100   -194.094684   0.29545
# 479 2025-08-31 13:34:16.574  SELL  104818.08   0.00023    -44.584158   0.29522
# 480 2025-08-31 13:34:16.574  SELL  104900.46   0.00023    -44.565210   0.29499
# 481 2025-08-31 13:34:16.574  SELL  106820.78   0.04015  -7702.434791   0.25484
# 482 2025-08-31 13:34:16.574  SELL  106756.75   0.00100   -191.905494   0.25384
# 483 2025-08-31 13:34:16.574  SELL  106553.90   0.00018    -34.579502   0.25366
# 484 2025-08-31 13:34:16.574  SELL  106419.54   0.00023    -44.215822   0.25343
# 485 2025-08-31 13:34:16.574  SELL  106391.89   0.00100   -192.270354   0.25243
# 486 2025-08-31 13:34:16.574  SELL  106347.36   0.00023    -44.232423   0.25220
# 487 2025-08-31 13:34:16.574  SELL  106263.84   0.00023    -44.251633   0.25197
# 488 2025-08-31 13:34:16.574  SELL  106027.02   0.00100   -192.635224   0.25097
# 489 2025-08-31 13:34:16.574  SELL  105695.60   0.00023    -44.382328   0.25074
# 490 2025-08-31 13:34:16.574  SELL  105662.16   0.00100   -193.000084   0.24974
# 491 2025-08-31 13:34:16.574  SELL  105623.91   0.00023    -44.398817   0.24951
# 492 2025-08-31 13:34:16.574  SELL  105540.96   0.00023    -44.417895   0.24928
# 493 2025-08-31 13:34:16.574  SELL  105466.61   0.00018    -34.775214   0.24910
# 494 2025-08-31 13:34:16.574  SELL  105297.29   0.00100   -193.364954   0.24810
# 495 2025-08-31 13:34:16.574  SELL  105225.50   0.29358 -56789.159386  -0.04548
# 496 2025-08-31 13:34:16.574  SELL  104971.65   0.00023      0.000000  -0.04548
# 497 2025-08-31 13:34:16.574  SELL  104932.43   0.00100      0.000000  -0.04548
# 498 2025-08-31 13:34:16.574  SELL  102075.88   0.00024      0.000000  -0.04548
# 499 2025-08-31 13:34:16.574  SELL   49955.99   0.00565      0.000000  -0.04548