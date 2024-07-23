import requests
import yfinance as yf
from bs4 import BeautifulSoup


def get_nasdaq_100_tickers():
    
    url = 'https://en.wikipedia.org/wiki/NASDAQ-100'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', {'id': 'constituents'})
    
    tickers = []
    for row in table.findAll('tr')[1:]:
        ticker = row.findAll('td')[1].text.strip()
        tickers.append(ticker)
    
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
    
    import pdb

    nasdaq_100_tickers = get_nasdaq_100_tickers()

    tech_tickers = filter_tech_stocks(nasdaq_100_tickers)

    print(tech_tickers)
