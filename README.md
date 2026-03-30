# CLI Portfolio Tracker
A command-line portfolio tracking application built as part of a job application at a.s.r. Vermogensbeheer. Track investments across global exchanges, analyse portfolio composition, and simulate long-term performance using Monte Carlo methods.

---

## Assignment requirements

The following five requirements from the assignment brief are all implemented:

1. **Add assets** - add orders specifying ticker, sector, asset class, quantity, and purchase price
2. **Price history** - show current and historical prices with charts for single or multiple tickers
3. **View portfolio** - display name, sector, asset class, quantity, purchase price, transaction value, and current value per asset
4. **Weights** - total portfolio value and relative weights per asset, sector, and asset class
5. **Simulation** - 100,000 Monte Carlo paths over 15 years using Geometric Brownian Motion

---

## Extensions

Beyond the assignment requirements, the following features were added:

- **Multi-currency support** - live FX conversion to EUR via Yahoo Finance for portfolios spanning global exchanges
- **Risk metrics** - Sharpe ratio, Sortino ratio, maximum drawdown, VaR (95%), and CVaR (95%)
- **Benchmark comparison** - compare portfolio performance against major indices (S&P 500, AEX, FTSE, DAX, NASDAQ) with alpha and beta
- **Efficient frontier** - 10,000 random portfolio weightings optimised to find the maximum Sharpe ratio and minimum variance portfolios using `scipy`
- **PDF export** - automatically generated comprehensive report including all tables, charts, and analyses in a single document 

---

## Architecture

The application follows the **Model-View-Controller (MVC)** pattern:

- **Model** - stores and computes on portfolio data (`models/`)
- **View** - renders tables and charts, never fetches or computes (`views/`)
- **Controller** - receives CLI commands and routes between model and view (`controllers/`)
- **Infrastructure** - handles database persistence and market data fetching (`utils/`)

```
cli-portfolio-tracker/
├── main.py
├── schema.sql
├── requirements.txt
├── portfolio_tracker/
│   ├── models/
│   │   ├── asset.py           # Asset dataclass with position aggregation
│   │   ├── portfolio.py       # Portfolio-level calculations and weights
│   │   ├── simulation.py      # Monte Carlo GBM simulation
│   │   └── risk.py            # Risk metrics and efficient frontier
│   ├── views/
│   │   ├── table_view.py      # Rich terminal tables
│   │   └── chart_view.py      # Matplotlib charts
│   ├── controllers/
│   │   └── portfolio_controller.py
│   └── utils/
│       ├── storage.py         # SQLite persistence layer
│       ├── market_data.py     # yfinance wrapper
│       └── export.py          # PDF report generation
```

---

## Installation

### Prerequisites

**Linux** - install the tkinter system package before proceeding:
```bash
sudo apt install python3-tk
```

**Windows / macOS** - no additional system packages required.

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd cli-portfolio-tracker
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

The database is created automatically on first run.

---

## Usage

### Add an order
```bash
python main.py add <ticker> <sector> <asset_class> <quantity> <purchase_price> [--date YYYY-MM-DD]
```
```bash
# US exchange (USD)
python main.py add AAPL Technology Equity 10 250.00

# Euronext Amsterdam (EUR)
python main.py add ASML.AS Semiconductors Equity 2 1300.00

# London Stock Exchange (GBP)
python main.py add SHEL.L Energy Equity 10 3500.00

# With a specific purchase date
python main.py add MSFT Technology Equity 5 350.00 --date 2024-01-15
```

Tickers follow Yahoo Finance conventions. Append the exchange suffix for non-US stocks (`.AS` for Amsterdam, `.L` for London, `.DE` for Frankfurt, `.PA` for Paris).

### Show portfolio
```bash
python main.py show
```
Displays all positions with live prices, EUR-converted values, weighted average purchase price, and gain/loss per position and in total.

### Show weights
```bash
python main.py weights
```
Shows portfolio allocation broken down by asset, sector, and asset class.

### Show order history
```bash
python main.py orders
```
Lists every individual order stored in the database with its ID, useful for the `delete` command.

### Delete an order
```bash
python main.py delete <id>
```
Removes a single order by its ID. The portfolio recalculates automatically.

### Price history chart
```bash
# Single ticker
python main.py history AAPL

# Multiple tickers on one chart
python main.py history AAPL MSFT ASML.AS

# Custom period (1mo, 3mo, 6mo, 1y, 2y, 5y, max)
python main.py history AAPL --period 5y
```

