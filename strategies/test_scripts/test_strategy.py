import pandas as pd
# import pandas_ta as ta
import talib as ta
import yfinance as yf
from backtesting import Backtest, Strategy
from backtesting.lib import crossover
from backtesting.test import SMA


def fetch_stock_data(ticker, start, end):
    """
    Fetch historical stock data for the given ticker using yfinance.
    """
    return yf.download(ticker, start=start, end=end)

def EMA(df_in, window):
    df = df_in.copy()    
    ema_series = ta.ema(df['Close'], length=window)    
    return ema_series

def below_zero(macd, signal):
    if macd < 0 and signal < 0:
        return True
    
def above_zero(macd, signal):
    if macd > 0 and signal > 0:
        return True

class MACDRSIStrategy(Strategy):
    def init(self):
        # Short and long period for MACD
        # self.short_ema = self.I(ta.ema, self.data.Close, 12)
        # self.long_ema = self.I(ta.ema, self.data.Close, 26)
        # self.macd = self.short_ema - self.long_ema
        # self.signal = self.I(ta.ema, self.macd, 9)
        # self.ema200 = self.I(ta.ema, self.data.Close.to_series(), 100)

        # self.macd = self.I(ta.macd, self.data.Close.to_series(), 12, 26, 9)

        self.ema200 = self.I(ta.EMA, self.data.Close, timeperiod=200)

        self.macd, self.macdsignal, _ = self.I(ta.MACD, self.data.Close, fastperiod=12, slowperiod=26, signalperiod=9)

    
        
        # RSI period2
        # self.rsi = self.I(talib.RSI, self.data.Close, 14)
        
    def next(self):
        # macd_line = self.macd[0]
        # signal_line = self.macd[2]
        # # import pdb
        # # pdb.set_trace()

        # # and macd_line < 0 and signal_line < 0
        # if crossover(macd_line, signal_line) :
        #     # self.position.close()
        #     self.buy()
        # elif crossover(signal_line, macd_line) and macd_line > 0 and signal_line > 0:
        #     # self.position.close()
        #     self.sell()

        if self.data.Close[-1] > self.ema200[-1] and crossover(self.macd, self.macdsignal) and self.macd[-1] < 0 and self.macdsignal[-1] < 0:
            self.buy()
        
        # Exit signal: MACD crosses below the signal line
        elif self.data.Close[-1] < self.ema200[-1] and crossover(self.macdsignal, self.macd) and self.macd[-1] > 0 and self.macdsignal[-1] > 0:
            self.sell()

if __name__ == "__main__":
    # Fetch stock data
    ticker = 'GME'
    # start_date = '2024-05-24'
    # end_date = '2024-01-19'
    # data = fetch_stock_data(ticker, start=start_date, end=end_date, interval="1m")
    # data = fetch_stock_data(ticker, period="5d", interval="1m")
    data = yf.download(ticker, period="5d", interval="1m")
    # import pdb
    # pdb.set_trace()

    
    # Prepare data for backtesting
    data.index.name = 'Date'
    data.columns = ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']
    
    # Run backtest
    bt = Backtest(data, MACDRSIStrategy, cash=10000, commission=.002)
    stats = bt.run()
    
    # Print results
    # print(stats)
    print(stats['_trades'])
    
    # Plot results
    bt.plot()

#TODO: add stop loss
#TODO: complete this one strategy to include all small increments of changes and make sure it works well 
#TODO: volume scripts
#TODO: using indicators build a small LSTM model 
#TODO: use price action in a market that is choppy
#TODO: Indicators to use: RSI, VWAP, Bollinger Bands    