import yfinance as yf
import pandas as pd

def fetch_stock_data(symbol: str) -> dict:
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="3mo")
        if hist.empty:
            return {"error": f"No data found for {symbol}"}
        
        current_price = hist['Close'].iloc[-1]
        news = stock.news[:5] if stock.news else []
        news_titles = [n.get('title', '') for n in news]
        
        return {
            "symbol": symbol,
            "current_price": float(current_price),
            "history": hist.to_json(date_format='iso'),
            "news": news_titles
        }
    except Exception as e:
        return {"error": str(e)}
