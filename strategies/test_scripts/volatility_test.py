import os
import pdb
import pickle

import numpy as np
import pandas as pd
import pandas_ta as ta
import requests
import yfinance as yf
from bs4 import BeautifulSoup


def get_nasdaq_100_tech_stocks(path):

    if os.path.isfile(path):
        with open(path, "rb") as f:
            try:
                return pickle.load(f)
            except Exception: # so many things could go wrong, can't be more specific.
                pass 

    url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text.strip()
        tickers.append(ticker)


    tech_stocks = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        sector = stock.info.get('sector', '')
        if sector == 'Technology':
            tech_stocks.append(ticker)

    with open(path, "wb") as fp:   #Pickling
        pickle.dump(tickers, fp)

    return tech_stocks

def fetch_stock_data(ticker, period='1mo', interval='30m'):
    """
    Fetches historical stock data for a given ticker.
    """
    df = yf.download(ticker, period=period, interval=interval)
    return df

# def calculate_atr(df, window=14):

#     atr = df.ta.atr(high= df.High, low=df.Low, close=df.Close, window = window, fillna= False)

#     df['ATR'] = df.index.map(atr)

#     return df['ATR']

def calculate_average_volume(df, window=10):
    mean = df['Volume'].rolling(window).mean()

    return mean


def find_high_volume_volatile_stocks(tickers, volume_multiplier):
    """
    Finds stocks with high volume and high volatility.
    """
    high_volume_volatile_stocks = []

    for ticker in tickers:

        df = fetch_stock_data(ticker)
        # pdb.set_trace()
        df['Average_Volume'] = calculate_average_volume(df)

        average_of_last_elements = (df['Volume'].iloc[-10] + df['Volume'].iloc[-11] + df['Volume'].iloc[-11])//3
        # pdb.set_trace()
        # if average_of_last_elements * 3 
        # if average_of_last_elements > volume_multiplier * df['Average_Volume'].iloc[-1]:
        #     high_volume_volatile_stocks.append(ticker)

        # ratio_increase = df['Average_Volume'].iloc[-1] / average_of_last_elements

        # if ratio_increase >= volume_multiplier: 
        #     high_volume_volatile_stocks.append(ticker)

        if df['Volume'].iloc[-1] > volume_multiplier * df['Average_Volume'].iloc[-1]:
            high_volume_volatile_stocks.append(ticker)


    return high_volume_volatile_stocks

if __name__ == "__main__":

    volume_multiplier = 2
    file_name = 'tickers_' + 'randome2gge3'
    print("###############Getting tech stock tickers #################")
    stock_tickers = get_nasdaq_100_tech_stocks(file_name)
    print("###############Getting tech stock tickers: Done #################")
    # atr_threshold = 2.0

    print("########Finding High Volume Stocks###################")
    result = find_high_volume_volatile_stocks(stock_tickers, volume_multiplier)

    # Output the result
    print("High Volume Volatile Stocks:", result)
