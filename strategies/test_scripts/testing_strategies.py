import pandas as pd
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA, GOOG

# Define strategies
class MACDStrategy(Strategy):
    fast = 12
    slow = 26
    signal = 9

    def init(self):
        self.macd = self.I(lambda x: pd.Series(pd.Series(x).ewm(span=self.fast, adjust=False).mean() - pd.Series(x).ewm(span=self.slow, adjust=False).mean()), self.data.Close)
        self.signal_line = self.I(lambda x: pd.Series(pd.Series(x).ewm(span=self.signal, adjust=False).mean()), self.macd)
    
    def next(self):
        if crossover(self.macd, self.signal_line):
            self.buy()
        elif crossover(self.signal_line, self.macd):
            self.sell()

class MovingAverageStrategy(Strategy):
    short_window = 10
    long_window = 50

    def init(self):
        self.short_ma = self.I(SMA, self.data.Close, self.short_window)
        self.long_ma = self.I(SMA, self.data.Close, self.long_window)
    
    def next(self):
        if crossover(self.short_ma, self.long_ma):
            self.buy()
        elif crossover(self.long_ma, self.short_ma):
            self.sell()

class RSIStrategy(Strategy):
    rsi_period = 14
    rsi_overbought = 70
    rsi_oversold = 30

    def init(self):
        self.rsi = self.I(lambda x: pd.Series(x).rolling(self.rsi_period).apply(lambda r: 100 - (100 / (1 + (r[-1] - r.mean()) / r.std())), raw=False), self.data.Close)
    
    def next(self):
        if self.rsi[-1] < self.rsi_oversold:
            self.buy()
        elif self.rsi[-1] > self.rsi_overbought:
            self.sell()

# Define the symbols, durations, parameters, and test periods
symbols = ["MSFT", "NVDA", "TSLA"]
durations = ["1m", "3m", "5m", "15m", "30m", "1h", "4h", "1d"]
params = {
    "MACD": [(12, 26, 9), (10, 21, 5)],
    "MovingAverage": [(10, 50), (20, 100)],
    "RSI": [(14, 70, 30)]
}
test_durations = ["2 months", "6 months", "1 yr", "2 yr", "3 yr"]

# Function to simulate data for each symbol and duration (replace with actual data fetching)
def get_data(symbol, duration):
    # For simplicity, use the same GOOG data; replace with actual data fetching logic
    return GOOG

# Function to run backtest and document results
def run_backtests():
    results = []
    trades = []
    
    for strategy_name, param_sets in params.items():
        for symbol in symbols:
            for duration in durations:
                data = get_data(symbol, duration)
                
                for param_set in param_sets:
                    for test_duration in test_durations:
                        bt = None
                        if strategy_name == "MACD":
                            bt = Backtest(data, MACDStrategy, cash=10000, commission=.002)
                            MACDStrategy.fast, MACDStrategy.slow, MACDStrategy.signal = param_set
                        elif strategy_name == "MovingAverage":
                            bt = Backtest(data, MovingAverageStrategy, cash=10000, commission=.002)
                            MovingAverageStrategy.short_window, MovingAverageStrategy.long_window = param_set
                        elif strategy_name == "RSI":
                            bt = Backtest(data, RSIStrategy, cash=10000, commission=.002)
                            RSIStrategy.rsi_period, RSIStrategy.rsi_overbought, RSIStrategy.rsi_oversold = param_set
                        
                        stats = bt.run()
                        result = {
                            "Strategy": strategy_name,
                            "Symbol": symbol,
                            "Duration": duration,
                            "Params": param_set,
                            "Test Duration": test_duration,
                            "Stats": stats
                        }
                        results.append(result)
                        
                        trade_details = stats._trades
                        trades.append({
                            "Strategy": strategy_name,
                            "Symbol": symbol,
                            "Duration": duration,
                            "Params": param_set,
                            "Test Duration": test_duration,
                            "Trades": trade_details
                        })
    
    results_df = pd.DataFrame(results)
    trades_df = pd.DataFrame(trades)
    results_df.to_csv("backtest_results.csv", index=False)
    trades_df.to_csv("backtest_trades.csv", index=False)

run_backtests()
