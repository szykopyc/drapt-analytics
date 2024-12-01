import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, ticker, lookback_days):
        self.ticker = ticker
        self.lookback_days = lookback_days

    def get_data(self):
        data_start_date = datetime.now() - timedelta(days=self.lookback_days)
        asset_data = pd.DataFrame()
        try:
            # Download the data for the ticker
            data = yf.download(self.ticker, data_start_date)['Close']

            if data.empty:
                print(f"Error downloading data for: {self.ticker}")

            # Calculate cumulative percentage change
            asset_data[self.ticker] = data.pct_change()
        except Exception as e:
            print(f"Error downloading data for {self.ticker}: {e}")
            asset_data[self.ticker] = pd.Series()  # Assign empty Series if download fails

        return asset_data