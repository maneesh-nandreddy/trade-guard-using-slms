import pandas as pd
import pandas_ta as ta
from typing import Dict, Any

def analyze_technical_indicators(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculates technical indicators for the given historical data.
    """
    if df.empty or len(df) < 20:
        return {"error": "Insufficient data for technical analysis"}
    
    # Calculate indicators
    df.ta.rsi(length=14, append=True)
    df.ta.macd(fast=12, slow=26, signal=9, append=True)
    df.ta.bbands(length=20, std=2, append=True)
    df.ta.ema(length=50, append=True)
    df.ta.ema(length=200, append=True)
    
    latest = df.iloc[-1]
    
    rsi = latest.get("RSI_14", 50)
    macd = latest.get("MACD_12_26_9", 0)
    macd_signal = latest.get("MACDs_12_26_9", 0)
    bb_upper = latest.get("BBU_20_2.0", 0)
    bb_lower = latest.get("BBL_20_2.0", 0)
    bb_mid = latest.get("BBM_20_2.0", 0)
    ema_50 = latest.get("EMA_50", 0)
    ema_200 = latest.get("EMA_200", 0)
    current_price = latest.get("Close", 0)
    
    # Simple logic for technical summary
    rsi_signal = "Neutral"
    if rsi > 70: rsi_signal = "Overbought (Sell Pressure)"
    elif rsi < 30: rsi_signal = "Oversold (Buy Opportunity)"
    
    trend = "Neutral"
    if ema_50 > ema_200: trend = "Bullish (Golden Cross/Alignment)"
    elif ema_50 < ema_200: trend = "Bearish (Death Cross/Alignment)"
    
    return {
        "rsi": round(rsi, 2),
        "rsi_signal": rsi_signal,
        "macd": round(macd, 4),
        "macd_signal_line": round(macd_signal, 4),
        "macd_divergence": "Bullish" if macd > macd_signal else "Bearish",
        "bb_upper": round(bb_upper, 2),
        "bb_lower": round(bb_lower, 2),
        "ema_50": round(ema_50, 2),
        "ema_200": round(ema_200, 2),
        "trend": trend,
        "current_price": round(current_price, 2)
    }
