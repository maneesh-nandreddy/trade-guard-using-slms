from storage.database import SessionLocal, Alert, Watchlist
from data_layer.data_fetcher import get_current_price, fetch_ohlcv
from feature_engine.feature_engine import calculate_rsi
import pandas as pd

def evaluate_alerts():
    """
    Core rule evaluation engine. 
    Checks all active alerts against latest market data.
    """
    session = SessionLocal()
    active_alerts = session.query(Alert).filter_by(triggered=False).all()
    
    triggered_alerts = []
    
    for alert in active_alerts:
        symbol = alert.symbol
        condition = alert.condition
        threshold = alert.value
        
        current_value = None
        is_triggered = False
        
        if condition == "price_above":
            current_value = get_current_price(symbol)
            if current_value >= threshold:
                is_triggered = True
        elif condition == "price_below":
            current_value = get_current_price(symbol)
            if current_value <= threshold:
                is_triggered = True
        elif condition == "rsi_above":
            df = fetch_ohlcv(symbol)
            if not df.empty:
                current_value = calculate_rsi(df)
                if current_value >= threshold:
                    is_triggered = True
        elif condition == "rsi_below":
            df = fetch_ohlcv(symbol)
            if not df.empty:
                current_value = calculate_rsi(df)
                if current_value <= threshold:
                    is_triggered = True
        elif condition == "volume_spike":
            df = fetch_ohlcv(symbol, period="5d")
            if not df.empty and len(df) > 1:
                avg_vol = df['Volume'].iloc[:-1].mean()
                curr_vol = df['Volume'].iloc[-1]
                current_value = curr_vol / avg_vol
                if current_value >= threshold: # e.g. threshold = 2.0 (2x avg)
                    is_triggered = True
        
        if is_triggered:
            alert.triggered = True
            triggered_alerts.append({
                "symbol": symbol,
                "condition": condition,
                "threshold": threshold,
                "current_value": current_value
            })
            
    if triggered_alerts:
        session.commit()
    
    session.close()
    return triggered_alerts

def add_alert(symbol: str, condition: str, value: float):
    session = SessionLocal()
    new_alert = Alert(symbol=symbol, condition=condition, value=value)
    session.add(new_alert)
    session.commit()
    session.close()

def get_active_alerts():
    session = SessionLocal()
    alerts = session.query(Alert).filter_by(triggered=False).all()
    # Convert to list of dicts for transparency
    results = [{"id": a.id, "symbol": a.symbol, "condition": a.condition, "value": a.value} for a in alerts]
    session.close()
    return results
