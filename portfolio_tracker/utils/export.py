import io
from datetime import date
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)


def _fig_to_image(fig, width_cm: float = 16) -> Image:
    """Convert a matplotlib figure to a reportlab Image object."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    buf.seek(0)
    plt.close(fig)
    width  = width_cm * cm
    aspect = fig.get_figheight() / fig.get_figwidth()
    return Image(buf, width=width, height=width * aspect)


def _portfolio_table(summary: list[dict]) -> Table:
    """Build a reportlab table from the portfolio summary."""
    headers = ["Ticker", "Name", "Sector", "Class", "Qty", "Avg Price", "Curr Price", "Value (EUR)", "G/L (EUR)", "G/L %", "Weight"]
    rows = [headers]

    for a in summary:
        sign = "+" if a["gain_loss_eur"] >= 0 else ""
        rows.append([
            a["ticker"],
            a["name"],
            a["sector"],
            a["asset_class"],
            f"{a['quantity']:.2f}",
            f"{a['currency']} {a['avg_purchase_price']:.2f}",
            f"{a['currency']} {a['current_price_local']:.2f}",
            f"EUR {a['current_value_eur']:.2f}",
            f"{sign}EUR {a['gain_loss_eur']:.2f}",
            f"{sign}{a['gain_loss_pct']:.2f}%",
            f"{a['weight']:.2f}%",
        ])

    table = Table(rows, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8f8f8"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
    ])
    for i, a in enumerate(summary, start=1):
        colour = colors.HexColor("#1a7a3c") if a["gain_loss_eur"] >= 0 else colors.HexColor("#b22222")
        style.add("TEXTCOLOR", (8, i), (9, i), colour)
    table.setStyle(style)
    return table


def _weights_chart(weights: list[dict], title: str = "Portfolio weights") -> Image:
    """Generate a pie chart of portfolio weights."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie([w["weight"] for w in weights], labels=[w["ticker"] for w in weights], autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    plt.tight_layout()
    return _fig_to_image(fig)


def _breakdown_chart(breakdown: dict[str, float], title: str) -> Image:
    """Generate a pie chart for sector or asset class breakdown."""
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(list(breakdown.values()), labels=list(breakdown.keys()), autopct="%1.1f%%", startangle=90)
    ax.set_title(title)
    plt.tight_layout()
    return _fig_to_image(fig)


def _correlation_chart(tickers: list[str], returns) -> Image:
    """Generate a correlation heatmap."""
    corr = returns.corr()
    n    = len(tickers)
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
    return _fig_to_image(fig)


def _simulation_chart(paths: np.ndarray, initial_value: float, years: int = 15) -> Image:
    """Generate a Monte Carlo fan chart."""
    from portfolio_tracker.models.simulation import get_percentiles
    percentiles = get_percentiles(paths)
    x = np.linspace(0, years, paths.shape[1])
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.fill_between(x, percentiles["p5"],  percentiles["p95"], alpha=0.15, color="steelblue", label="5th–95th percentile")
    ax.fill_between(x, percentiles["p25"], percentiles["p75"], alpha=0.25, color="steelblue", label="25th–75th percentile")
    ax.plot(x, percentiles["p50"], color="steelblue", linewidth=2, label="Median (p50)")
    ax.axhline(y=initial_value, color="gray", linestyle="--", linewidth=1, label="Initial value")
    ax.set_title(f"Monte Carlo simulation — {years}-year outlook (100,000 paths)")
    ax.set_xlabel("Years")
    ax.set_ylabel("Portfolio value (EUR)")
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"EUR {v:,.0f}"))
    ax.legend()
    plt.tight_layout()
    return _fig_to_image(fig)


def _benchmark_chart(metrics: dict) -> Image:
    """Generate a cumulative return comparison chart."""
    portfolio_cum  = (1 + metrics["aligned_portfolio"]).cumprod()
    benchmark_cum  = (1 + metrics["aligned_benchmark"]).cumprod()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(portfolio_cum.index,  portfolio_cum.values,  label="Portfolio",                   linewidth=2, color="steelblue")
    ax.plot(benchmark_cum.index,  benchmark_cum.values,  label=metrics["benchmark"].upper(),   linewidth=2, color="gray", linestyle="--")
    ax.axhline(y=1.0, color="black", linestyle=":", linewidth=0.8)
    ax.set_title(f"Portfolio vs {metrics['benchmark'].upper()} ({metrics['period']})")
    ax.set_xlabel("Date")
    ax.set_ylabel("Cumulative return (1 = starting value)")
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax.legend()
    fig.autofmt_xdate()
    plt.tight_layout()
    return _fig_to_image(fig)


def _frontier_chart(frontier: dict) -> Image:
    """Generate the efficient frontier scatter plot."""
    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(
        frontier["volatilities"], frontier["returns"],
        c=frontier["sharpe_ratios"], cmap="RdYlGn", alpha=0.4, s=8
    )
    plt.colorbar(sc, ax=ax, label="Sharpe ratio")
    ax.scatter(frontier["max_sharpe_vol"], frontier["max_sharpe_return"],
               marker="*", color="blue", s=300, zorder=5, label="Max Sharpe")
    ax.scatter(frontier["min_var_vol"],    frontier["min_var_return"],
               marker="*", color="red",  s=300, zorder=5, label="Min variance")
    ax.set_title(f"Efficient frontier ({frontier['period']} history, 10,000 portfolios)")
    ax.set_xlabel("Annualised volatility (%)")
    ax.set_ylabel("Annualised return (%)")
    ax.legend()
    plt.tight_layout()
    return _fig_to_image(fig)


