import yfinance as yf
import pandas as pd


def get_current_price(ticker: str) -> float:
    stock = yf.Ticker(ticker)
    data = stock.fast_info
    return data.last_price


def get_company_name(ticker: str) -> str:
    stock = yf.Ticker(ticker)
    return stock.info.get("longName", ticker)


def get_history(ticker: str, period: str = "1y") -> pd.DataFrame:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist[["Close"]]


def get_multiple_history(tickers: list[str], period: str = "1y") -> pd.DataFrame:
    data = yf.download(tickers, period=period, auto_adjust=True)["Close"]
    return data