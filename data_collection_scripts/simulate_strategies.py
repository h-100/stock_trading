import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime
import pdb

def read_stock_data(stock_name, interval, start_date, end_date):
    # Convert the date strings to datetime objects
    start_date = datetime.strptime(start_date, "%d-%m-%Y").replace(hour=0, minute=0, second=0)
    end_date = datetime.strptime(end_date, "%d-%m-%Y").replace(hour=23, minute=59, second=59)
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']

    # Create a list of file names that fall within the start and end dates
    files_to_read = []
    for year in range(start_date.year, end_date.year + 1):
        for month in months:
            if start_date.year == end_date.year and start_date.month <= int(month) <= end_date.month:
                file_name = f"{stock_name}-{interval}-{month}-{year}.csv"
            elif start_date.year < end_date.year:
                if year == start_date.year and int(month) >= start_date.month:
                    file_name = f"{stock_name}-{interval}-{month}-{year}.csv"
                elif year == end_date.year and int(month) <= end_date.month:
                    file_name = f"{stock_name}-{interval}-{month}-{year}.csv"
                elif start_date.year < year < end_date.year:
                    file_name = f"{stock_name}-{interval}-{month}-{year}.csv"
                else:
                    continue
            else:
                continue
            
            folder_name = f'data/{stock_name}'
            file_path = os.path.join(folder_name, file_name)

            if os.path.exists(file_path):
                files_to_read.append(file_path)

    # Read the relevant data from the files
    df_list = []


    for file in files_to_read:
        df = pd.read_csv(file, parse_dates=['timestamp'])
        df_list.append(df)

    # Concatenate all the dataframes
    all_data = pd.concat(df_list)

    # Filter the data based on the start and end dates
    filtered_data = all_data[(all_data['timestamp'] >= start_date) & (all_data['timestamp'] <= end_date)]
    # Assuming df is your DataFrame and it has a 'timestamp' column
    filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
    filtered_data_sorted = filtered_data.sort_values(by='timestamp')

    return filtered_data_sorted

# Calculate the slope of the moving averages
def calculate_slope(series, period):
    return (series - series.shift(period)) / period

# Identify crossover signals
def crossover_signal(data, small_win, long_win):
    key_small = f'SMA_{small_win}'
    key_large = f'SMA_{long_win}'
  
    data[key_small] = data['close'].rolling(window=int(small_win)).mean()
    data[key_large] = data['close'].rolling(window=int(long_win)).mean()

    key_slope_small = f'Slope_{key_small}'
    key_slope_large = f'Slope_{key_large}'

  
    data[key_slope_small] = calculate_slope(data[key_small], period=int(small_win))
    data[key_slope_large] = calculate_slope(data[key_large], period=int(long_win))

    # Set the slope threshold
    slope_threshold = 0.05 # Adjust based on your specific requirements
    area_threshold = 0.07
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0
    
    # pdb.set_trace()
    data['Signals'] = 0

    data['Slope_Area'] = np.abs(data[key_slope_small] - data[key_slope_large])
    data['Signals'][int(small_win):] = np.where(data[key_small][int(small_win):] > data[key_large][int(small_win):], 1, 0)

    signals['Signal'] = data['Signals'].diff()

    return signals

import pandas as pd

def compute_macd_signals(prices, short_window=12, long_window=26, signal_window=9):
 
    # Calculate the short-term EMA
    short_ema = prices.ewm(span=short_window, adjust=False).mean()
    
    # Calculate the long-term EMA
    long_ema = prices.ewm(span=long_window, adjust=False).mean()
    
    # Calculate the MACD line
    macd = short_ema - long_ema
    
    # Calculate the signal line
    signal_line = macd.ewm(span=signal_window, adjust=False).mean()
    
    # Create a DataFrame to store the values
    df = pd.DataFrame({'Prices': prices, 'MACD': macd, 'Signal_Line': signal_line})
    
    # Create buy/sell signals
    df['Signals'] = 0
    df['Signals'][short_window:] = \
        [1 if macd.iloc[i] > signal_line.iloc[i] and macd.iloc[i - 1] <= signal_line.iloc[i - 1] else
         -1 if macd.iloc[i] < signal_line.iloc[i] and macd.iloc[i - 1] >= signal_line.iloc[i - 1] else 0
         for i in range(short_window, len(macd))]
    
    df['Signal'] = df['Signals'].diff()
    
    return df


def plot_(stock_data):
  
  plt.figure(figsize=(14, 7))
  df = pd.DataFrame(stock_data)
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df.set_index('timestamp', inplace=True)

  plt.plot(df.index, df['close'], label='Close Price')

  # Plot buy signals
 
  
  for i in df.loc[df['Signal'] == 1.0].index:
    plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='g', va='bottom')

  # Plot sell signals
  
  for i in df.loc[df['Signal'] == -1.0].index:
    plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='r', va='bottom')

  plt.title('Stock Price with Buy and Sell Signals')
  plt.xlabel('Date')
  plt.ylabel('Price')
  plt.legend()
  plt.grid(True)

  plt.tight_layout()
  plt.show()

    
