from storage.database import SessionLocal, Trade, Portfolio
from typing import Dict

def calculate_performance_metrics() -> Dict:
    session = SessionLocal()
    trades = session.query(Trade).filter(Trade.exit_price != None).all()
    portfolio = session.query(Portfolio).first()
    
    total_trades = len(trades)
    wins = [t for t in trades if (t.exit_price > t.entry_price)]
    win_rate = (len(wins) / total_trades * 100) if total_trades > 0 else 0.0
    
    total_pnl = sum([(t.exit_price - t.entry_price) * t.quantity for t in trades])
    pnl_pct = (total_pnl / 100000.0 * 100) # Initial capital 100,000
    
    metrics = {
        "total_trades": total_trades,
        "win_rate": f"{win_rate:.2f}%",
        "total_pnl": f"₹{total_pnl:.2f}",
        "pnl_pct": f"{pnl_pct:.2f}%",
        "current_cash": f"₹{portfolio.cash:.2f}" if portfolio else "0.00"
    }
    session.close()
    return metrics
