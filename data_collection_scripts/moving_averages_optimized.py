import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import os
from datetime import datetime

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
        (data[short_window] > data[long_window]) &
        (data['Slope_' + short_window].abs() > slope_threshold) &
        (data['Slope_' + long_window].abs() > slope_threshold),
        1.0, 0.0)

    # Sell signal
    signals['Signal'] = np.where(
        (data[short_window] < data[long_window]) &
        (data['Slope_' + short_window].abs() > slope_threshold) &
        (data['Slope_' + long_window].abs() > slope_threshold),
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

def trading_simulation(data, initial_cash):
    
    file = open('output.csv', 'a')
    

    cash = initial_cash
    shares = 0
    portfolio_value = []
    buy_price = 0
    trades = pd.DataFrame()
    trades = []
    buy_date = None
    buy_value = None

    for i in range(len(data)):
        if data['Signal'].iloc[i] == 1.0 and cash > 0:  # Buy signal
            shares = cash // data['close'].iloc[i]
            buy_price = data['close'].iloc[i]
            total_cash_used = shares * buy_price
            cash -= total_cash_used
            buy_date = data['timestamp'].iloc[i]
            buy_value = total_cash_used
            num_shares_bought = shares
                       
            # line =f'{data['timestamp'].iloc[i]}, {buy_price}, {shares}'
        elif data['Signal'].iloc[i] == -1.0 and shares > 0:  # Sell signal
            cash += shares * data['close'].iloc[i]
            shares = 0
            if buy_date is not None:
                profit_or_loss = (shares * data['close'].iloc[i]) - buy_value
                sell_date = data['timestamp'].iloc[i]
                sell_value = data['close'].iloc[i]
                trades.append({
                'buy_date': buy_date,
                'sell_date': sell_date,
                'buy_value': buy_value,
                'num_shares_bought': num_shares_bought,
                'sell_value': sell_value,
                'profit_or_loss': profit_or_loss
                })
                """
                TODO:
                add intervals, strategy_name, run_id, strategy parameters  
                """
            buy_date = None

        # Calculate current portfolio value
        portfolio_value.append(cash + shares * data['close'].iloc[i])

    return portfolio_value, cash + shares * data['close'].iloc[-1]


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
  slope_threshold = 0.01  # Adjust based on your specific requirements

  signals = crossover_signal(stock_data, key_small, key_large, slope_threshold)
  stock_data['Signal'] = signals['Signal']

  initial_cash = 10000  # Initial cash amount
  stock_data['Portfolio_Value'], final_portfolio_value = trading_simulation(stock_data, initial_cash)

  print(f"Final Portfolio Value: ${final_portfolio_value:.2f}")

if __name__ == "__main__":
    main()