### Portfolio charts
```bash
python main.py charts
```
Displays pie charts for portfolio weights, sector breakdown, and asset class breakdown.

### Correlation heatmap
```bash
python main.py correlate
python main.py correlate --period 2y
```
Shows a heatmap of return correlations between all assets in the portfolio.

### Monte Carlo simulation
```bash
python main.py simulate
```
Runs 100,000 simulated portfolio paths over 15 years using Geometric Brownian Motion, calibrated to the portfolio's historical returns and volatility. Displays a fan chart showing the 5th, 25th, 50th, 75th, and 95th percentile outcomes.

### Risk metrics
```bash
python main.py risk
python main.py risk --period 5y
```
Displays Sharpe ratio, Sortino ratio, maximum drawdown, VaR (95%), and CVaR (95%), calculated from historical portfolio returns.

### Benchmark comparison
```bash
python main.py benchmark
python main.py benchmark --benchmark aex
python main.py benchmark --benchmark aex --period 5y
```
Compares portfolio cumulative returns against a benchmark index. Available benchmarks: `sp500`, `aex`, `ftse`, `dax`, `nasdaq`. Also accepts any raw Yahoo Finance ticker. Displays alpha, beta, and a cumulative return chart.

### Efficient frontier
```bash
python main.py frontier
python main.py frontier --period 5y
```
Generates 10,000 random portfolio weightings and plots the risk/return tradeoff. Highlights the maximum Sharpe ratio and minimum variance portfolios found by `scipy` optimisation.

### Export PDF report
```bash
python main.py export
python main.py export --filename my_report.pdf
```
Generates a comprehensive PDF report including the holdings table, allocation charts, correlation heatmap, benchmark comparison, Monte Carlo simulation fan chart, and efficient frontier. Defaults to `portfolio_report_YYYY-MM-DD.pdf`.

---

## Methodology

### Multi-currency support
All portfolio values are converted to EUR at display time using live FX rates fetched from Yahoo Finance. Purchase prices are stored in the local currency of the exchange. Gain/loss calculations reflect both price movement and FX rate changes since purchase, giving a true EUR return from a European investor's perspective.

### Monte Carlo simulation
Simulations use Geometric Brownian Motion (GBM):

$$S(t) = S(0) \cdot \exp\left(\left(\mu - \frac{1}{2}\sigma^2\right)dt + \sigma\sqrt{dt}\,Z\right)$$

Where `mu` and `sigma` are estimated from 5 years of actual historical portfolio returns, weighted by current portfolio allocation. This makes the simulation specific to the composition of your portfolio, a high-volatility portfolio will produce a wider fan than a low-volatility one.

The simulation assumes **252 trading days per year**, the standard convention in quantitative finance (actual days vary between 250 and 252 depending on the year).

### Weighted average purchase price
Multiple orders in the same stock are aggregated into a single position using a quantity-weighted average purchase price:

$$\bar{P} = \frac{\sum_{i} Q_i \cdot P_i}{\sum_{i} Q_i}$$

This reflects the true average cost basis of the position regardless of order timing.

### Risk metrics
All risk metrics are computed from daily historical portfolio returns, weighted by current portfolio allocation:

- **Sharpe ratio** - annualised excess return over the risk-free rate divided by portfolio volatility
- **Sortino ratio** - like Sharpe, but penalises downside volatility only
- **Maximum drawdown** - largest peak-to-trough decline over the period
- **VaR (95%)** - maximum expected daily loss on 95% of trading days
- **CVaR (95%)** - average loss on the worst 5% of trading days

A European risk-free rate of 3% (annualised) is assumed.

### Efficient frontier
10,000 random weight combinations are generated and evaluated for annualised return and volatility. Two optimal portfolios are then found using `scipy.optimize.minimize` with SLSQP:

- **Maximum Sharpe ratio** - best risk-adjusted return
- **Minimum variance** - lowest possible portfolio volatility

---

## Dependencies

Key packages:
- `yfinance` - market data and FX rates
- `rich` - terminal table formatting
- `matplotlib` - charts and visualisations
- `numpy` - numerical computation for simulation
- `pandas` - time series data handling
- `scipy` - portfolio optimisation for the efficient frontier
- `reportlab` - PDF report generation

Full list in `requirements.txt`.
