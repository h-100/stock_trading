import pandas as pd
import time
from alpha_vantage.timeseries import TimeSeries
import vectorbt as vbt
import pdb

# Define your Alpha Vantage API key
api_key = '8T9B4J4ZDAWZF7SD'

# Initialize the TimeSeries class with your API key
ts = TimeSeries(key=api_key, output_format='pandas')

# Function to fetch data in chunks
def fetch_data_in_chunks(symbol, start_date, end_date, interval='5min'):
    date_range = pd.date_range(start=start_date, end=end_date, freq='ME')  # Monthly frequency
    all_data = pd.DataFrame()
    import pdb
    pdb.set_trace()
    
    for i in range(len(date_range) - 1):
        try:
            data, meta_data = ts.get_intraday(symbol=symbol, interval=interval, outputsize='full')
            # Alpha Vantage returns all available data, so we filter by date range manually
            data = data[(data.index >= date_range[i].strftime('%Y-%m-%d')) & (data.index < date_range[i + 1].strftime('%Y-%m-%d'))]
            all_data = pd.concat([all_data, data])
            time.sleep(60)  # To respect API rate limits
        except Exception as e:
            print(f"Error fetching data for {date_range[i]}: {e}")
            time.sleep(60)  # To respect API rate limits
    
    # Sort the data by date
    all_data.sort_index(inplace=True)
    return all_data

# Fetch data for NVDA from 1 May 2022 to 1 May 2024
symbol = 'NVDA'
start_date = '2022-05-01'
end_date = '2024-05-01'
interval = '5min'

# Retrieve data
data = fetch_data_in_chunks(symbol, start_date, end_date, interval)
pdb.set_trace()
# Save the raw data to a CSV file
data.to_csv('NVDA_5min_raw_data.csv')
print("Raw data saved to NVDA_5min_raw_data.csv")

# Prepare the data for vectorbt
data.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
close_prices = data['Close']

# Define the moving average strategy
short_window = 7
long_window = 13

# Calculate short and long moving averages
short_ma = close_prices.rolling(window=short_window).mean()
long_ma = close_prices.rolling(window=long_window).mean()

# Generate signals
entries = short_ma > long_ma
exits = short_ma < long_ma

# Backtest the strategy
pf = vbt.Portfolio.from_signals(close_prices, entries, exits, init_cash=10000, fees=0.001)
pdb.set_trace()
# Save the portfolio statistics
stats = pf.stats()
stats.to_csv('NVDA_MA_strategy_stats.csv')
print("Strategy statistics saved to NVDA_MA_strategy_stats.csv")

# Display the profits
print(stats)

# Save detailed trades to CSV
trades = pf.trades.records
trades.to_csv('NVDA_MA_strategy_trades.csv')
print("Detailed trades saved to NVDA_MA_strategy_trades.csv")

# Plot the equity curve
pf.plot().show()
