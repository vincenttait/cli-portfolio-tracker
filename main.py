import argparse
from portfolio_tracker.utils.storage import init_db
from portfolio_tracker.controllers import portfolio_controller


def main():
    init_db()

    parser = argparse.ArgumentParser(
        prog="portfolio-tracker",
        description="CLI portfolio tracker — a.s.r. Vermogensbeheer assignment"
    )
    subparsers = parser.add_subparsers(dest="command")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new order to the portfolio")
    add_parser.add_argument("ticker",         type=str,   help="Asset ticker e.g. AAPL")
    add_parser.add_argument("sector",         type=str,   help="Sector e.g. Technology")
    add_parser.add_argument("asset_class",    type=str,   help="Asset class e.g. Equity")
    add_parser.add_argument("quantity",       type=float, help="Number of shares")
    add_parser.add_argument("purchase_price", type=float, help="Price per share at purchase")
    add_parser.add_argument("--date",         type=str,   help="Purchase date (YYYY-MM-DD), defaults to today")

    # show
    subparsers.add_parser("show",     help="Show current portfolio")
    subparsers.add_parser("weights",  help="Show portfolio weights by asset, sector and class")
    subparsers.add_parser("orders",   help="Show full order history")
    subparsers.add_parser("charts",   help="Show portfolio pie charts")
    subparsers.add_parser("simulate", help="Run Monte Carlo simulation")

    # delete
    del_parser = subparsers.add_parser("delete", help="Delete an order by ID")
    del_parser.add_argument("id", type=int, help="Order ID to delete")

    # history
    hist_parser = subparsers.add_parser("history", help="Plot price history for one or more tickers")
    hist_parser.add_argument("tickers", type=str, nargs="+", help="One or more tickers e.g. AAPL MSFT")
    hist_parser.add_argument("--period", type=str, default="1y", help="Period e.g. 1mo 6mo 1y 5y (default: 1y)")

    # correlate
    corr_parser = subparsers.add_parser("correlate", help="Show asset return correlation heatmap")
    corr_parser.add_argument("--period", type=str, default="1y", help="Period for historical returns (default: 1y)")

    # risk
    risk_parser = subparsers.add_parser("risk", help="Show portfolio risk metrics")
    risk_parser.add_argument("--period", type=str, default="2y", help="Historical period for calculations (default: 2y)")

    args = parser.parse_args()

    if args.command == "add":
        portfolio_controller.add_asset(
            ticker=args.ticker,
            sector=args.sector,
            asset_class=args.asset_class,
            quantity=args.quantity,
            purchase_price=args.purchase_price,
            purchase_date=args.date,
        )
    elif args.command == "show":
        portfolio_controller.show_portfolio()
    elif args.command == "weights":
        portfolio_controller.show_weights()
    elif args.command == "orders":
        portfolio_controller.show_orders()
    elif args.command == "charts":
        portfolio_controller.show_charts()
    elif args.command == "simulate":
        portfolio_controller.simulate()
    elif args.command == "delete":
        portfolio_controller.remove_asset(args.id)
    elif args.command == "history":
        portfolio_controller.show_history(args.tickers, args.period)
    elif args.command == "correlate":
        portfolio_controller.show_correlation(args.period)
    elif args.command == "risk":
        portfolio_controller.show_risk(args.period)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()