import numpy as np
import pandas as pd
from portfolio_tracker.utils.market_data import get_multiple_history

TRADING_DAYS_PER_YEAR = 252  # Industry convention in quantitative finance; actual days vary 250-252 per year
RISK_FREE_RATE = 0.03        # Approximate European risk-free rate (ECB, annualised)


def get_portfolio_returns(tickers: list[str], weights: list[float], period: str = "2y") -> pd.Series:
    """Fetch historical data and compute weighted daily portfolio returns."""
    hist = get_multiple_history(tickers, period=period)
    returns = hist.pct_change().dropna()
    weights_arr = np.array(weights)
    return returns.dot(weights_arr)


def sharpe_ratio(portfolio_returns: pd.Series) -> float:
    """
    Sharpe ratio: risk-adjusted return relative to a risk-free rate.
    Higher is better. Above 1.0 is generally considered good.
    """
    daily_rf = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
    excess_returns = portfolio_returns - daily_rf
    return (excess_returns.mean() / excess_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)


def sortino_ratio(portfolio_returns: pd.Series) -> float:
    """
    Sortino ratio: like Sharpe but only penalises downside volatility.
    More relevant for asymmetric return distributions.
    """
    daily_rf = RISK_FREE_RATE / TRADING_DAYS_PER_YEAR
    excess_returns = portfolio_returns - daily_rf
    downside_returns = excess_returns[excess_returns < 0]
    downside_std = np.sqrt((downside_returns ** 2).mean()) * np.sqrt(TRADING_DAYS_PER_YEAR)
    annualised_excess = excess_returns.mean() * TRADING_DAYS_PER_YEAR
    return annualised_excess / downside_std


def max_drawdown(portfolio_returns: pd.Series) -> float:
    """
    Maximum drawdown: largest peak-to-trough decline in the portfolio.
    Expressed as a negative percentage.
    """
    cumulative = (1 + portfolio_returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return drawdown.min() * 100


def value_at_risk(portfolio_returns: pd.Series, confidence: float = 0.95) -> float:
    """
    VaR: maximum expected daily loss at a given confidence level.
    At 95% confidence: on 95% of days, losses will not exceed this value.
    Expressed as a negative percentage.
    """
    return np.percentile(portfolio_returns, (1 - confidence) * 100) * 100


def conditional_value_at_risk(portfolio_returns: pd.Series, confidence: float = 0.95) -> float:
    """
    CVaR (Expected Shortfall): average loss on the worst days beyond the VaR threshold.
    A more conservative risk measure than VaR.
    Expressed as a negative percentage.
    """
    var = np.percentile(portfolio_returns, (1 - confidence) * 100)
    tail_losses = portfolio_returns[portfolio_returns <= var]
    return tail_losses.mean() * 100


def compute_all(tickers: list[str], weights: list[float], period: str = "2y") -> dict:
    """Compute all risk metrics and return as a single dict."""
    returns = get_portfolio_returns(tickers, weights, period)
    return {
        "sharpe_ratio":  sharpe_ratio(returns),
        "sortino_ratio": sortino_ratio(returns),
        "max_drawdown":  max_drawdown(returns),
        "var_95":        value_at_risk(returns, 0.95),
        "cvar_95":       conditional_value_at_risk(returns, 0.95),
        "period":        period,
    }