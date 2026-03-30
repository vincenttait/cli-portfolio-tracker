import matplotlib
try:
    matplotlib.use("TkAgg")
except Exception:
    pass
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


def plot_price_history(history: dict[str, pd.DataFrame], period: str = "1y"):
    """Plot historical price history for one or multiple tickers."""
    fig, ax = plt.subplots(figsize=(12, 6))

    for ticker, df in history.items():
        ax.plot(df.index, df["Close"], label=ticker, linewidth=1.5)

    ax.set_title(f"Price history ({period})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (€)")
    ax.legend()
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_simulation_fan(percentiles: dict[str, np.ndarray], initial_value: float, years: int = 15):
    """Plot Monte Carlo simulation results as a fan chart with percentile bands."""
    trading_days = years * 252
    x = np.linspace(0, years, trading_days + 1)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.fill_between(x, percentiles["p5"],  percentiles["p95"], alpha=0.15, color="steelblue", label="5th–95th percentile")
    ax.fill_between(x, percentiles["p25"], percentiles["p75"], alpha=0.25, color="steelblue", label="25th–75th percentile")
    ax.plot(x, percentiles["p50"], color="steelblue", linewidth=2, label="Median (p50)")
    ax.axhline(y=initial_value, color="gray", linestyle="--", linewidth=1, label="Initial value")

    ax.set_title(f"Monte Carlo simulation — {years} year outlook (100,000 paths)")
    ax.set_xlabel("Years")
    ax.set_ylabel("Portfolio value (€)")
    ax.legend()
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"€{x:,.0f}"))
    plt.tight_layout()
    plt.show()


def plot_weights_pie(weights: list[dict], title: str = "Portfolio weights"):
    """Plot portfolio weights as a pie chart."""
    labels = [w["ticker"] for w in weights]
    sizes  = [w["weight"] for w in weights]

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def plot_breakdown_pie(breakdown: dict[str, float], title: str):
    """Plot sector or asset class breakdown as a pie chart."""
    labels = list(breakdown.keys())
    sizes  = list(breakdown.values())

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def plot_correlation(returns: pd.DataFrame):
    """Plot a correlation heatmap of asset returns."""
    corr = returns.corr()
    tickers = list(corr.columns)
    n = len(tickers)

    fig, ax = plt.subplots(figsize=(max(6, n), max(5, n - 1)))
    im = ax.imshow(corr.values, cmap="RdYlGn", vmin=-1, vmax=1)

    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(tickers)
    ax.set_yticklabels(tickers)

    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=9)

    plt.colorbar(im, ax=ax)
    ax.set_title("Asset return correlation matrix")
    plt.tight_layout()
    plt.show()


def plot_benchmark_comparison(metrics: dict):
    """Plot cumulative portfolio returns against a benchmark index."""
    portfolio_returns = metrics["aligned_portfolio"]
    benchmark_returns = metrics["aligned_benchmark"]

    portfolio_cumulative = (1 + portfolio_returns).cumprod()
    benchmark_cumulative = (1 + benchmark_returns).cumprod()

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(portfolio_cumulative.index, portfolio_cumulative.values, label="Portfolio",                    linewidth=2, color="steelblue")
    ax.plot(benchmark_cumulative.index, benchmark_cumulative.values, label=metrics["benchmark"].upper(),   linewidth=2, color="gray", linestyle="--")
    ax.axhline(y=1.0, color="black", linestyle=":", linewidth=0.8)

    ax.set_title(f"Portfolio vs {metrics['benchmark'].upper()} ({metrics['period']})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative return (1 = starting value)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.show()


def plot_efficient_frontier(frontier: dict):
    """
    Plot the efficient frontier — the cloud of random portfolios coloured
    by Sharpe ratio, with the optimal portfolios highlighted.
    """
    fig, ax = plt.subplots(figsize=(12, 8))

    # Scatter plot of all random portfolios, coloured by Sharpe ratio
    sc = ax.scatter(
        frontier["volatilities"],
        frontier["returns"],
        c=frontier["sharpe_ratios"],
        cmap="RdYlGn",
        alpha=0.4,
        s=8,
    )
    plt.colorbar(sc, ax=ax, label="Sharpe ratio")

    # Maximum Sharpe ratio portfolio
    ax.scatter(
        frontier["max_sharpe_vol"],
        frontier["max_sharpe_return"],
        marker="*", color="blue", s=300, zorder=5,
        label=f"Max Sharpe  {_weights_label(frontier['tickers'], frontier['max_sharpe_weights'])}"
    )

    # Minimum variance portfolio
    ax.scatter(
        frontier["min_var_vol"],
        frontier["min_var_return"],
        marker="*", color="red", s=300, zorder=5,
        label=f"Min variance  {_weights_label(frontier['tickers'], frontier['min_var_weights'])}"
    )

    ax.set_title(f"Efficient frontier ({frontier['period']} history, 10,000 portfolios)")
    ax.set_xlabel("Annualised volatility (%)")
    ax.set_ylabel("Annualised return (%)")
    ax.legend(loc="upper left", fontsize=9)
    plt.tight_layout()
    plt.show()


def _weights_label(tickers: list[str], weights: list[float]) -> str:
    """Format weights as a compact label for the legend."""
    return "  |  ".join(f"{t}: {w*100:.1f}%" for t, w in zip(tickers, weights))