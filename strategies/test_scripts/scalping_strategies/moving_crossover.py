import pandas as pd
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA

# Define the Moving Average Crossover strategy
class MACrossover(Strategy):
    n1 = 7
    n2 = 13

    def init(self):
        self.sma1 = self.I(SMA, self.data.Close, self.n1)
        self.sma2 = self.I(SMA, self.data.Close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.sell()

# Fetch NVDA stock data with 5-minute candlesticks
symbol = 'NVDA'
data = yf.download(symbol, start='2024-05-01', end='2024-07-01', interval='1h')
# Prepare the data for backtesting.py
data = data[['Open', 'High', 'Low', 'Close', 'Volume']]

# Run the backtest
bt = Backtest(data, MACrossover, cash=10000, commission=0.002)
stats = bt.run()

# Save the results to a CSV file
results = {
    'Profit': [stats['Equity Final [$]'] - 10000],
    'Candlestick Interval': ['1h'],
    'Stock Name': [symbol],
    'MA Values': ['7, 13']
}

results_df = pd.DataFrame(results)
results_df.to_csv('backtest_results.csv', index=False)

# Print the results
print(results_df)

#### candlestick intervals: yahoo finance does not give enough data, so we can't have a uniform number of 
#### candlestick patterns