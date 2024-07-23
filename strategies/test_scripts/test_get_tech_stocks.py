import os
import pickle

import requests
import yfinance as yf
from bs4 import BeautifulSoup


def get_nasdaq_100_tickers():
    """
    Scrapes the NASDAQ-100 tickers from the official NASDAQ website.
    """
    # path = 'tickers'
    # if os.path.isfile(path):
    #     with open(path, "rb") as f:
    #         try:
    #             return pickle.load(f)
    #         except Exception: # so many things could go wrong, can't be more specific.
    #             pass 

    url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text.strip()
        tickers.append(ticker)

    with open("tickers", "wb") as fp:   #Pickling
        pickle.dump(tickers, fp)
    
    return tickers

def filter_tech_stocks(tickers):
    """
    Filters the list of tickers to include only tech stocks using yfinance.
    """
    tech_stocks = []
    for ticker in tickers:
        stock = yf.Ticker(ticker)
        sector = stock.info.get('sector', '')
        if sector == 'Technology':
            tech_stocks.append(ticker)
    
    return tech_stocks

if __name__ == "__main__":
    # Get NASDAQ-100 tickers
    nasdaq_100_tickers = get_nasdaq_100_tickers()

    # Filter for tech stocks
    tech_tickers = filter_tech_stocks(nasdaq_100_tickers)

    # Output the list of tech stock tickers
    print("Tech Stock Tickers in NASDAQ-100:", tech_tickers)
