import pandas as pd
import risks.data_fetcher as data
import numpy as np
import risks.risk_metrics as risk_metrics

class Portfolio:
    def __init__(self, tickers_and_weights: list, lookback_days: int = 30, yearly_risk_free_rate: float = 0.04):
        self.tickers_and_weights = tickers_and_weights
        self.lookback_days = lookback_days
        self.yearly_risk_free_rate = yearly_risk_free_rate

        self.daily_risk_free_rate = self.yearly_risk_free_rate / 252

        self.portfolio_data = pd.DataFrame()
        self.portfolio_data_cumsum = None

        tickers = []

        for i in self.tickers_and_weights:
            tickers.append(i[0])

        print(tickers)

        dataFetcherInstance = data.DataFetcher(tickers, self.lookback_days)
        self.portfolio_data = dataFetcherInstance.get_data()

        self.portfolio_data["Portfolio"] = sum(
            self.portfolio_data[ticker] * weight for ticker, weight in zip(self.portfolio_data.columns, [weight for _, weight in self.tickers_and_weights])
        )

        self.portfolio_data.iloc[0] = 0
        self.portfolio_data = self.portfolio_data.dropna()
        self.portfolio_data_cumsum = self.portfolio_data.cumsum()

        self.portfolio_data_cumsum.index =  self.portfolio_data_cumsum.index.strftime('%Y-%m-%d')

    def compute_volatility(self):
        return self.portfolio_data['Portfolio'].std()

    def compute_variance(self):
        return self.portfolio_data['Portfolio'].var()

    def compute_sharpe(self):
        mean_daily_return = self.portfolio_data['Portfolio'].mean()
        daily_volatility = self.portfolio_data['Portfolio'].std()

        excess_return = mean_daily_return - self.daily_risk_free_rate

        sharpe_ratio = excess_return / daily_volatility
        annualized_sharpe_ratio = sharpe_ratio * np.sqrt(252)  # Annualize the Sharpe ratio

        return annualized_sharpe_ratio
    
    def simulate_monte_carlo(self, num_simulations: int=1000, lookahead_days:int = 100, initial_value:float = 100):
        return risk_metrics.monte_carlo_simulation(self.portfolio_data['Portfolio'], num_simulations=num_simulations,lookahead_days=lookahead_days,initial_value=initial_value)
    
    def calculate_var(self, confidence):
        return risk_metrics.calculate_var(self.portfolio_data['Portfolio'], confidence_level=confidence)
    
    def compute_correlation_matrix(self):
        return risk_metrics.correlation_matrix(self.portfolio_data.drop('Portfolio',axis=1))
