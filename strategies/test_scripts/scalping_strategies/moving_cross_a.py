# import requests
# import pandas as pd

# # Replace with your Alpha Vantage API key
# api_key = '8T9B4J4ZDAWZF7SD'
# symbol = 'AAPL'
# interval = '1min'
# outputsize = 'full'

# # API URL
# url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&outputsize={outputsize}&apikey={api_key}'

# # Get data
# response = requests.get(url)
# data = response.json()

# time_series = data.get(f'Time Series ({interval})', {})
# df = pd.DataFrame

# # Convert index to datetime
# df.index = pd.to_datetime(df.index)
# df = df.sort_index()

# # Optionally save to CSV
# df.to_csv('stock_data.csv')

# print(df.head())

import requests

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=NVDA&interval=1min&apikey=8T9B4J4ZDAWZF7SD&month=2023-01'
r = requests.get(url)
data = r.json()
import pdb
pdb.set_trace()
print(data)