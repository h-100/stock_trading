import pandas as pd
import yfinance as yf
import vectorbt as vbt
import talib

# Fetch stock data
def fetch_stock_data(ticker, start, end):
    """
    Fetch historical stock data for the given ticker using yfinance.
    """
    # data = yf.download(ticker, start=start, end=end)
    data = yf.download(ticker, period="5d", interval="1m")
    return data['Close']

# Define the strategy
def macd_rsi_strategy(close, macd_params, rsi_params):
    fast_ema = close.ewm(span=macd_params['fast'], adjust=False).mean()
    slow_ema = close.ewm(span=macd_params['slow'], adjust=False).mean()
    macd = fast_ema - slow_ema
    signal = macd.ewm(span=macd_params['signal'], adjust=False).mean()
    macd_hist = macd - signal

    # rsi = vbt.IndicatorFactory.from_pandas_ta('RSI').run(close, window=rsi_params['window'])
    rsi = vbt.RSI.run(close, window=rsi_params['window'])
    # import pdb
    # pdb.set_trace()
    
    entries = (macd > signal) & (macd < 0) & (rsi.rsi_below(30))
    exits = (macd < signal) & (macd > 0 ) & (rsi.rsi_above(70))
    
    return entries, exits

if __name__ == "__main__":
    # Parameters
    ticker = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2023-01-01'
    macd_params = {'fast': 12, 'slow': 26, 'signal': 9}
    rsi_params = {'window': 14}

    # Fetch stock data
    close = fetch_stock_data(ticker, start=start_date, end=end_date)

    # Get signals
    entries, exits = macd_rsi_strategy(close, macd_params, rsi_params)

    # Run backtest
    pf = vbt.Portfolio.from_signals(close, entries, exits, init_cash=10000, fees=0.002)
    stats = pf.stats()

    # Print results
    print(stats)

    # Plot results
    pf.plot().show()
