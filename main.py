import argparse
import pdb

import pandas as pd
from backtesting import Backtest
from tabulate import tabulate

import DataHandler as dh
import strategies.RsiOscillator as rsiOsc


def get_data(ticker, start_date, end_date):
  """
  get ticker and start and end dates and output a dataframe 
  """
  pass

def get_stats(strategy_type, data, cash):
  if strategy_type == 'rsiOscillator':
    bt = Backtest(data, rsiOsc.RsiOscillator, cash=cash)
    stats = bt.run()
    return stats
  else:
    return {}

def get_list_of_tickers(num):
  """
  num is optional
  """
  
  pass
def convert_to_dataframe(stats):
  # df = pd.DataFrame()
  # df.columns = ['Start', 'End', 'Duration', 'Exposure Time', 'Equity Final [$]', 'Equity Peak [$]', 'Return [%]', 'Return (Ann.) [%]', 'Volatility (Ann.) [%]']

  data = {}
  col_names = ['Start', 'End', 'Duration', 'Exposure Time [%]', 'Equity Final [$]', 'Equity Peak [$]', 'Return [%]']

  for i in col_names:
    data[i] = []

  # pdb.set_trace()
  for i in range(len(stats)):
    for key in data.keys():
      data[key].append(stats[i][key])

  return pd.DataFrame(data)

def print_stats(stats):
  
  """
  print stats in a printable format
  """
  df = convert_to_dataframe(stats)
  print(df.to_markdown())

  # if not df.empty:
  #   print(df.to_markdown())
  convert_to_dataframe(stats)

def get_plot():
  pass


def main():
 
  parser = argparse.ArgumentParser()
  parser.add_argument('-s', '--start-date', action="store", dest="start_date")
  parser.add_argument('-e', '--end-date', action="store", dest="end_date")
  parser.add_argument('-st', '--strategy', action="store", dest="strategy_name")
  parser.add_argument('-c', '--cash', action="store", dest="cash", type=int)
  parser.add_argument('-t', '--ticker', action="store", dest="ticker")

  args = parser.parse_args()
  global_stats = []

  ### get data 
  data = dh.DataHandler(args.ticker, args.start_date, args.end_date).load_data()
  stats = get_stats(args.strategy_name, data, args.cash)
  global_stats.append(stats)
  print_stats(global_stats)
  



if __name__ == "__main__":
  main()

## Priority TODOS
####### add handlers for flags, are they required or are they not required
####### add help indicating how to run everything
#### 1. TODO1: transform stats to columns and print in the form of a table 
#### 2. TODO2: do the same for multiple number of stocks 
#### 3. TODO3: add other strategies 
#### 4. TODO4: add plots 


###########################################

## TODO: add argeparse to integrate elements 
## TODO: display stats for a single strategy that runs once and displays the graph
## TODO: display profit states for same data source but on different data ranges; comparison table
## TODO: display profit stats for multiple data sources and same date ranges; comparison table