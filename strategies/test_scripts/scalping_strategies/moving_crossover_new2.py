import vectorbt as vbt
import numpy as np
import yfinance as yf

# Load data
ticker = 'AAPL'
start_date = '2020-01-01'
end_date = '2021-01-01'
price = yf.download(ticker, start=start_date, end=end_date)['Close']

# Define moving average crossover strategy
def moving_average_crossover(price, short_window, long_window):
    short_ma = price.rolling(window=short_window).mean()
    long_ma = price.rolling(window=long_window).mean()
    entries = short_ma > long_ma
    exits = short_ma < long_ma
    return entries, exits

# Define parameter ranges
short_window_range = np.arange(5, 20)
long_window_range = np.arange(10, 25, 5)

# Run optimization
short_windows, long_windows = np.meshgrid(short_window_range, long_window_range, indexing='ij')
import pdb
pdb.set_trace()
entries, exits = moving_average_crossover(price, short_windows, long_windows)

pf = vbt.Portfolio.from_signals(
    close=price,
    entries=entries,
    exits=exits
)

# Optimize for a specific metric, e.g., total return
total_return = pf.total_return()
best_params = np.unravel_index(np.argmax(total_return.values), total_return.shape)
best_short_window = short_window_range[best_params[0]]
best_long_window = long_window_range[best_params[1]]

print(f'Best short window: {best_short_window}, Best long window: {best_long_window}')

# Analyze the results
best_pf = pf[(best_short_window, best_long_window)]
stats = best_pf.stats()
print(stats)
