from execution_engine.trade_executor import execute_buy, execute_sell
from strategy_engine.strategy_engine import get_simulation_recommendation
from storage.database import SessionLocal, Watchlist, Position, Trade
from portfolio_engine.portfolio_manager import get_portfolio_summary
import logging

logger = logging.getLogger(__name__)

def run_simulation_step():
    """
    6Runs a single step of the auto-simulation.
    Checks watchlist, evaluates strategy, and executes trades.
    """
    session = SessionLocal()
    watchlist = [item.symbol for item in session.query(Watchlist).all()]
    
    # 1. Check existing positions for exit (SELL)
    positions = session.query(Position).all()
    for pos in positions:
        strat = get_simulation_recommendation(pos.symbol)
        if strat.get("recommendation") == "SELL":
            # Find the active trade log to close it
            trade = session.query(Trade).filter_by(symbol=pos.symbol, result=None).first()
            if trade:
                execute_sell(pos.symbol, pos.quantity, trade.id)
                logger.info(f"Simulation: SOLD {pos.quantity} of {pos.symbol}")
    
    # 2. Check watchlist for entry (BUY)
    # Constraints: Max 3 active trades/positions at a time
    current_pos_count = session.query(Position).count() 
    if current_pos_count < 3:
        for symbol in watchlist:
            # Don't buy if already holding
            if session.query(Position).filter_by(symbol=symbol).first():
                continue
            
            strat = get_simulation_recommendation(symbol)
            if strat.get("recommendation") == "BUY":
                # Fixed risk: buy 100 shares for now (or calculate based on capital)
                qty = 100 
                execute_buy(symbol, qty, strat.get("stop_loss"), strat.get("target"))
                logger.info(f"Simulation: BOUGHT {qty} of {symbol}")
                current_pos_count += 1
                if current_pos_count >= 3: break
                
    session.close()
