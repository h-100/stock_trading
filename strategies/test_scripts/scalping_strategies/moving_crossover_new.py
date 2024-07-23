from tvDatafeed import TvDatafeed, Interval
from datetime import datetime, timedelta
import vectorbt as vbt
import pandas as pd
import pdb

# Initialize tvDatafeed with login credentials, or leave blank for anonymous access

username = 'huma.qureshi@gmail.com'
password = 'LetsWinThisTime00'

tv = TvDatafeed(username, password)

def calculate_trading_days(start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d')
    end = datetime.strptime(end_date, '%Y-%m-%d')
    
    delta = end - start
    trading_days = 0
    
    for i in range(delta.days + 1):
        day = start + timedelta(days=i)
        if day.weekday() < 5:  # Monday to Friday are trading days
            trading_days += 1
    
    return trading_days

def calculate_bars(start_date, end_date, interval_minutes):
    
    trading_days = calculate_trading_days(start_date, end_date)
    
    # Trading hours per day
    trading_hours_per_day = 6.5  # 9:30 AM to 4:00 PM
    trading_minutes_per_day = trading_hours_per_day * 60
    
    # Calculate the number of bars per trading day
    bars_per_day = trading_minutes_per_day / interval_minutes
    
    # Calculate total number of bars
    total_bars = trading_days * bars_per_day
    
    return total_bars


def fetch_data(symbol, exchange, interval, start_date, end_date):

    interval_minutes = 1       # Interval in minutes (e.g., 1 minute, 5 minutes, etc.)

    interval_minutes = {Interval.in_1_minute.value: 1, Interval.in_5_minute.value: 5, Interval.in_15_minute.value: 15, 
                        Interval.in_30_minute.value: 30, 
                        Interval.in_1_hour.value: 60, Interval.in_4_hour.value: 240}

    bars = calculate_bars(start_date, end_date, interval_minutes[interval.value])
    data = tv.get_hist(symbol=symbol, exchange=exchange, interval=interval, n_bars=round(bars))
    return data

# Define intervals
intervals = [Interval.in_5_minute, Interval.in_15_minute, Interval.in_30_minute, Interval.in_1_hour, Interval.in_4_hour]

# Define symbols and exchange
# 1 minute: 14 June - 6 July
symbol = 'AAPL'  # Example: Apple Inc.
exchange = 'NASDAQ'  # Adjust as per your target security
start_date = '2024-06-01'  # Start date
end_date = '2024-07-01'    # End date

# Function to backtest and save profits for all combinations

def backtest_strategy(symbol, exchange, intervals, s, l):
    results = []
    for interval in intervals:
        try:
            
          data = fetch_data(symbol, exchange, interval, start_date, end_date)
          
          # Prepare the data
          close = data['close']
          short_ma = close.rolling(window=s, min_periods=1).mean()
          long_ma = close.rolling(window=l, min_periods=1).mean()

          # Generate signals
          entries = short_ma > long_ma
          exits = short_ma < long_ma

          # Backtest the strategy
          pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000)

          # Store results
          profit = pf.total_return() * 100  # Profit as percentage
          results.append({
            'Stock Name': symbol,
            'MA Window': f'small: {s}, long: {l}',
            'Interval': str(interval),
            'Profit (%)': profit
        })
        except Exception as ex:
            pass

    return pd.DataFrame(results)

symbols = ['AAPL', 'NVDA', 'TSLA', 'MSFT']
small_ma = [5, 7, 11, 14]
long_ma = [7, 11, 14, 18]
strategies = ['MA', 'MACD', 'RSI']


results_df = pd.DataFrame()
for symbol in symbols:
    for s in small_ma:
        for l in long_ma:
          results = backtest_strategy(symbol, exchange, intervals, s, l)
          results_df = pd.concat([results_df, results])
    
# Save results to CSV
results_df.to_csv('backtest_results.csv', index=False)
print("Backtest results saved to 'backtest_results.csv'.")

# Print the results
print(results_df)

##TODO : move to another data source, or find another means of comparison
##TODO: optimize using vectorbt optimizations
##TODO: Just use yahoo finance if all options fail and choose a smaller 