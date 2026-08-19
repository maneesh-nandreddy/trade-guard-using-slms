from feature_engine.feature_engine import generate_features
from data_layer.data_fetcher import fetch_ohlcv
import pandas as pd

def simple_strategy(symbol: str) -> dict:
    """
    Local rule-based strategy (no LLM).
    Returns recommendation: BUY, SELL, or HOLD.
    """
    df = fetch_ohlcv(symbol)
    if df.empty: return {"recommendation": "HOLD"}
    
    features = generate_features(df)
    rsi = features['rsi']
    trend = features['trend']
    
    current_price = df['Close'].iloc[-1]
    
    # Simple logic
    if rsi < 35 and trend == "up":
        return {
            "recommendation": "BUY",
            "price": current_price,
            "stop_loss": current_price * 0.95,
            "target": current_price * 1.05
        }
    elif rsi > 70:
        return {"recommendation": "SELL", "price": current_price}
    else:
        return {"recommendation": "HOLD"}

def get_simulation_recommendation(symbol: str) -> dict:
    return simple_strategy(symbol)
