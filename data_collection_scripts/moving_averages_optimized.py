import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
from datetime import datetime
import pdb

def read_stock_data(stock_name, interval, start_date, end_date):
    # Convert the date strings to datetime objects
    # start_date = datetime.strptime(start_date, "%d-%m-%Y")
    start_date = datetime.strptime(start_date, "%d-%m-%Y").replace(hour=0, minute=0, second=0)
    # end_date = datetime.strptime(end_date, "%d-%m-%Y")
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
def calculate_slope(series, period=1):
    return (series - series.shift(period)) / period

# Identify crossover signals
def crossover_signal(data, short_window, long_window, slope_threshold):
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0

    # Buy signal
    signals['Signal'] = np.where(
        (data[short_window] > data[long_window]),
      #  (data['Slope_' + short_window].abs() > slope_threshold) &
      #  (data['Slope_' + long_window].abs() > slope_threshold),
        1.0, signals['Signal'])

    # Sell signal
    signals['Signal'] = np.where(
        (data[short_window] < data[long_window]),
      #  (data['Slope_' + short_window].abs() > slope_threshold) &
      #   (data['Slope_' + long_window].abs() > slope_threshold),
          -1.0, signals['Signal'])

    return signals

def plot(stock_data, small, large):
  key_small = f'SMA_{small}'
  key_large = f'SMA_{large}'



# Plot the stock price with buy and sell signals
  label1 = f'{small}-day SMA'
  label2 = f'{large}-day SMA'
  plt.figure(figsize=(14, 7))
  plt.plot(stock_data['close'], label='Close Price')
  plt.plot(stock_data[key_small], label=label1)
  plt.plot(stock_data[key_large], label=label2)

  # Plot buy signals
  plt.plot(stock_data.loc[stock_data['Signal'] == 1.0].index, 
          stock_data[key_small][stock_data['Signal'] == 1.0], 
          '^', markersize=10, color='g', label='Buy Signal')

  # Plot sell signals
  plt.plot(stock_data.loc[stock_data['Signal'] == -1.0].index, 
          stock_data[key_small][stock_data['Signal'] == -1.0], 
          'v', markersize=10, color='r', label='Sell Signal')

  plt.title('Stock Price with Buy and Sell Signals')
  plt.xlabel('Date')
  plt.ylabel('Price')
  plt.legend()
  plt.show()


import pandas as pd

def trading_simulation(stock_data, initial_cash, strategy_name, strategy_parameters, interval, stock_name, start_date, end_date):
    
    trades = []
    position = None
    file_name = f'{stock_name}_{interval}_{strategy_name}_{strategy_parameters}_{start_date}_{end_date}.csv'

    for i, row in stock_data.iterrows():
        if row['Signal'] == 1 and position is None:  # Buy signal and no current position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],  # Example: Buying $100 worth of shares
                'position_type': 'long'
            }
        elif row['Signal'] == -1 and position is None:  # Sell short signal and no current position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],  # Example: Selling short $100 worth of shares
                'position_type': 'short'
            }

        elif row['Signal'] == -1 and position is not None and position['position_type'] == 'long':  # Sell signal for long position
            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['sell_value'] - position['buy_value']) * position['num_shares']
            trades.append(position)
            position = None  # Clear the position
        elif row['Signal'] == 1 and position is not None and position['position_type'] == 'short':  # Buy to cover signal for short position
            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['buy_value'] - position['sell_value']) * position['num_shares']
            trades.append(position)
            position = None  # Clear the position

    # Convert trades list to DataFrame
    trades_df = pd.DataFrame(trades)

    # Save to CSV
    trades_df.to_csv(file_name, index=False)
    print(f"Total Profit: ${trades_df['profit_loss'].sum()}")
    print(f"Total Profit (only +ve trades): ${trades_df['profit_loss'][trades_df['profit_loss'] > 0].sum()}")

    return trades_df


def main():

  if (len(sys.argv[1:]) < 6 or len(sys.argv[1:]) > 6 ):
    print("Please enter arguments: stock, start_date, end_date, interval with spaces")
    sys.exit()

  stock, start_date, end_date, interval, small, large = sys.argv[1:]  
  stock_data = read_stock_data(stock, interval, start_date, end_date)
  # Calculate short-term and long-term moving averages
  key_small = f'SMA_{small}'
  key_large = f'SMA_{large}'
  stock_data[key_small] = stock_data['close'].rolling(window=int(small)).mean()
  stock_data[key_large] = stock_data['close'].rolling(window=int(large)).mean()

  key_slope_small = f'Slope_{key_small}'
  key_slope_large = f'Slope_{key_large}'

  stock_data[key_slope_small] = calculate_slope(stock_data[key_small], period=1)
  stock_data[key_slope_large] = calculate_slope(stock_data[key_large], period=1)

  # Set the slope threshold
  slope_threshold = 0 # Adjust based on your specific requirements

  signals = crossover_signal(stock_data, key_small, key_large, slope_threshold)
  stock_data['Signal'] = signals['Signal']

  initial_cash = 10000 # Initial cash amount
  strategy_parameters = f'{small}MA_{large}MA'
  trading_simulation(stock_data, initial_cash, 'MA CrossOver', strategy_parameters, interval, stock, start_date, end_date)

  

if __name__ == "__main__":
    main()


