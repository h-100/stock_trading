import pandas as pd
import talib as ta
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import \
    GOOG  # You can replace GOOG with any other dataset or load your own data


# Define the strategy
class MACD_EMA200_Strategy(Strategy):
    def init(self):
        # Calculate the 200-period EMA
        self.ema200 = self.I(ta.EMA, self.data.Close, timeperiod=200)
        
        # Calculate MACD
        self.macd, self.macdsignal, _ = self.I(ta.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)

    def next(self):
        # Entry signal: Price is above 200 EMA and MACD crosses above the signal line
        if self.data.Close[-1] > self.ema200[-1] and crossover(self.macd, self.macdsignal):
            self.buy()
        
        # Exit signal: MACD crosses below the signal line
        elif crossover(self.macdsignal, self.macd):
            self.sell()

# Load data (using GOOG sample data here, you can replace this with your own dataset)
data = GOOG

# Run the backtest
bt = Backtest(data, MACD_EMA200_Strategy, cash=10000, commission=.002)
stats = bt.run()

# Print the results
print(stats)

# Plot the results
bt.plot()
