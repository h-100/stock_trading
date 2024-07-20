import pandas as pd
import numpy as np
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
from datetime import datetime
import pdb

def read_stock_data(stock_name, interval, start_date, end_date):

    start_date = datetime.strptime(start_date, "%d-%m-%Y").replace(hour=0, minute=0, second=0)
    end_date = datetime.strptime(end_date, "%d-%m-%Y").replace(hour=23, minute=59, second=59)
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


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

  
    df_list = []


    for file in files_to_read:
        df = pd.read_csv(file, parse_dates=['timestamp'])
        df_list.append(df)

    
    all_data = pd.concat(df_list)

 
    filtered_data = all_data[(all_data['timestamp'] >= start_date) & (all_data['timestamp'] <= end_date)]
   
    filtered_data['timestamp'] = pd.to_datetime(filtered_data['timestamp'])
    filtered_data_sorted = filtered_data.sort_values(by='timestamp')

    return filtered_data_sorted


def calculate_slope(series, period):
    return (series - series.shift(period)) / period


def crossover_signal(data, small_win, long_win):
    key_small = f'SMA_{small_win}'
    key_large = f'SMA_{long_win}'
  
    data[key_small] = data['close'].rolling(window=int(small_win)).mean()
    data[key_large] = data['close'].rolling(window=int(long_win)).mean()

    key_slope_small = f'Slope_{key_small}'
    key_slope_large = f'Slope_{key_large}'

  
    data[key_slope_small] = calculate_slope(data[key_small], period=int(small_win))
    data[key_slope_large] = calculate_slope(data[key_large], period=int(long_win))


    slope_threshold = 0.05 
    area_threshold = 0.07
    signals = pd.DataFrame(index=data.index)
    signals['Signal'] = 0.0
    
    # pdb.set_trace()
    data['Signals'] = 0

    data['Signals'][int(small_win):] = np.where(data[key_small][int(small_win):] > data[key_large][int(small_win):], 1, 0)

    signals['Signal'] = data['Signals'].diff()

    return signals

def plot(stock_data, small, large):

  key_small = f'SMA_{small}'
  key_large = f'SMA_{large}'

  label1 = f'{small}-day SMA'
  label2 = f'{large}-day SMA'
  plt.figure(figsize=(14, 7))
  df = pd.DataFrame(stock_data)
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  df.set_index('timestamp', inplace=True)

  df.dropna(subset=['close', key_small, key_large], inplace=True)
    
  df['index'] = range(len(df))

  plt.plot(df['index'], df['close'], label='Close Price')
  plt.plot(df['index'], df[key_small], label=label1)
  plt.plot(df['index'], df[key_large], label=label2)

  plt.plot(df.loc[df['Signal'] == 1.0]['index'], 
             df[key_small][df['Signal'] == 1.0], 
             '^', markersize=10, color='g', label='Buy Signal')

  for i in df.loc[df['Signal'] == 1.0]['index']:
        plt.text(i, df['close'][df['index'] == i].values[0], f'{df["close"][df["index"] == i].values[0]:.2f}', fontsize=9, ha='center', color='g', va='bottom')

  plt.plot(df.loc[df['Signal'] == -1.0]['index'], 
             df[key_small][df['Signal'] == -1.0], 
             'v', markersize=10, color='r', label='Sell Signal')

  for i in df.loc[df['Signal'] == -1.0]['index']:
        plt.text(i, df['close'][df['index'] == i].values[0], f'{df["close"][df["index"] == i].values[0]:.2f}', fontsize=9, ha='center', color='r', va='bottom')

  plt.title('Stock Price with Buy and Sell Signals')
  plt.xlabel('Date')
  plt.ylabel('Price')
  plt.legend()
  plt.grid(True)

  n = max(1, len(df) // 10)  
  plt.xticks(ticks=df['index'][::n], labels=[date.strftime('%Y-%m-%d') for date in df.index][::n], rotation=45)

  plt.tight_layout()
  plt.tight_layout()
  plt.show()


def trading_simulation_shorting_logic(stock_data, initial_cash, strategy_name, strategy_parameters, interval, stock_name, start_date, end_date, borrow_rate=0.01):
    
    trades = []
    position = None
    file_name = f'{stock_name}_{interval}_{strategy_name}_{strategy_parameters}_{start_date}_{end_date}.csv'

    cash_balance = initial_cash

    for i, row in stock_data.iterrows():
        ## buy signal + no shares have been bought before position == short (shares have been bought before )
        """
        1. when buy singal == 1, normally we would just buy the shares
        2. since we also have the short position, that is shares have been sold before need to be bought again to make a profit, what do we do?
        3. extra shares bought with the same value 
        
        """
        if row['Signal'] == 1 and (position is None or position['position_type'] == 'short'):  # Buy signal and no current position or covering a short position
            if position and position['position_type'] == 'short':  # Cover short position
                position['sell_date'] = row.timestamp
                position['sell_value'] = row['close']
                position['profit_loss'] = (position['buy_value'] - position['sell_value']) * position['num_shares']

                # Calculate borrow cost
                days_held = (row.timestamp - position['buy_date']).days
                borrow_cost = position['borrowed_value'] * borrow_rate * (days_held / 365)

                cash_balance -= (position['num_shares'] * position['sell_value']) + borrow_cost  # Adjust cash balance for covering
                position['cash_balance'] = cash_balance - borrow_cost  # Subtracting the borrow cost
                position['borrow_cost'] = borrow_cost
                trades.append(position)
                position = None  # Clear the position

            # Open new long position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': cash_balance / row['close'],  # Example: Buying shares worth of available cash balance
                'position_type': 'long',
                'cash_balance': cash_balance
            }
            cash_balance -= position['num_shares'] * row['close']  # Adjust cash balance for purchase

        elif row['Signal'] == -1 and (position is None or position['position_type'] == 'long'):  # Sell signal and no current position or opening a short position
            if position and position['position_type'] == 'long':  # Close long position
                position['sell_date'] = row.timestamp
                position['sell_value'] = row['close']
                position['profit_loss'] = (position['sell_value'] - position['buy_value']) * position['num_shares']

                cash_balance += position['num_shares'] * position['sell_value']  # Adjust cash balance for sale
                position['cash_balance'] = cash_balance
                trades.append(position)
                position = None  # Clear the position

            # Open new short position
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': cash_balance / row['close'],  # Example: Selling short shares worth of available cash balance
                'position_type': 'short',
                'cash_balance': cash_balance,
                'borrowed_value': row['close'] * (cash_balance / row['close'])  # Value of borrowed shares
            }
            cash_balance += position['num_shares'] * row['close']

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
  

