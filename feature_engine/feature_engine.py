import pandas as pd
import pandas_ta as ta

def calculate_rsi(df: pd.DataFrame, length=14) -> float:
    if len(df) < length: return 50.0
    rsi = df.ta.rsi(length=length)
    return rsi.iloc[-1] if not rsi.empty else 50.0

def calculate_trend(df: pd.DataFrame) -> str:
    if len(df) < 50: return "sideways"
    sma_20 = df.ta.sma(length=20)
    sma_50 = df.ta.sma(length=50)
    
    current_price = df['Close'].iloc[-1]
    last_sma_20 = sma_20.iloc[-1]
    last_sma_50 = sma_50.iloc[-1]
    
    if current_price > last_sma_20 > last_sma_50:
        return "up"
    elif current_price < last_sma_20 < last_sma_50:
        return "down"
    else:
        return "sideways"

def calculate_momentum_score(df: pd.DataFrame) -> float:
    """
    Custom formula for momentum scoring.
    Combines RSI, Rate of Change (ROC), and price relative to SMAs.
    """
    if len(df) < 20: return 50.0
    
    rsi = calculate_rsi(df)
    roc = df.ta.roc(length=10).iloc[-1] if not df.ta.roc(length=10).empty else 0.0
    
    # Normalize RSI (0-100) and ROC (assume -10 to 10 range for normalization)
    norm_rsi = rsi
    norm_roc = max(min((roc + 10) * 5, 100), 0)
    
    score = (norm_rsi * 0.6) + (norm_roc * 0.4)
    return round(score, 2)

def generate_features(df: pd.DataFrame) -> dict:
    return {
        "rsi": calculate_rsi(df),
        "trend": calculate_trend(df),
        "momentum_score": calculate_momentum_score(df)
    }
