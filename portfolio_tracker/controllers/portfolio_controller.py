from portfolio_tracker.models.portfolio import Portfolio
from portfolio_tracker.models.simulation import run_simulation, get_percentiles
from portfolio_tracker.utils.storage import save_asset, delete_asset, load_assets
from portfolio_tracker.utils.market_data import get_price_in_eur, get_company_name, get_currency, get_history, get_multiple_history
from portfolio_tracker.views import table_view, chart_view
from datetime import date


def add_asset(ticker: str, sector: str, asset_class: str, quantity: float, purchase_price: float, purchase_date: str = None):
    """Fetch company name and currency from yfinance and save a new order to the database."""
    try:
        _, currency, _ = get_price_in_eur(ticker)
    except Exception:
        table_view.render_error(f"Ticker '{ticker}' not found on Yahoo Finance.")
        return

    name = get_company_name(ticker)
    asset = {
        "ticker":         ticker.upper(),
        "name":           name,
        "sector":         sector,
        "asset_class":    asset_class,
        "quantity":       quantity,
        "purchase_price": purchase_price,
        "purchase_date":  purchase_date or str(date.today()),
        "currency":       currency,
    }
    save_asset(asset)
    table_view.render_message(f"[green]Added {quantity} x {ticker.upper()} at {currency} {purchase_price:.2f}[/green]")


def show_portfolio():
    """Load portfolio, fetch current prices and render the full portfolio table."""
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty. Add assets with the 'add' command.")
        return
    table_view.render_portfolio(
        summary=portfolio.get_summary(),
        total_value=portfolio.total_value,
        total_invested=portfolio.total_invested,
        total_gain_loss=portfolio.total_gain_loss,
        total_gain_loss_pct=portfolio.total_gain_loss_pct,
    )


def show_weights():
    """Render asset, sector and asset class weights."""
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    table_view.render_weights(portfolio.get_weights())
    table_view.render_breakdown(portfolio.get_sector_breakdown(), "Sector")
    table_view.render_breakdown(portfolio.get_asset_class_breakdown(), "Asset class")


def show_orders():
    """Render the raw order history from the database."""
    orders = load_assets()
    if not orders:
        table_view.render_message("No orders found.")
        return
    table_view.render_orders(orders)


def remove_asset(asset_id: int):
    """Delete a single order by ID."""
    delete_asset(asset_id)
    table_view.render_message(f"[green]Order {asset_id} removed.[/green]")


def show_history(tickers: list[str], period: str = "1y"):
    """Fetch and plot price history for one or more tickers."""
    history = {ticker: get_history(ticker, period) for ticker in tickers}
    chart_view.plot_price_history(history, period)


def show_charts():
    """Plot pie charts for portfolio weights, sector and asset class breakdown."""
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    chart_view.plot_weights_pie(portfolio.get_weights(), "Portfolio weights")
    chart_view.plot_breakdown_pie(portfolio.get_sector_breakdown(), "Sector breakdown")
    chart_view.plot_breakdown_pie(portfolio.get_asset_class_breakdown(), "Asset class breakdown")


def show_correlation(period: str = "1y"):
    """Fetch historical returns and plot the correlation heatmap."""
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    tickers = [a.ticker for a in portfolio.assets]
    hist = get_multiple_history(tickers, period)
    returns = hist.pct_change().dropna()
    chart_view.plot_correlation(returns)


def simulate():
    """Run Monte Carlo simulation and plot the fan chart."""
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    table_view.render_message("Running 100,000 simulations over 15 years...")
    paths = run_simulation(portfolio)
    percentiles = get_percentiles(paths)
    chart_view.plot_simulation_fan(percentiles, portfolio.total_value)


def show_risk(period: str = "2y"):
    """Compute and display portfolio risk metrics."""
    from portfolio_tracker.models import risk
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    tickers = [a.ticker for a in portfolio.assets]
    weights = [a.current_value_eur / portfolio.total_value for a in portfolio.assets]
    table_view.render_message(f"Computing risk metrics from {period} of historical data...")
    metrics = risk.compute_all(tickers, weights, period)
    table_view.render_risk(metrics)


def show_benchmark(benchmark: str = "sp500", period: str = "2y"):
    """Compare portfolio performance against a benchmark index."""
    from portfolio_tracker.models import risk
    portfolio = Portfolio()
    if not portfolio.assets:
        table_view.render_message("Your portfolio is empty.")
        return
    tickers = [a.ticker for a in portfolio.assets]
    weights = [a.current_value_eur / portfolio.total_value for a in portfolio.assets]
    table_view.render_message(f"Comparing portfolio against {benchmark.upper()} over {period}...")
    metrics = risk.benchmark_comparison(tickers, weights, benchmark, period)
    table_view.render_benchmark(metrics)
    chart_view.plot_benchmark_comparison(metrics)