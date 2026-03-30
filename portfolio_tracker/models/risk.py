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

def benchmark_comparison(
    tickers: list[str],
    weights: list[float],
    benchmark: str = "sp500",
    period: str = "2y"
) -> dict:
    """
    Compare portfolio performance against a benchmark index.
    Computes alpha, beta, and cumulative return for both.
    """
    from portfolio_tracker.utils.market_data import get_benchmark_history

    portfolio_returns = get_portfolio_returns(tickers, weights, period)
    bench_hist = get_benchmark_history(benchmark, period)
    bench_returns = bench_hist["Close"].pct_change().dropna()

    # Strip timezone info to avoid tz-naive vs tz-aware mismatch across exchanges
    portfolio_returns.index = portfolio_returns.index.tz_localize(None)
    bench_returns.index = bench_returns.index.tz_localize(None)

    # Align dates — only keep days both have data
    aligned = pd.concat([portfolio_returns, bench_returns], axis=1).dropna()
    aligned.columns = ["portfolio", "benchmark"]

    # Beta: how much the portfolio moves relative to the benchmark
    cov = np.cov(aligned["portfolio"], aligned["benchmark"])
    beta = cov[0, 1] / cov[1, 1]

    # Alpha: annualised excess return over what beta would predict
    portfolio_ann = aligned["portfolio"].mean() * TRADING_DAYS_PER_YEAR
    benchmark_ann  = aligned["benchmark"].mean() * TRADING_DAYS_PER_YEAR
    alpha = portfolio_ann - (RISK_FREE_RATE + beta * (benchmark_ann - RISK_FREE_RATE))

    # Cumulative returns over the period
    portfolio_cumulative = (1 + aligned["portfolio"]).cumprod().iloc[-1] - 1
    benchmark_cumulative = (1 + aligned["benchmark"]).cumprod().iloc[-1] - 1

    return {
        "alpha":             alpha * 100,
        "beta":              beta,
        "portfolio_return":  portfolio_cumulative * 100,
        "benchmark_return":  benchmark_cumulative * 100,
        "outperformance":    (portfolio_cumulative - benchmark_cumulative) * 100,
        "benchmark":         benchmark,
        "period":            period,
        "aligned_portfolio": aligned["portfolio"],
        "aligned_benchmark": aligned["benchmark"],
    }


from scipy.optimize import minimize

def efficient_frontier(tickers: list[str], period: str = "2y", n_portfolios: int = 10_000) -> dict:
    """
    Generate the efficient frontier by simulating random portfolio weightings
    and optimising for minimum variance and maximum Sharpe ratio.
    """
    hist = get_multiple_history(tickers, period=period)
    returns = hist.pct_change().dropna()
    returns.index = returns.index.tz_localize(None)

    mean_returns = returns.mean() * TRADING_DAYS_PER_YEAR
    cov_matrix   = returns.cov() * TRADING_DAYS_PER_YEAR
    n_assets     = len(tickers)

    # Simulate random portfolios
    results = np.zeros((3, n_portfolios))
    all_weights = np.zeros((n_portfolios, n_assets))

    for i in range(n_portfolios):
        w = np.random.random(n_assets)
        w /= w.sum()
        all_weights[i] = w

        port_return = np.dot(w, mean_returns)
        port_volatility = np.sqrt(w @ cov_matrix.values @ w)
        port_sharpe = (port_return - RISK_FREE_RATE) / port_volatility

        results[0, i] = port_volatility * 100
        results[1, i] = port_return * 100
        results[2, i] = port_sharpe

    # Optimise for maximum Sharpe ratio
    def neg_sharpe(w):
        ret = np.dot(w, mean_returns)
        vol = np.sqrt(w @ cov_matrix.values @ w)
        return -(ret - RISK_FREE_RATE) / vol

    def neg_sharpe(w):
        ret = np.dot(w, mean_returns)
        vol = np.sqrt(w @ cov_matrix.values @ w)
        return -(ret - RISK_FREE_RATE) / vol

    def portfolio_volatility(w):
        return np.sqrt(w @ cov_matrix.values @ w)

    constraints = {"type": "eq", "fun": lambda w: w.sum() - 1}
    bounds = tuple((0, 1) for _ in range(n_assets))
    w0 = np.ones(n_assets) / n_assets

    max_sharpe_result = minimize(neg_sharpe,        w0, method="SLSQP", bounds=bounds, constraints=constraints)
    min_var_result    = minimize(portfolio_volatility, w0, method="SLSQP", bounds=bounds, constraints=constraints)

    def portfolio_stats(w):
        ret = np.dot(w, mean_returns)
        vol = np.sqrt(w @ cov_matrix.values @ w)
        return ret * 100, vol * 100

    max_sharpe_return, max_sharpe_vol = portfolio_stats(max_sharpe_result.x)
    min_var_return,    min_var_vol    = portfolio_stats(min_var_result.x)

    return {
        "tickers":            tickers,
        "volatilities":       results[0],
        "returns":            results[1],
        "sharpe_ratios":      results[2],
        "all_weights":        all_weights,
        "max_sharpe_weights": max_sharpe_result.x,
        "min_var_weights":    min_var_result.x,
        "max_sharpe_return":  max_sharpe_return,
        "max_sharpe_vol":     max_sharpe_vol,
        "min_var_return":     min_var_return,
        "min_var_vol":        min_var_vol,
        "period":             period,
    }