def plot(stock_data, small, large):
  key_small = f'SMA_{small}'
  key_large = f'SMA_{large}'



# Plot the stock price with buy and sell signals
  label1 = f'{small}-day SMA'
  label2 = f'{large}-day SMA'
  plt.figure(figsize=(14, 7))
  df = pd.DataFrame(stock_data)
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df.set_index('timestamp', inplace=True)

  plt.plot(df.index, df['close'], label='Close Price')
  plt.plot(df[key_small], label=label1)
  plt.plot(df[key_large], label=label2)

  # Plot buy signals
  plt.plot(df.loc[df['Signal'] == 1.0].index, 
          df[key_small][df['Signal'] == 1.0], 
          '^', markersize=10, color='g', label='Buy Signal')
  
  for i in df.loc[df['Signal'] == 1.0].index:
    plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='g', va='bottom')

  # Plot sell signals
  plt.plot(df.loc[df['Signal'] == -1.0].index, 
          df[key_small][df['Signal'] == -1.0], 
          'v', markersize=10, color='r', label='Sell Signal')
  
  for i in df.loc[df['Signal'] == -1.0].index:
    plt.text(i, df['close'][i], f'{df['close'][i]:.2f}', fontsize=9, ha='center', color='r', va='bottom')

  plt.title('Stock Price with Buy and Sell Signals')
  plt.xlabel('Date')
  plt.ylabel('Price')
  plt.legend()
  plt.grid(True)

  plt.tight_layout()
  plt.show()

def get_string_name(strategy_parameters):
    # pdb.set_trace()
    name = ''
    for key, value in strategy_parameters.items():
        name += f'{str(key)}_{str(value)}'

    return name

def trading_simulation(stock_data, initial_cash, strategy_name, strategy_parameters, interval, stock_name, start_date, end_date):
    
    trades = []
    position = None

    strategy_name = get_string_name(strategy_parameters)
    file_name = f'{stock_name}_{interval}_{strategy_name}_{strategy_name}_{start_date}_{end_date}.csv'

    cash_balance = initial_cash

    for i, row in stock_data.iterrows():
        if row['Signal'] == 1 and position is None:  # Buy signal and no current position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],  # Example: Buying $100 worth of shares
                'position_type': 'long',
                'cash_balance': cash_balance
            }
            cash_balance -= position['num_shares'] * row['close']  # Adjust cash balance for purchase

        elif row['Signal'] == -1 and position is None:  # Sell short signal and no current position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],  # Example: Selling short $100 worth of shares
                'position_type': 'short',
                'cash_balance': cash_balance
            }
            cash_balance += position['num_shares'] * row['close']

        elif row['Signal'] == -1 and position is not None and position['position_type'] == 'long':  # Sell signal for long position
            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['sell_value'] - position['buy_value']) * position['num_shares']

            cash_balance += position['num_shares'] * position['sell_value']  # Adjust cash balance for sale
            position['cash_balance'] = cash_balance

            trades.append(position)
            position = None  # Clear the position

        elif row['Signal'] == 1 and position is not None and position['position_type'] == 'short':  # Buy to cover signal for short position
            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['buy_value'] - position['sell_value']) * position['num_shares']
            cash_balance -= position['num_shares'] * position['sell_value']  # Adjust cash balance for covering
            position['cash_balance'] = cash_balance
            trades.append(position)
            position = None  # Clear the position

    # Convert trades list to DataFrame
    trades_df = pd.DataFrame(trades)

    # Save to CSV

    folder_name = f'data/trade_iterations'
    file_path = os.path.join(folder_name, file_name)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    trades_df.to_csv(file_path, index=False)

    if trades_df.empty:
        print("No trades")

    else:
        final_cash_balance = trades_df['cash_balance'].iloc[-1]
        print(f"Final Profit: ${final_cash_balance - initial_cash}")

    return trades_df


def main():

  if (len(sys.argv[1:]) < 6 or len(sys.argv[1:]) > 6 ):
    print("Please enter arguments: stock, start_date, end_date, interval with spaces")
    sys.exit()

  stock, start_date, end_date, interval, small, large = sys.argv[1:]  
  stock_data = read_stock_data(stock, interval, start_date, end_date)
 
  initial_cash = 10000 # Initial cash amount
  
  current_strategy = 'MACD'

  current_strategy_params = {
        'small': '7',
        'long': '14'
    }
  
  if current_strategy == 'MA CrossOver':
      signals = crossover_signal(stock_data, current_strategy_params['small'], current_strategy_params['long'])

  elif current_strategy == 'MACD':
    signals = compute_macd_signals(stock_data, short_window=12, long_window=26, signal_window=9)

    
  stock_data['Signal'] = signals['Signal']
  trading_simulation(stock_data, initial_cash, current_strategy, current_strategy_params, interval, stock, start_date, end_date)

  if current_strategy == 'MA CrossOver':
    plot(stock_data, small, large)
  elif current_strategy == 'MACD':
    plot_(stock_data)
      


  

if __name__ == "__main__":
    main()


