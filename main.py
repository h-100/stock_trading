import argparse

from backtesting import Backtest

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

def print_stats(stats):
  """
  print stats in a printable format
  """
  pass

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

  ### get data 
  data = dh.DataHandler(args.ticker, args.start_date, args.end_date).load_data()

  stats = get_stats(args.strategy_name, data, args.cash)
  print(stats)
  



if __name__ == "__main__":
  main()

## Priority TODOS
#### 1. TODO1: transform stats to columns and print in the form of a table 
#### 2. TODO2: do the same for multiple number of stocks 
#### 3. TODO3: add other strategies 
#### 4. TODO4: add plots 


###########################################

## TODO: add argeparse to integrate elements 
## TODO: display stats for a single strategy that runs once and displays the graph
## TODO: display profit states for same data source but on different data ranges; comparison table
## TODO: display profit stats for multiple data sources and same date ranges; comparison table