import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from scipy.stats import t, norm
from scipy.stats import multivariate_normal
from sklearn.cluster import KMeans

def calculate_var(returns, confidence_level=0.95):
    # Historical VaR
    return np.percentile(returns, (1 - confidence_level) * 100)

def monte_carlo_simulation(returns, num_simulations: int = 1000, lookahead_days: int = 100, initial_value: float = 100):
    """Run Monte Carlo simulation to predict future prices."""
    # Convert daily returns to log returns (use log(1+return))
    log_returns = pd.Series(np.log(1 + returns))

    # Initialize matrix to store simulated prices
    simulated_prices = np.zeros((lookahead_days, num_simulations))

    # Set the initial price (for simplicity, assume starting at 1)
    simulated_prices[0, :] = initial_value

    # Calculate the drift (mean of log returns) and the standard deviation
    drift = log_returns.mean()
    stdev = log_returns.std()

    # Run the simulation for each day
    for i in range(1, lookahead_days):
        # Random normal shocks (Z)
        Z = np.random.normal(0, 1, num_simulations)
        # Simulate future prices using Geometric Brownian motion formula
        simulated_prices[i, :] = simulated_prices[i-1, :] * np.exp(drift + stdev * Z)

    # Calculate mean and standard deviation for each day (across simulations)
    mean_simulated_prices = np.mean(simulated_prices, axis=1)  # Mean across simulations for each day
    sd_simulated_prices = np.std(simulated_prices, axis=1)    # SD across simulations for each day

    # Calculate the upper and lower bounds (1 SD range) for each day
    upper_sd_simulated_prices = mean_simulated_prices + sd_simulated_prices
    lower_sd_simulated_prices = mean_simulated_prices - sd_simulated_prices

    # Create a DataFrame with the results
    date_index = pd.date_range(start=pd.Timestamp.today(), periods=lookahead_days, freq='B')
    mean_upper_lower_simulated_df = pd.DataFrame({
        "Mean": mean_simulated_prices,
        "UpperSD": upper_sd_simulated_prices,
        "LowerSD": lower_sd_simulated_prices
    }, index=date_index)

    # Format the index to display dates in 'YYYY-MM-DD' format
    mean_upper_lower_simulated_df.index = mean_upper_lower_simulated_df.index.strftime('%Y-%m-%d')

    return mean_upper_lower_simulated_df


def correlation_matrix(data):
    if isinstance(data, pd.DataFrame) and not data.empty:
        matrix = data.corr()

        # Rename index and columns to avoid conflicts
        matrix.index.name = "Asset 1"
        matrix.columns.name = "Asset 2"

        # Convert matrix to long format
        corr_pairs = matrix.stack().reset_index()

        # Rename columns for clarity
        corr_pairs.columns = ['Asset 1', 'Asset 2', 'Correlation']

        # Remove self-correlations (where Asset 1 == Asset 2)
        corr_pairs = corr_pairs[corr_pairs['Asset 1'] != corr_pairs['Asset 2']]

        # Sort by absolute correlation to find the most and least correlated pairs
        most_correlated = corr_pairs.sort_values(by='Correlation', ascending=False).head(5)
        least_correlated = corr_pairs.sort_values(by='Correlation', ascending=True).head(5)

        return matrix, most_correlated, least_correlated

    else:
        return None, None, None  # Handle case where input data is invalid

def monte_carlo_stress_test(returns, weights, num_simulations: int = 1000, lookahead_days: int = 100, initial_value: float = 100):
    log_returns = np.log(1 + returns)

    t_params = {ticker: t.fit(log_returns[ticker]) for ticker in log_returns.columns}

    simulated_returns = np.array([t.rvs(*t_params[ticker], size=(lookahead_days, num_simulations))
                                  for ticker in log_returns.columns]).T  # Shape: (lookahead_days, num_simulations, num_assets)
    
    corr_matrix = log_returns.corr()
    stress_corr = corr_matrix + (1 - corr_matrix) * 0.7  # Increase correlations by 70%

    vols = log_returns.std() * 1.5  # Increase vol by 50%
    stress_cov = np.outer(vols, vols) * stress_corr
    stressed_returns = multivariate_normal(mean=np.zeros(len(log_returns.columns)),
                                           cov=stress_cov).rvs(size=(lookahead_days, num_simulations))

    num_assets = len(log_returns.columns)
    simulated_prices = np.zeros((lookahead_days, num_simulations, num_assets))
    simulated_prices[0, :, :] = initial_value  # Set initial prices for all assets across simulations

    for i in range(1, lookahead_days):
        simulated_prices[i, :, :] = simulated_prices[i-1, :, :] * np.exp(stressed_returns[i])  # Apply stressed returns for each asset

    portfolio_values = np.sum(simulated_prices * weights, axis=2)  # Shape: (lookahead_days, num_simulations)

    mean_portfolio_values = np.mean(portfolio_values, axis=1)
    sd_portfolio_values = np.std(portfolio_values, axis=1)

    upper_sd_portfolio_values = mean_portfolio_values + sd_portfolio_values
    lower_sd_portfolio_values = mean_portfolio_values - sd_portfolio_values

    date_index = pd.date_range(start=pd.Timestamp.today(), periods=lookahead_days, freq='B')
    portfolio_df = pd.DataFrame({"Mean": mean_portfolio_values,
                                 "UpperSD": upper_sd_portfolio_values,
                                 "LowerSD": lower_sd_portfolio_values},
                                index=date_index)

    portfolio_df.index = portfolio_df.index.strftime('%Y-%m-%d')

    return portfolio_df