import pandas as pd
import yfinance as yf

df = pd.read_csv('companylist.csv')

print(df['Symbol'])
increased_symbols = []

for stock in df['Symbol']:
    stock = stock.upper()
    if '^' in stock:
        pass
    else:
        try:
            stock_info = yf.Ticker(stock)
            hist = stock_info.history(period="5d")
            previous_averaged_volume = hist['Volume'].iloc[1:4:1].mean()
            todays_volume = hist['Volume'][-1]
            if todays_volume #greater than previous_averaged_volume * 4
                increased_symbols.append(stock)
        except:
            pass

print(increased_symbols)