def _frontier_weights_table(frontier: dict) -> Table:
    """Build a small table showing optimal frontier weights."""
    headers = ["Ticker", "Max Sharpe", "Min Variance"]
    rows = [headers] + [
        [t, f"{ms*100:.1f}%", f"{mv*100:.1f}%"]
        for t, ms, mv in zip(
            frontier["tickers"],
            frontier["max_sharpe_weights"],
            frontier["min_var_weights"]
        )
    ]
    table = Table(rows)
    table.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  colors.HexColor("#1a1a2e")),
        ("TEXTCOLOR",     (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",      (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [colors.HexColor("#f8f8f8"), colors.white]),
        ("GRID",          (0, 0), (-1, -1), 0.25, colors.HexColor("#dddddd")),
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ]))
    return table


def export_pdf(
    summary: list[dict],
    weights: list[dict],
    sector_breakdown: dict[str, float],
    asset_class_breakdown: dict[str, float],
    total_value: float,
    total_invested: float,
    total_gain_loss: float,
    total_gain_loss_pct: float,
    paths: np.ndarray,
    benchmark_metrics: dict,
    frontier: dict,
    filename: str = None,
) -> Path:
    """
    Generate a comprehensive PDF portfolio report including holdings table,
    weight charts, correlation heatmap, benchmark comparison,
    Monte Carlo simulation, and efficient frontier.
    """
    if filename is None:
        filename = f"portfolio_report_{date.today()}.pdf"

    output_path = Path(filename)
    doc = SimpleDocTemplate(str(output_path), pagesize=A4, topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()

    title_style   = ParagraphStyle("title",   parent=styles["Title"],    fontSize=20, spaceAfter=6)
    heading_style = ParagraphStyle("heading", parent=styles["Heading2"], fontSize=13, spaceBefore=16, spaceAfter=6)
    normal_style  = styles["Normal"]
    muted_style   = ParagraphStyle("muted",   parent=styles["Normal"],   fontSize=9,  textColor=colors.HexColor("#666666"))

    gl_sign  = "+" if total_gain_loss >= 0 else ""
    gl_color = "#1a7a3c" if total_gain_loss >= 0 else "#b22222"

    # Fetch returns for correlation heatmap
    from portfolio_tracker.utils.market_data import get_multiple_history
    tickers = [a["ticker"] for a in summary]
    hist    = get_multiple_history(tickers, period="1y")
    returns = hist.pct_change().dropna()

    story = [
        Paragraph("Portfolio Report", title_style),
        Paragraph(f"Generated on {date.today().strftime('%d %B %Y')}", muted_style),
        Spacer(1, 0.5*cm),

        # Summary
        Paragraph("Portfolio summary", heading_style),
        Paragraph(f"Total value:    <b>EUR {total_value:,.2f}</b>", normal_style),
        Paragraph(f"Total invested: <b>EUR {total_invested:,.2f}</b>", normal_style),
        Paragraph(
            f"Total G/L: <b><font color='{gl_color}'>{gl_sign}EUR {total_gain_loss:,.2f} ({gl_sign}{total_gain_loss_pct:.2f}%)</font></b>",
            normal_style
        ),
        Spacer(1, 0.4*cm),

        # Holdings table
        Paragraph("Holdings", heading_style),
        _portfolio_table(summary),
        PageBreak(),

        # Weights
        Paragraph("Portfolio allocation", heading_style),
        _weights_chart(weights, "Asset weights"),
        Spacer(1, 0.3*cm),
        _breakdown_chart(sector_breakdown,      "Sector breakdown"),
        Spacer(1, 0.3*cm),
        _breakdown_chart(asset_class_breakdown, "Asset class breakdown"),
        PageBreak(),

        # Correlation
        Paragraph("Return correlation", heading_style),
        Paragraph("Pairwise correlation of daily returns between portfolio assets. Green = positive correlation, red = negative.", muted_style),
        Spacer(1, 0.3*cm),
        _correlation_chart(tickers, returns),
        PageBreak(),

        # Benchmark
        Paragraph("Benchmark comparison", heading_style),
        Paragraph(
            f"Portfolio cumulative return vs {benchmark_metrics['benchmark'].upper()} over {benchmark_metrics['period']}. "
            f"Alpha: {benchmark_metrics['alpha']:+.2f}%  |  Beta: {benchmark_metrics['beta']:.4f}  |  "
            f"Outperformance: {benchmark_metrics['outperformance']:+.2f}%",
            muted_style
        ),
        Spacer(1, 0.3*cm),
        _benchmark_chart(benchmark_metrics),
        PageBreak(),

        # Simulation
        Paragraph("Monte Carlo simulation", heading_style),
        Paragraph(
            "100,000 simulated portfolio paths over 15 years using Geometric Brownian Motion, "
            "calibrated to historical returns and volatility. Assumes 252 trading days per year.",
            muted_style
        ),
        Spacer(1, 0.3*cm),
        _simulation_chart(paths, total_value),
        PageBreak(),

        # Efficient frontier
        Paragraph("Efficient frontier", heading_style),
        Paragraph(
            "10,000 random portfolio weightings plotted by annualised risk and return, coloured by Sharpe ratio. "
            "The optimal portfolios — maximum Sharpe ratio (blue) and minimum variance (red) — are highlighted.",
            muted_style
        ),
        Spacer(1, 0.3*cm),
        _frontier_chart(frontier),
        Spacer(1, 0.4*cm),
        Paragraph("Optimal weightings", heading_style),
        _frontier_weights_table(frontier),
    ]

    doc.build(story)
    return output_path