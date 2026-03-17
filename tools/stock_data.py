import yfinance as yf
import pandas as pd
from utils.tv_datafeed import TvDatafeed, Interval

def fetch_stock_data(symbol: str) -> dict:
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
        
    try:
        # 1. Fetch historical data from TradingView
        tv = TvDatafeed()
        # strip .NS for TV, pass NSE as exchange
        tv_symbol = symbol.replace(".NS", "")
        # fetch 250 bars to compute TA indicators like EMA 200 properly
        tv_hist = tv.get_hist(tv_symbol, exchange="NSE", interval=Interval.in_daily, n_bars=250)
        
        if tv_hist is None or tv_hist.empty:
            return {"error": f"No data found for {symbol} on TradingView"}
            
        current_price = tv_hist['Close'].iloc[-1]
        
        # 2. Fetch data and news from yfinance
        stock = yf.Ticker(symbol)
        yf_hist = stock.history(period="3mo")
        news = stock.news[:5] if stock.news else []
        news_titles = [n.get('title', '') for n in news]
        
        return {
            "symbol": symbol,
            "current_price": float(current_price),
            "tv_history": tv_hist.to_json(date_format='iso'),
            "yf_history": yf_hist.to_json(date_format='iso') if not yf_hist.empty else "{}",
            "news": news_titles
        }
    except Exception as e:
        return {"error": str(e)}

def fetch_stock_fundamentals(symbol: str) -> dict:
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return {
            "symbol": symbol,
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "summary": info.get("longBusinessSummary")
        }
    except Exception as e:
        return {"error": str(e)}
