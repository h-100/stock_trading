""" Example command to run for GOOG and AAPL stocks for specified start date, end date, strategy and 
with an initial cash investment of 10_000

python3 backtest_stocks.py -s '2020-1-1' -e '2024-4-30' -st rsiOscillator -c 10_000 -t GOOG,AAP
"""

import argparse

import pandas as pd
from backtesting import Backtest
from tabulate import tabulate

import DataHandler as dh
import strategies.RsiOscillator as rsiOsc
import strategies.SR_CandleSticks as srCandles
import strategies.SR_Rsi as srRSI


def get_stats(strategy_type, data, cash):

  stats = {}

  if strategy_type == 'rsiOscillator':
    bt = Backtest(data, rsiOsc.RsiOscillator, cash=cash)
    stats = bt.run()
  elif strategy_type == 'SR_rsi':
    bt = Backtest(data, srRSI.SupportResistanceRSI, cash=cash)
    stats = bt.run()
  elif strategy_type == 'SR_candles':
    bt = Backtest(data, srCandles.SR_Candles, cash=cash)
    stats = bt.run()
    
  return stats

def get_list_of_tickers(num):
  """
  num is optional
  """  
  pass

def convert_to_dataframe(stats):

  data = {}
  col_names = ['Stock Name', '_strategy', 'Start', 'End', 'Exposure Time [%]', 'Equity Final [$]', 'Equity Peak [$]', 'Return [%]', 'Volatility (Ann.) [%]']

  for i in col_names:
    data[i] = []

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

  convert_to_dataframe(stats)

def get_plot():
  pass


def main():
 
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-s', '--start-date', action="store", dest="start_date")
  parser.add_argument('-e', '--end-date', action="store", dest="end_date")
  parser.add_argument('-st', '--strategy', action="store", dest="strategy_name", help="strategy types = 1. rsiOscillator 2. SR_rsi 3. SR_candles")
  parser.add_argument('-c', '--cash', action="store", dest="cash", type=int)
  parser.add_argument('-t', '--tickers', action="store", dest="tickers")

  args = parser.parse_args()

  if args.tickers is not None:
    args.tickers = [s.strip() for s in args.tickers.split(",")]
  
  global_stats = []

  ### get data
  data_list = [] 
  for ticker in args.tickers:
    ## get data for each ticker
    if args.strategy_name == 'SR_rsi':
      indicator = 'rsi'
    else:
      indicator = None

    data = dh.DataHandler(ticker, args.start_date, args.end_date, indicator).load_data()

    ## get stats for each ticker
    stats = get_stats(args.strategy_name, data, args.cash)
  
    ## add the stock name
    stats['Stock Name'] = ticker
    global_stats.append(stats)


  ## process and print stats for each ticker
  for data in data_list:
    global_stats.append(get_stats(args.strategy_name, data, args.cash))

  print_stats(global_stats)
  

if __name__ == "__main__":
  main()
