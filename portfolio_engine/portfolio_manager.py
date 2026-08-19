from storage.database import SessionLocal, Portfolio, Position, Trade
from typing import List, Dict
import datetime

def get_portfolio_summary() -> Dict:
    session = SessionLocal()
    portfolio = session.query(Portfolio).first()
    positions = session.query(Position).all()
    
    pos_list = [{"symbol": p.symbol, "quantity": p.quantity, "avg_price": p.avg_price} for p in positions]
    
    summary = {
        "cash": portfolio.cash if portfolio else 0.0,
        "positions": pos_list
    }
    session.close()
    return summary

def update_cash(amount: float):
    session = SessionLocal()
    portfolio = session.query(Portfolio).first()
    if portfolio:
        portfolio.cash += amount
        session.commit()
    session.close()

def add_position(symbol: str, quantity: int, price: float):
    session = SessionLocal()
    pos = session.query(Position).filter_by(symbol=symbol).first()
    if pos:
        total_qty = pos.quantity + quantity
        total_cost = (pos.quantity * pos.avg_price) + (quantity * price)
        pos.avg_price = total_cost / total_qty
        pos.quantity = total_qty
    else:
        new_pos = Position(symbol=symbol, quantity=quantity, avg_price=price)
        session.add(new_pos)
    session.commit()
    session.close()

def remove_position(symbol: str, quantity: int):
    session = SessionLocal()
    pos = session.query(Position).filter_by(symbol=symbol).first()
    if pos:
        if pos.quantity >= quantity:
            pos.quantity -= quantity
            if pos.quantity == 0:
                session.delete(pos)
            session.commit()
            session.close()
            return True
    session.close()
    return False

def log_trade(symbol: str, entry_price: float, quantity: int, stop_loss: float, target: float):
    session = SessionLocal()
    new_trade = Trade(
        symbol=symbol,
        entry_price=entry_price,
        quantity=quantity,
        stop_loss=stop_loss,
        target=target
    )
    session.add(new_trade)
    session.commit()
    trade_id = new_trade.id
    session.close()
    return trade_id

def close_trade(trade_id: int, exit_price: float, result: str):
    session = SessionLocal()
    trade = session.query(Trade).filter_by(id=trade_id).first()
    if trade:
        trade.exit_price = exit_price
        trade.result = result
        trade.exit_timestamp = datetime.datetime.utcnow()
        session.commit()
    session.close()
