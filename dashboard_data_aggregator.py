from data_layer.data_fetcher import fetch_ohlcv
from feature_engine.feature_engine import generate_features
from storage.database import SessionLocal, Watchlist
from utils.schemas import StockDataSchema
from typing import List

def get_watchlist_data() -> List[StockDataSchema]:
    """
    Fetch and process data for all stocks in the watchlist.
    No LLM calls here – all technical calculation is local.
    """
    session = SessionLocal()
    watchlist_symbols = [item.symbol for item in session.query(Watchlist).all()]
    session.close()
    
    results = []
    for symbol in watchlist_symbols:
        df = fetch_ohlcv(symbol)
        if df.empty: continue
        
        features = generate_features(df)
        current_price = df['Close'].iloc[-1]
        
        # In a real app, cached sentiment would be fetched from a database
        # For now, we'll placeholder it as "Neutral" until we implement sentiment batching
        stock_data = StockDataSchema(
            symbol=symbol,
            price=current_price,
            rsi=features['rsi'],
            trend=features['trend'],
            momentum_score=features['momentum_score'],
            cached_sentiment="Neutral" 
        )
        results.append(stock_data)
        
    return results

def get_market_sentiment_batched(symbols: List[str]):
    """
    Batched sentiment analysis (Groq) – to be called every few hours.
    Not implemented yet (placeholder).
    """
    pass
