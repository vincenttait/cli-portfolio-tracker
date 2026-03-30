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