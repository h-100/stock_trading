import pandas as pd
import yfinance as yf


def compute_volatility(ticker, start_date, end_date):
    # Fetch historical data
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    
    # Calculate daily returns
    stock_data['Returns'] = stock_data['Adj Close'].pct_change()
    
    # Calculate volatility (standard deviation of returns)
    volatility = stock_data['Returns'].std() * (252 ** 0.5)  # Annualize the volatility
    
    return volatility

# Example usage
tickers = ['NFLX', 'NVDA', 'AMZN', 'TSLA', 'GOOG', 'META', 'MSFT']
start_date = '2024-05-01'
end_date = '2024-07-01'

volatility_list = {}

for ticker in tickers:
    volatility_list[ticker] = compute_volatility(ticker, start_date, end_date)
# volatility = compute_volatility(ticker, start_date, end_date)
sorted_dict = dict(sorted(volatility_list.items(), key=lambda item: item[1]))
print(f"The annualized volatility of {tickers} from {start_date} to {end_date} is {sorted_dict}")
