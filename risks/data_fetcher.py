from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, tickers, lookback_days):
        self.tickers = tickers
        self.lookback_days = lookback_days

    def fetch_single_ticker(self, ticker):
        data_start_date = datetime.now() - timedelta(days=self.lookback_days)
        try:
            # Download the data for the ticker
            data = yf.download(ticker, data_start_date)['Close']
            # Calculate cumulative percentage change
            return data.pct_change()
        except Exception as e:
            print(f"EXCEPTION | Error downloading data for {ticker}: {e}")
            return pd.Series(name=ticker)

    def get_data(self):
        results = [self.fetch_single_ticker(ticker) for ticker in self.tickers]
        return pd.concat(results, axis=1)