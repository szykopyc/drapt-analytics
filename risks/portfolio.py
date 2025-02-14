import pandas as pd
import risks.data_fetcher as data
import numpy as np
import risks.risk_metrics as risk_metrics

class Portfolio:
    def __init__(self, tickers_and_weights: list, lookback_days: int = 30, yearly_risk_free_rate: float = 0.04):
        self.tickers_and_weights = tickers_and_weights
        self.lookback_days = lookback_days
        self.yearly_risk_free_rate = yearly_risk_free_rate
        
        benchmark_ticker= ["^GSPC"]
        benchmarkFetcher = data.DataFetcher(benchmark_ticker,self.lookback_days)
        benchmarkData = benchmarkFetcher.get_data()

        self.daily_risk_free_rate = (1 + self.yearly_risk_free_rate) ** (1/252) - 1

        self.portfolio_data = pd.DataFrame()
        self.portfolio_data_cumsum = None

        tickers = []

        for i in self.tickers_and_weights:
            tickers.append(i[0])

        dataFetcherInstance = data.DataFetcher(tickers, self.lookback_days)
        self.portfolio_data = dataFetcherInstance.get_data()

        self.portfolio_data["Portfolio"] = sum(
            self.portfolio_data[ticker] * weight for ticker, weight in zip(self.portfolio_data.columns, [weight for _, weight in self.tickers_and_weights])
        )

        self.portfolio_data.iloc[0] = 0
        self.portfolio_data = self.portfolio_data.dropna()
        self.portfolio_data_cumsum = self.portfolio_data.cumsum()

        self.portfolio_data_cumsum.index =  self.portfolio_data_cumsum.index.strftime('%Y-%m-%d')


        self.beta = self.portfolio_data['Portfolio'].var()/benchmarkData.var()
        self.beta = self.beta.iloc[0]

        R_p = self.portfolio_data['Portfolio'].mean() * 252  # Annualized portfolio return
        R_m = benchmarkData.dropna().mean() * 252  # Annualized market return

        self.jensens_alpha = R_p - (self.yearly_risk_free_rate + self.beta * (R_m - self.yearly_risk_free_rate))
        self.jensens_alpha=self.jensens_alpha.iloc[-1]
        self.skewness = self.portfolio_data['Portfolio'].skew()


    def compute_volatility(self):
        return self.portfolio_data['Portfolio'].std()

    def compute_variance(self):
        return self.portfolio_data['Portfolio'].var()

    def compute_sharpe(self):
        mean_daily_return = self.portfolio_data['Portfolio'].mean()  # Assume this is annual returns
        annual_return = (1 + mean_daily_return) ** 252 - 1
        daily_volatility = self.portfolio_data['Portfolio'].std(ddof=1)
        annual_volatility = daily_volatility * (252 ** 0.5)  # Annualize the daily volatility

        excess_return = annual_return - self.yearly_risk_free_rate  # No conversion needed

        print(f"Mean Annual Return: {annual_return}")
        print(f"Annual Risk-Free Rate: {self.yearly_risk_free_rate}")
        print(f"Annual Volatility: {annual_volatility}")

        sharpe_ratio = excess_return / annual_volatility  # No need to multiply by sqrt(252)

        return sharpe_ratio
        
    def simulate_monte_carlo(self, num_simulations: int=1000, lookahead_days:int = 100, initial_value:float = 100):
        return risk_metrics.monte_carlo_simulation(self.portfolio_data['Portfolio'], num_simulations=num_simulations,lookahead_days=lookahead_days,initial_value=initial_value)
    
    def calculate_var(self, confidence):
        return risk_metrics.calculate_var(self.portfolio_data['Portfolio'], confidence_level=confidence)
    
    def compute_correlation_matrix(self):
        return risk_metrics.correlation_matrix(self.portfolio_data.drop('Portfolio',axis=1))
