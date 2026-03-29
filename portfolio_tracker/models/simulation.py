import numpy as np
from portfolio_tracker.models.portfolio import Portfolio
from portfolio_tracker.utils.market_data import get_multiple_history


def run_simulation(portfolio: Portfolio, n_paths: int = 100_000, years: int = 15) -> np.ndarray:
    """
    Run a Monte Carlo simulation using Geometric Brownian Motion.
    Returns an array of shape (n_paths, trading_days) with simulated portfolio values.
    """
    tickers = [a.ticker for a in portfolio.assets]
    weights = np.array([a.current_value / portfolio.total_value for a in portfolio.assets])

    hist = get_multiple_history(tickers, period="5y")
    returns = hist.pct_change().dropna()

    # Portfolio daily return and volatility from historical data
    portfolio_returns = returns.dot(weights)
    mu = portfolio_returns.mean()
    sigma = portfolio_returns.std()

    trading_days = years * 252 #252 is convention for number of trading days in a year
    dt = 1 / 252
    initial_value = portfolio.total_value

    # GBM: S(t) = S(0) * exp((mu - 0.5 * sigma^2) * dt + sigma * sqrt(dt) * Z)
    Z = np.random.standard_normal((n_paths, trading_days))
    daily_returns = np.exp((mu - 0.5 * sigma ** 2) * dt + sigma * np.sqrt(dt) * Z)

    paths = np.empty((n_paths, trading_days + 1))
    paths[:, 0] = initial_value
    paths[:, 1:] = initial_value * np.cumprod(daily_returns, axis=1)

    return paths


def get_percentiles(paths: np.ndarray) -> dict[str, np.ndarray]:
    """Extract percentile bands from simulation paths for fan chart plotting."""
    return {
        "p5":    np.percentile(paths, 5,  axis=0),
        "p25":   np.percentile(paths, 25, axis=0),
        "p50":   np.percentile(paths, 50, axis=0),
        "p75":   np.percentile(paths, 75, axis=0),
        "p95":   np.percentile(paths, 95, axis=0),
    }