import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta

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

    # Calculate mean and standard deviation for each day
    mean_simulated_prices = np.mean(simulated_prices, axis=1)  # Convert to list for JSON compatibility
    date_index = pd.date_range(start=pd.Timestamp.today(), periods=lookahead_days, freq='B')

    sd_simulated_prices = np.std(simulated_prices).item()  # Convert np.float64 to native Python float

    upper_sd_simulated_prices = mean_simulated_prices+sd_simulated_prices
    lower_sd_simulated_prices = mean_simulated_prices-sd_simulated_prices

    mean_upper_lower_simulated_df = pd.DataFrame({"Mean":mean_simulated_prices,"UpperSD":upper_sd_simulated_prices,"LowerSD":lower_sd_simulated_prices},index=date_index)

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