"""
EMA Scanner - Daily Timeframe (10, 20, 40) — Crossover Signal
Scans S&P 500, Nasdaq-100, and Dow Jones 30 stocks
Checks EMA crossover on: Daily timeframe only

Signal (all 6 must be true):
  1. Close > EMA10
  2. Close > EMA20
  3. Close > EMA40
  4. Previous Close < Previous EMA10  (fresh crossover)
  5. EMA20 > EMA40
  6. EMA10 > EMA20
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import time


def load_symbols():
    """Load symbols from top US indices (S&P 500, Nasdaq-100, Dow 30)"""
    try:
        with open('top_indices_symbols.txt', 'r') as f:
            symbols = [line.strip() for line in f if line.strip()]
        print(f"✓ Loaded {len(symbols)} symbols from top US indices")
        return symbols
    except FileNotFoundError:
        print("❌ Error: top_indices_symbols.txt not found!")
        return []


def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    return prices.ewm(span=period, adjust=False).mean()


def analyze_ema_daily(symbol):
    """
    Analyzes a stock's EMA 10/20/40 crossover on the Daily timeframe.
    Returns dict when all 6 crossover conditions are met, else None.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='6mo', interval='1d')  # 6 months of daily data

        if df.empty or len(df) < 41:
            return None

        # Calculate EMAs
        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        df['EMA40'] = calculate_ema(df['Close'], 40)

        df = df.dropna(subset=['EMA10', 'EMA20', 'EMA40'])

        if len(df) < 2:  # Need at least 2 rows (today + yesterday)
            return None

        # Today's values
        today = df.iloc[-1]
        price  = round(today['Close'], 2)
        ema10  = round(today['EMA10'], 2)
        ema20  = round(today['EMA20'], 2)
        ema40  = round(today['EMA40'], 2)

        # Previous bar's values
        prev = df.iloc[-2]
        prev_close = prev['Close']
        prev_ema10 = prev['EMA10']

        # All 6 crossover conditions
        c1 = price > ema10           # Close > EMA10
        c2 = price > ema20           # Close > EMA20
        c3 = price > ema40           # Close > EMA40
        c4 = prev_close < prev_ema10 # Prev Close < Prev EMA10 (fresh crossover)
        c5 = ema20 > ema40           # EMA20 > EMA40
        c6 = ema10 > ema20           # EMA10 > EMA20

        if c1 and c2 and c3 and c4 and c5 and c6:
            return {
                'Symbol':  symbol,
                'Signal':  '🟢 BULLISH (EMA Crossover)',
                'Price':   price,
                'EMA10':   ema10,
                'EMA20':   ema20,
                'EMA40':   ema40,
                'Status':  '✅ Fresh crossover above EMA10 · EMAs stacked bullish'
            }

        return None  # Crossover conditions not met

    except Exception:
        return None


def scan_ema_daily():
    """Main scanning function — Daily EMA only"""
    print("=" * 70)
    print(" EMA SCANNER — DAILY TIMEFRAME (10, 20, 40)")
    print(" S&P 500 + Nasdaq-100 + Dow Jones 30")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("\n📊 Logic: Fresh EMA10 crossover with bullish EMA stacking")
    print("   Close > EMA10/20/40 + Prev Close < Prev EMA10 + EMA10>20>40")
    print("=" * 70)

    symbols = load_symbols()
    if not symbols:
        input("\nPress Enter to exit...")
        return

    print(f"\nScanning {len(symbols)} stocks on Daily timeframe...")
    print("This will take approximately 5-8 minutes.")
    print("-" * 70)

    aligned_stocks = []
    total_symbols = len(symbols)

    for i, symbol in enumerate(symbols, 1):
        if i % 25 == 0:
            print(f"Progress: {i}/{total_symbols} scanned... ({len(aligned_stocks)} aligned found)")

        result = analyze_ema_daily(symbol)

        if result:
            aligned_stocks.append(result)
            print(f"[{i}/{total_symbols}] ✓ {symbol} - {result['Signal']}")

        time.sleep(0.2)

    print("\n" + "=" * 70)
    print(f" Scan Complete! Found {len(aligned_stocks)} stocks in Daily Uptrend")
    print("=" * 70)

    if aligned_stocks:
        df_results = pd.DataFrame(aligned_stocks)
        df_results = df_results.sort_values('Signal')

        output_file = f"ema_daily_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df_results.to_csv(output_file, index=False)
        print(f"\n✓ Results saved to: {output_file}\n")

        print(f"\n🟢 BULLISH — Fresh EMA crossover on Daily: {len(df_results)}")
        print("-" * 70)
        if not df_results.empty:
            print(df_results[['Symbol', 'Price', 'EMA10', 'EMA20', 'EMA40']].to_string(index=False))
        else:
            print("No stocks found")

        print("\n" + "=" * 70)
        print("\n📈 EMA Crossover Logic (Daily):")
        print("   1. Close > EMA10, EMA20, EMA40")
        print("   2. Previous Close < Previous EMA10 (fresh breakout)")
        print("   3. EMA10 > EMA20 > EMA40 (bullish stacking)")
        print("=" * 70)
    else:
        print("\n❌ No stocks found with all Daily EMAs aligned.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    scan_ema_daily()
