import yfinance as yf
import pandas as pd
from typing import Optional

def fetch_ohlcv(symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
    """Fetch historical OHLCV data from yfinance."""
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period, interval=interval)
    return df

def get_current_price(symbol: str) -> float:
    """Fetch the latest price for a symbol."""
    ticker = yf.Ticker(symbol)
    # Use fast_info if available or history(period="1d")
    df = ticker.history(period="1d")
    if not df.empty:
        return df['Close'].iloc[-1]
    return 0.0

def fetch_all_data(symbol: str) -> Optional[pd.DataFrame]:
    """Fetch comprehensive data for a symbol."""
    try:
        df = fetch_ohlcv(symbol)
        if df.empty: return None
        return df
    except Exception:
        return None
