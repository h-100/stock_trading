import pandas as pd
import time
from alpha_vantage.timeseries import TimeSeries
import vectorbt as vbt
import pdb

## paid key HXA9JB1IU4NTPEND

# Define your Alpha Vantage API key
api_key = '8T9B4J4ZDAWZF7SD'

# Initialize the TimeSeries class with your API key
ts = TimeSeries(key=api_key, output_format='pandas')
interval = '1min'

data, meta_data = ts.get_intraday(symbol='NVDA', interval='1min', outputsize='', month='2023-01')
data.to_csv('stock_data_new.csv')

import pdb
pdb.set_trace()
print(data)