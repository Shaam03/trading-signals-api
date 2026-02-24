"""
Multi-Timeframe SMA 50 Scanner
Scans S&P 500, Nasdaq-100, and Dow Jones 30 stocks
Checks if price is above/below SMA 50 on: Daily + 1HR + 15min
Strong signal when ALL timeframes align!
"""
 
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
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
 
def calculate_sma(prices, period=50):
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return None
    return prices.rolling(window=period).mean()
 
def get_sma_position(symbol, interval):
    """
    Get current price position relative to SMA 50 for a specific timeframe.
    Returns: 'above', 'below', or None (if error)
    """
    try:
        ticker = yf.Ticker(symbol)
       
        # Fetch data based on interval
        if interval == '1d':
            df = ticker.history(period='3mo', interval='1d')  # 90 days for daily
        elif interval == '1h':
            df = ticker.history(period='1mo', interval='1h')  # 30 days for hourly (need 50 hours)
        elif interval == '15m':
            df = ticker.history(period='5d', interval='15m')  # 5 days for 15min (need 50 bars)
        else:
            return None, None, None
       
        if df.empty or len(df) < 51:
            return None, None, None
       
        # Calculate SMA 50
        df['SMA50'] = calculate_sma(df['Close'], period=50)
        df = df.dropna(subset=['SMA50'])
       
        if len(df) < 1:
            return None, None, None
       
        # Get latest values
        latest = df.iloc[-1]
        price = round(latest['Close'], 2)
        sma = round(latest['SMA50'], 2)
        position = 'above' if price > sma else 'below'
       
        return position, price, sma
       
    except Exception as e:
        return None, None, None
 
def analyze_multi_timeframe(symbol):
    """
    Analyzes a stock across 3 timeframes: Daily, 1HR, 15min
    Returns dict with analysis or None if not aligned
    """
    try:
        # Get position for each timeframe
        daily_pos, daily_price, daily_sma = get_sma_position(symbol, '1d')
        hourly_pos, hourly_price, hourly_sma = get_sma_position(symbol, '1h')
        min15_pos, min15_price, min15_sma = get_sma_position(symbol, '15m')
       
        # Skip if any timeframe failed
        if None in [daily_pos, hourly_pos, min15_pos]:
            return None
       
        # Check for alignment
        all_above = (daily_pos == 'above' and hourly_pos == 'above' and min15_pos == 'above')
        all_below = (daily_pos == 'below' and hourly_pos == 'below' and min15_pos == 'below')
       
        if all_above:
            return {
                'Symbol': symbol,
                'Signal': '🟢 BULLISH (All Above SMA50)',
                'Daily_Price': daily_price,
                'Daily_SMA50': daily_sma,
                '1HR_Price': hourly_price,
                '1HR_SMA50': hourly_sma,
                '15min_Price': min15_price,
                '15min_SMA50': min15_sma,
                'Daily': '✅ Above',
                '1HR': '✅ Above',
                '15min': '✅ Above'
            }
        elif all_below:
            return {
                'Symbol': symbol,
                'Signal': '🔴 BEARISH (All Below SMA50)',
                'Daily_Price': daily_price,
                'Daily_SMA50': daily_sma,
                '1HR_Price': hourly_price,
                '1HR_SMA50': hourly_sma,
                '15min_Price': min15_price,
                '15min_SMA50': min15_sma,
                'Daily': '❌ Below',
                '1HR': '❌ Below',
                '15min': '❌ Below'
            }
       
        return None  # Not aligned across all timeframes
       
    except Exception as e:
        return None
 
def scan_multi_timeframe():
    """Main scanning function for multi-timeframe analysis"""
    print("="*70)
    print(" MULTI-TIMEFRAME SMA 50 SCANNER")
    print(" Daily + 1HR + 15min Alignment")
    print(" S&P 500 + Nasdaq-100 + Dow Jones 30")
    print("="*70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print("\n📊 Logic: Find stocks where price is above/below SMA50")
    print("   on ALL 3 timeframes (Daily + 1HR + 15min)")
    print("="*70)
   
    # Load symbols
    symbols = load_symbols()
    if not symbols:
        input("\nPress Enter to exit...")
        return
   
    print(f"\nScanning {len(symbols)} stocks across 3 timeframes...")
    print("This will take approximately 15-20 minutes.")
    print("-"*70)
   
    aligned_stocks = []
    total_symbols = len(symbols)
   
    for i, symbol in enumerate(symbols, 1):
        # Progress indicator every 25 stocks
        if i % 25 == 0:
            print(f"Progress: {i}/{total_symbols} stocks scanned... ({len(aligned_stocks)} aligned found)")
       
        result = analyze_multi_timeframe(symbol)
       
        if result:
            aligned_stocks.append(result)
            print(f"[{i}/{total_symbols}] ✓ {symbol} - {result['Signal']}")
       
        # Delay to avoid rate limiting (more requests per stock now)
        time.sleep(0.3)
   
    print("\n" + "=" * 70)
    print(f" Scan Complete! Found {len(aligned_stocks)} stocks with aligned timeframes")
    print("=" * 70)
   
    if aligned_stocks:
        # Create DataFrame and save to CSV
        df_results = pd.DataFrame(aligned_stocks)
       
        # Sort by signal type
        df_results = df_results.sort_values('Signal')
       
        output_file = f"multi_tf_sma50_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        df_results.to_csv(output_file, index=False)
       
        print(f"\n✓ Results saved to: {output_file}\n")
       
        # Display results
        bullish = df_results[df_results['Signal'].str.contains('BULLISH')]
        bearish = df_results[df_results['Signal'].str.contains('BEARISH')]
       
        print(f"\n🟢 BULLISH - Price ABOVE SMA50 on Daily + 1HR + 15min: {len(bullish)}")
        print("-"*70)
        if not bullish.empty:
            display_cols = ['Symbol', 'Daily_Price', 'Daily_SMA50', '1HR_Price', '1HR_SMA50', '15min_Price', '15min_SMA50']
            print(bullish[display_cols].to_string(index=False))
        else:
            print("No stocks found")
       
        print(f"\n🔴 BEARISH - Price BELOW SMA50 on Daily + 1HR + 15min: {len(bearish)}")
        print("-"*70)
        if not bearish.empty:
            display_cols = ['Symbol', 'Daily_Price', 'Daily_SMA50', '1HR_Price', '1HR_SMA50', '15min_Price', '15min_SMA50']
            print(bearish[display_cols].to_string(index=False))
        else:
            print("No stocks found")
       
        print("\n" + "=" * 70)
    else:
        print("\n❌ No stocks found with all 3 timeframes aligned.")
   
    input("\nPress Enter to exit...")
 
if __name__ == "__main__":
    scan_multi_timeframe()