# CLI Portfolio Tracker
A command-line portfolio tracking application built as part of a job application at a.s.r. Vermogensbeheer. Track investments across global exchanges, analyse portfolio composition, and simulate long-term performance using Monte Carlo methods.

---

## Features

- Add and manage orders across global stock exchanges
- View current portfolio with live prices, EUR-converted values, and gain/loss
- Automatic multi-currency support with live FX conversion to EUR
- Portfolio weights broken down by asset, sector, and asset class
- Price history charts for one or multiple tickers
- Asset return correlation heatmap
- Monte Carlo simulation (100,000 paths, 15-year outlook) using Geometric Brownian Motion
- Full order history with per-transaction detail

---

## Architecture

The application follows the **Model-View-Controller (MVC)** pattern:

- **Model** — stores and computes on portfolio data (`models/`)
- **View** — renders tables and charts, never fetches or computes (`views/`)
- **Controller** — receives CLI commands and routes between model and view (`controllers/`)
- **Infrastructure** — handles database persistence and market data fetching (`utils/`)

```
cli-portfolio-tracker/
├── main.py
├── schema.sql
├── requirements.txt
├── portfolio_tracker/
│   ├── models/
│   │   ├── asset.py          # Asset dataclass with position aggregation
│   │   ├── portfolio.py      # Portfolio-level calculations and weights
│   │   └── simulation.py     # Monte Carlo GBM simulation
│   ├── views/
│   │   ├── table_view.py     # Rich terminal tables
│   │   └── chart_view.py     # Matplotlib charts
│   ├── controllers/
│   │   └── portfolio_controller.py
│   └── utils/
│       ├── storage.py        # SQLite persistence layer
│       └── market_data.py    # yfinance wrapper
```

---

## Installation

### Prerequisites

**Linux** — install the tkinter system package before proceeding:
```bash
sudo apt install python3-tk
```

**Windows / macOS** — no additional system packages required.

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

Tickers follow Yahoo Finance conventions — append the exchange suffix for non-US stocks (`.AS` for Amsterdam, `.L` for London, `.DE` for Frankfurt, `.PA` for Paris).

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

---

## Methodology

### Multi-currency support
All portfolio values are converted to EUR at display time using live FX rates fetched from Yahoo Finance. Purchase prices are stored in the local currency of the exchange. Gain/loss calculations reflect both price movement and FX rate changes since purchase, giving a true EUR return from a European investor's perspective.

### Monte Carlo simulation
Simulations use Geometric Brownian Motion (GBM):

$$S(t) = S(0) \cdot \exp\left(\left(\mu - \frac{1}{2}\sigma^2\right)dt + \sigma\sqrt{dt}\,Z\right)$$

Where `mu` and `sigma` are estimated from 5 years of actual historical portfolio returns, weighted by current portfolio allocation. This makes the simulation specific to the composition of your portfolio. A high-volatility portfolio will produce a wider fan than a low-volatility one.

The simulation assumes **252 trading days per year**, the standard convention in quantitative finance (actual days vary between 250 and 252 depending on the year).

### Weighted average purchase price
Multiple orders in the same stock are aggregated into a single position using a quantity-weighted average purchase price:

$$\bar{P} = \frac{\sum_{i} Q_i \cdot P_i}{\sum_{i} Q_i}$$

This reflects the true average cost basis of the position regardless of order timing.

---

## Dependencies

Key packages:
- `yfinance` — market data and FX rates
- `rich` — terminal table formatting
- `matplotlib` — charts and visualisations
- `numpy` — numerical computation for simulation
- `pandas` — time series data handling

Full list in `requirements.txt`.
