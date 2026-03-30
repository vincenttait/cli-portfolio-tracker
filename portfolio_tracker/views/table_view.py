import matplotlib
try:
    matplotlib.use("TkAgg")
except Exception:
    pass
from rich.console import Console
from rich.table import Table
from rich import box

console = Console()


def render_portfolio(summary: list[dict], total_value: float, total_invested: float, total_gain_loss: float, total_gain_loss_pct: float):
    """Render the full portfolio as a Rich table."""
    table = Table(box=box.ROUNDED, show_footer=True, footer_style="bold")

    table.add_column("Ticker",        style="bold")
    table.add_column("Name")
    table.add_column("Sector")
    table.add_column("Class")
    table.add_column("Currency")
    table.add_column("Qty",           justify="right")
    table.add_column("Avg Price",     justify="right")
    table.add_column("Curr Price",    justify="right")
    table.add_column("Value (EUR)",   justify="right")
    table.add_column("Invested (EUR)",justify="right")
    table.add_column("G/L (EUR)",     justify="right")
    table.add_column("G/L %",         justify="right")
    table.add_column("Weight",        justify="right")

    for a in summary:
        gl_color = "green" if a["gain_loss_eur"] >= 0 else "red"
        gl_sign  = "+" if a["gain_loss_eur"] >= 0 else ""

        table.add_row(
            a["ticker"],
            a["name"],
            a["sector"],
            a["asset_class"],
            a["currency"],
            f"{a['quantity']:.2f}",
            f"{a['currency']} {a['avg_purchase_price']:.2f}",
            f"{a['currency']} {a['current_price_local']:.2f}",
            f"€{a['current_value_eur']:.2f}",
            f"€{a['total_invested_eur']:.2f}",
            f"[{gl_color}]{gl_sign}€{a['gain_loss_eur']:.2f}[/{gl_color}]",
            f"[{gl_color}]{gl_sign}{a['gain_loss_pct']:.2f}%[/{gl_color}]",
            f"{a['weight']:.2f}%",
        )

    gl_color = "green" if total_gain_loss >= 0 else "red"
    gl_sign  = "+" if total_gain_loss >= 0 else ""
    console.print(f"\nTotal value (EUR):    €{total_value:.2f}")
    console.print(f"Total invested (EUR): €{total_invested:.2f}")
    console.print(f"Total G/L (EUR):      [{gl_color}]{gl_sign}€{total_gain_loss:.2f} ({gl_sign}{total_gain_loss_pct:.2f}%)[/{gl_color}]\n")
    console.print(table)


def render_weights(weights: list[dict]):
    """Render asset weights as a Rich table."""
    table = Table(box=box.ROUNDED)
    table.add_column("Ticker", style="bold")
    table.add_column("Weight", justify="right")

    for w in weights:
        table.add_row(w["ticker"], f"{w['weight']:.2f}%")

    console.print(table)


def render_breakdown(breakdown: dict[str, float], label: str):
    """Render sector or asset class breakdown as a Rich table."""
    table = Table(title=label, box=box.ROUNDED)
    table.add_column(label,    style="bold")
    table.add_column("Weight", justify="right")

    for name, weight in sorted(breakdown.items(), key=lambda x: x[1], reverse=True):
        table.add_row(name, f"{weight:.2f}%")

    console.print(table)


def render_orders(orders: list[dict]):
    """Render raw order history as a Rich table."""
    table = Table(title="Order history", box=box.ROUNDED)
    table.add_column("ID",             justify="right")
    table.add_column("Ticker",         style="bold")
    table.add_column("Name")
    table.add_column("Sector")
    table.add_column("Class")
    table.add_column("Currency")
    table.add_column("Qty",            justify="right")
    table.add_column("Purchase Price", justify="right")
    table.add_column("Date")

    for o in orders:
        table.add_row(
            str(o["id"]),
            o["ticker"],
            o["name"] or o["ticker"],
            o["sector"],
            o["asset_class"],
            o.get("currency", "USD"),
            f"{o['quantity']:.2f}",
            f"{o.get('currency', 'USD')} {o['purchase_price']:.2f}",
            o["purchase_date"],
        )

    console.print(table)


def render_message(message: str):
    """Render a simple informational message."""
    console.print(message)


def render_error(message: str):
    """Render an error message in red."""
    console.print(f"[red]Error: {message}[/red]")
    
    
def render_risk(metrics: dict):
    """Render risk metrics as a Rich table."""
    table = Table(title=f"Risk metrics ({metrics['period']} history)", box=box.ROUNDED)
    table.add_column("Metric",      style="bold")
    table.add_column("Value",       justify="right")
    table.add_column("Interpretation")

    def fmt_ratio(v):
        color = "green" if v >= 1.0 else "yellow" if v >= 0.5 else "red"
        return f"[{color}]{v:.4f}[/{color}]"

    def fmt_pct(v):
        color = "green" if v >= 0 else "red"
        return f"[{color}]{v:.2f}%[/{color}]"

    table.add_row("Sharpe ratio",  fmt_ratio(metrics["sharpe_ratio"]),  "> 1.0 good, > 2.0 excellent")
    table.add_row("Sortino ratio", fmt_ratio(metrics["sortino_ratio"]), "> 1.0 good, penalises downside only")
    table.add_row("Max drawdown",  fmt_pct(metrics["max_drawdown"]),    "Largest peak-to-trough decline")
    table.add_row("VaR (95%)",     fmt_pct(metrics["var_95"]),          "Max daily loss 95% of the time")
    table.add_row("CVaR (95%)",    fmt_pct(metrics["cvar_95"]),         "Avg loss on worst 5% of days")

    console.print(table)


def render_benchmark(metrics: dict):
    """Render benchmark comparison as a Rich table."""
    table = Table(
        title=f"Benchmark comparison vs {metrics['benchmark'].upper()} ({metrics['period']})",
        box=box.ROUNDED
    )
    table.add_column("Metric",      style="bold")
    table.add_column("Value",       justify="right")
    table.add_column("Interpretation")

    out_color = "green" if metrics["outperformance"] >= 0 else "red"
    out_sign  = "+" if metrics["outperformance"] >= 0 else ""

    def fmt_pct(v):
        color = "green" if v >= 0 else "red"
        sign  = "+" if v >= 0 else ""
        return f"[{color}]{sign}{v:.2f}%[/{color}]"

    table.add_row(
        "Portfolio return",
        fmt_pct(metrics["portfolio_return"]),
        f"Over {metrics['period']}"
    )
    table.add_row(
        "Benchmark return",
        fmt_pct(metrics["benchmark_return"]),
        f"{metrics['benchmark'].upper()} over {metrics['period']}"
    )
    table.add_row(
        "Outperformance",
        f"[{out_color}]{out_sign}{metrics['outperformance']:.2f}%[/{out_color}]",
        "Portfolio minus benchmark"
    )
    table.add_row(
        "Alpha",
        fmt_pct(metrics["alpha"]),
        "Annualised excess return (CAPM)"
    )
    table.add_row(
        "Beta",
        f"{metrics['beta']:.4f}",
        "< 1.0 less volatile than benchmark"
    )

    console.print(table)