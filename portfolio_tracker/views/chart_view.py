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