import yfinance as yf
import pandas as pd
import json

# Market cap segmented watchlist for Indian stocks
MARKET_CAP_SEGMENTS = {
    "Large Cap": {
        "Banking": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS"],
        "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS"],
        "Energy": ["RELIANCE.NS", "ONGC.NS"],
        "Consumer": ["HINDUNILVR.NS", "ITC.NS"],
        "Pharma": ["SUNPHARMA.NS"],
        "Automobile": ["MARUTI.NS", "M&M.NS"],
    },
    "Mid Cap": {
        "Banking": ["FEDERALBNK.NS", "BANDHANBNK.NS"],
        "IT": ["MPHASIS.NS", "LTTS.NS", "PERSISTENT.NS"],
        "Pharma": ["TORNTPHARM.NS", "ALKEM.NS"],
        "Consumer": ["GODREJCP.NS", "DABUR.NS"],
        "Infrastructure": ["CUMMINSIND.NS", "APLAPOLLO.NS"],
    },
    "Small Cap": {
        "IT": ["NEWGEN.NS", "TANLA.NS"],
        "Pharma": ["GRANULES.NS", "SUVEN.NS"],
        "Consumer": ["VSTIND.NS", "PDMJEPAPER.NS"],
        "Finance": ["CREDITACC.NS", "AAVAS.NS"],
    }
}

MAJOR_INDICES = {
    "NIFTY 50": "^NSEI",
    "NIFTY BANK": "^NSEBANK",
    "NIFTY IT": "^CNXIT"
}

def get_market_summary() -> dict:
    """Gets the performance of major Indian indices."""
    summary = {}
    for name, ticker in MAJOR_INDICES.items():
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="2d")
            if len(hist) >= 2:
                prev_close = hist['Close'].iloc[-2]
                curr_price = hist['Close'].iloc[-1]
                p_change = ((curr_price - prev_close) / prev_close) * 100
                summary[name] = {
                    "price": round(curr_price, 2),
                    "change_pct": round(p_change, 2)
                }
        except Exception:
            summary[name] = "Error fetching data"
    return summary

def scan_segment(segment_name: str) -> dict:
    """Scans a specific market cap segment and returns stock data with technicals."""
    segment = MARKET_CAP_SEGMENTS.get(segment_name, {})
    all_tickers = [t for sector in segment.values() for t in sector]
    
    if not all_tickers:
        return {"stocks": [], "segment": segment_name}
    
    results = []
    try:
        data = yf.download(all_tickers, period="14d", interval="1d", group_by='ticker', auto_adjust=True)
        
        for sector, tickers in segment.items():
            for ticker in tickers:
                try:
                    ticker_data = data[ticker] if len(all_tickers) > 1 else data
                    if ticker_data.empty or len(ticker_data) < 2:
                        continue
                    
                    curr_price = ticker_data['Close'].iloc[-1]
                    prev_close = ticker_data['Close'].iloc[-2]
                    p_change = ((curr_price - prev_close) / prev_close) * 100
                    
                    # RSI (14 period)
                    delta = ticker_data['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    rsi = 100 - (100 / (1 + rs.iloc[-1]))
                    
                    results.append({
                        "symbol": ticker,
                        "sector": sector,
                        "segment": segment_name,
                        "price": round(curr_price, 2),
                        "change_pct": round(p_change, 2),
                        "rsi": round(rsi, 2) if not pd.isna(rsi) else None
                    })
                except Exception:
                    continue
    except Exception as e:
        return {"stocks": [], "segment": segment_name, "error": str(e)}
    
    return {"stocks": results, "segment": segment_name}

def scan_top_stocks() -> dict:
    """Scans all market cap segments and returns combined results."""
    all_results = []
    for segment_name, segment in MARKET_CAP_SEGMENTS.items():
        result = scan_segment(segment_name)
        all_results.extend(result.get("stocks", []))
    return {"stocks": all_results}