def trading_simulation(stock_data, initial_cash, strategy_name, strategy_parameters, interval, stock_name, start_date, end_date, borrow_rate=0.01):
    
    trades = []
    position = None
    file_name = f'{stock_name}_{interval}_{strategy_name}_{strategy_parameters}_{start_date}_{end_date}.csv'

    cash_balance = initial_cash

    for i, row in stock_data.iterrows():
        if row['Signal'] == 1 and position is None: 
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],
                'position_type': 'long',
                'cash_balance': cash_balance
            }
            cash_balance -= position['num_shares'] * row['close']  

        elif row['Signal'] == -1 and position is None:  
            position = {
                'buy_date': row.timestamp,
                'buy_value': row['close'],
                'num_shares': initial_cash / row['close'],  
                'position_type': 'short',
                'cash_balance': cash_balance,
                'borrowed_value': row['close'] * (initial_cash / row['close'])
            }
            cash_balance += position['num_shares'] * row['close']

        elif row['Signal'] == -1 and position is not None and position['position_type'] == 'long':  
            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['sell_value'] - position['buy_value']) * position['num_shares']

            cash_balance += position['num_shares'] * position['sell_value']  # Adjust cash balance for sale
            position['cash_balance'] = cash_balance

            trades.append(position)
            position = None  

        elif row['Signal'] == 1 and position is not None and position['position_type'] == 'short':  

            position['sell_date'] = row.timestamp
            position['sell_value'] = row['close']
            position['profit_loss'] = (position['buy_value'] - position['sell_value']) * position['num_shares']

            days_held = (row.timestamp - position['buy_date']).days
            borrow_cost = position['borrowed_value'] * borrow_rate * (days_held / 365)

            cash_balance -= (position['num_shares'] * position['sell_value']) + borrow_cost  
            position['cash_balance'] = cash_balance - borrow_cost  
            position['borrow_cost'] = borrow_cost
            trades.append(position)
            position = None  
 
    trades_df = pd.DataFrame(trades)

##TODOL: when to do short. when no pre-buy signals exist. when pre-buy signals exist we do long
##TODO: can we do a short when we've already sold at a point
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
 
  initial_cash = 10000 
  strategy_parameters = f'{small}MA_{large}MA'

  signals = crossover_signal(stock_data, small, large)
  stock_data['Signal'] = signals['Signal']
  trading_simulation_shorting_logic(stock_data, initial_cash, 'MA CrossOver', strategy_parameters, interval, stock, start_date, end_date)

  plot(stock_data, small, large)


if __name__ == "__main__":
    main()


