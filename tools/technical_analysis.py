import pandas as pd
import pandas_ta as ta

def calculate_technical_indicators(hist_json: str) -> dict:
    import io
    try:
        df = pd.read_json(io.StringIO(hist_json))
        if df.empty or len(df) < 20:
            return {"error": "Not enough data for technical analysis. Minimum 20 days required."}
            
        df.ta.rsi(length=14, append=True)
        df.ta.macd(fast=12, slow=26, signal=9, append=True)
        df.ta.bbands(length=20, std=2, append=True)
        
        # EMA for trend
        df.ta.ema(length=50, append=True)
        df.ta.ema(length=200, append=True)
        
        # Forward fill to handle any NaNs and get the latest
        df.ffill(inplace=True)
        latest = df.iloc[-1]
        
        rsi = latest.get('RSI_14', 50)
        macd = latest.get('MACD_12_26_9', 0)
        macd_signal = latest.get('MACDs_12_26_9', 0)
        ema_50 = latest.get('EMA_50', 0)
        ema_200 = latest.get('EMA_200', 0)
        bb_upper = latest.get('BBU_20_2.0', 0)
        bb_lower = latest.get('BBL_20_2.0', 0)
        
        trend = "bullish" if (macd > macd_signal and ema_50 > ema_200) else "bearish"
        if rsi > 70:
            overbought_oversold = "Overbought"
        elif rsi < 30:
            overbought_oversold = "Oversold"
        else:
            overbought_oversold = "Neutral"

        return {
            "rsi": float(rsi),
            "macd": float(macd),
            "macd_signal": float(macd_signal),
            "ema_50": float(ema_50) if not pd.isna(ema_50) else None,
            "ema_200": float(ema_200) if not pd.isna(ema_200) else None,
            "bb_upper": float(bb_upper),
            "bb_lower": float(bb_lower),
            "trend": trend,
            "condition": overbought_oversold
        }
    except Exception as e:
        return {"error": f"TA calculation failed: {str(e)}"}
