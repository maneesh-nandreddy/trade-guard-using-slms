import yfinance as yf
import pandas as pd
from typing import Dict, Any, List

def fetch_stock_basic_info(symbol: str) -> Dict[str, Any]:
    """
    Fetches basic information for a given stock symbol.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName", "N/A"),
            "current_price": info.get("currentPrice", 0.0),
            "previous_close": info.get("previousClose", 0.0),
            "change_pct": ((info.get("currentPrice", 0.0) - info.get("previousClose", 0.0)) / info.get("previousClose", 1.0)) * 100,
            "market_cap": info.get("marketCap", 0),
            "volume": info.get("volume", 0),
            "52_week_high": info.get("fiftyTwoWeekHigh", 0.0),
            "52_week_low": info.get("fiftyTwoWeekLow", 0.0),
            "currency": info.get("currency", "INR")
        }
    except Exception as e:
        return {"error": f"Error fetching info for {symbol}: {str(e)}"}

def fetch_stock_history(symbol: str, period: str = "1mo") -> pd.DataFrame:
    """
    Fetches historical price data for technical analysis.
    """
    try:
        ticker = yf.Ticker(symbol)
        history = ticker.history(period=period)
        return history
    except Exception as e:
        print(f"Error fetching history: {e}")
        return pd.DataFrame()

def fetch_stock_news(symbol: str) -> List[Dict[str, str]]:
    """
    Fetches latest news headlines for sentiment analysis.
    """
    try:
        ticker = yf.Ticker(symbol)
        news = ticker.news
        headlines = []
        for item in news[:5]: # Take top 5 news
            headlines.append({
                "title": item.get("title", ""),
                "publisher": item.get("publisher", ""),
                "link": item.get("link", "")
            })
        return headlines
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []
