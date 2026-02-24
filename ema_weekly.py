"""
EMA Scanner - Weekly Timeframe (10, 20, 40)
Scans S&P 500, Nasdaq-100, and Dow Jones 30 stocks
Checks EMA alignment on: Weekly timeframe only
Signal when Price > EMA10 > EMA20 > EMA40 (Bullish)
      or Price < EMA10 < EMA20 < EMA40 (Bearish)
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


def analyze_ema_weekly(symbol):
    """
    Analyzes a stock's EMA 10/20/40 position on the Weekly timeframe.
    Returns dict with analysis or None if not aligned.
    """
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period='2y', interval='1wk')  # 2 years of weekly data

        if df.empty or len(df) < 41:
            return None

        # Calculate EMAs
        df['EMA10'] = calculate_ema(df['Close'], 10)
        df['EMA20'] = calculate_ema(df['Close'], 20)
        df['EMA40'] = calculate_ema(df['Close'], 40)

        df = df.dropna(subset=['EMA10', 'EMA20', 'EMA40'])

        if len(df) < 1:
            return None

        # Get latest values
        latest = df.iloc[-1]
        price  = round(latest['Close'], 2)
        ema10  = round(latest['EMA10'], 2)
        ema20  = round(latest['EMA20'], 2)
        ema40  = round(latest['EMA40'], 2)

        # Bullish only: Price > EMA10 > EMA20 > EMA40
        bullish = (price > ema10 > ema20 > ema40)

        if bullish:
            return {
                'Symbol':  symbol,
                'Signal':  '🟢 BULLISH (Above All EMAs)',
                'Price':   price,
                'EMA10':   ema10,
                'EMA20':   ema20,
                'EMA40':   ema40,
                'Status':  '✅ Price > EMA10 > EMA20 > EMA40'
            }

        return None  # Not in uptrend alignment

    except Exception:
        return None


def scan_ema_weekly():
    """Main scanning function — Weekly EMA only"""
    print("=" * 70)
    print(" EMA SCANNER — WEEKLY TIMEFRAME (10, 20, 40)")
    print(" S&P 500 + Nasdaq-100 + Dow Jones 30")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print("\n📊 Logic: Find stocks in Strong Uptrend on Weekly chart")
    print("   BULLISH = Price > EMA10 > EMA20 > EMA40")
    print("=" * 70)

    symbols = load_symbols()
    if not symbols:
        input("\nPress Enter to exit...")
        return

    print(f"\nScanning {len(symbols)} stocks on Weekly timeframe...")
    print("This will take approximately 5-8 minutes.")
    print("-" * 70)

    aligned_stocks = []
    total_symbols = len(symbols)

    for i, symbol in enumerate(symbols, 1):
        if i % 25 == 0:
            print(f"Progress: {i}/{total_symbols} scanned... ({len(aligned_stocks)} aligned found)")

        result = analyze_ema_weekly(symbol)

        if result:
            aligned_stocks.append(result)
            print(f"[{i}/{total_symbols}] ✓ {symbol} - {result['Signal']}")

        time.sleep(0.2)

    print("\n" + "=" * 70)
    print(f" Scan Complete! Found {len(aligned_stocks)} stocks in Weekly Uptrend")
    print("=" * 70)

    if aligned_stocks:
        df_results = pd.DataFrame(aligned_stocks)
        df_results = df_results.sort_values('Signal')

        output_file = f"ema_weekly_scan_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df_results.to_csv(output_file, index=False)
        print(f"\n✓ Results saved to: {output_file}\n")

        print(f"\n🟢 BULLISH — Price > EMA10 > EMA20 > EMA40 on Weekly: {len(df_results)}")
        print("-" * 70)
        if not df_results.empty:
            print(df_results[['Symbol', 'Price', 'EMA10', 'EMA20', 'EMA40']].to_string(index=False))
        else:
            print("No stocks found")

        print("\n" + "=" * 70)
        print("\n📈 EMA Explanation (Weekly):")
        print("   EMA 10 = Fast  — short-term weekly trend")
        print("   EMA 20 = Medium — mid-term weekly trend")
        print("   EMA 40 = Slow  — longer-term weekly trend")
        print("\n   Strong Uptrend: Price > EMA10 > EMA20 > EMA40")
        print("=" * 70)
    else:
        print("\n❌ No stocks found with all Weekly EMAs aligned.")

    input("\nPress Enter to exit...")


if __name__ == "__main__":
    scan_ema_weekly()
