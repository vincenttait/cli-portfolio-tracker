import yfinance as yf
import pandas as pd

TRADING_DAYS_PER_YEAR = 252  #252 is the convention for the number of trading days in a year.

BENCHMARKS = {
    "sp500":  "^GSPC",
    "aex":    "^AEX",
    "ftse":   "^FTSE",
    "dax":    "^GDAXI",
    "nasdaq": "^IXIC",
}


def get_current_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    return stock.fast_info.last_price


def get_company_name(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    return stock.info.get("longName", ticker)


def get_currency(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    return stock.fast_info.currency


def get_fx_rate(from_currency: str, to_currency: str = "EUR") -> float:
    """Fetch live FX rate to convert from_currency to to_currency."""
    if from_currency == to_currency:
        return 1.0
    ticker = f"{from_currency}{to_currency}=X"
    rate = yf.Ticker(ticker).fast_info.last_price
    return rate


def get_price_in_eur(ticker: str) -> tuple[float, str, float]:
    """
    Returns (local_price, currency, eur_price) for a given ticker.
    Fetches the local price and converts to EUR using live FX rate.
    """
    local_price = get_current_price(ticker)
    currency = get_currency(ticker)
    fx_rate = get_fx_rate(currency)
    return local_price, currency, local_price * fx_rate


def get_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist[["Close"]]


def get_multiple_history(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    data = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    return data


def get_benchmark_history(benchmark: str, period: str = "2y") -> pd.DataFrame:
    """
    Fetch historical data for a benchmark index.
    Accepts either a shorthand (sp500, aex, ftse, dax, nasdaq) or a raw Yahoo Finance ticker.
    """
    ticker = BENCHMARKS.get(benchmark.lower(), benchmark)
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist[["Close"]]