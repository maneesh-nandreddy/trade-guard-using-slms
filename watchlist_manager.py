from storage.database import SessionLocal, Watchlist
from typing import List

def add_to_watchlist(symbol: str) -> bool:
    session = SessionLocal()
    existing = session.query(Watchlist).filter_by(symbol=symbol).first()
    if existing:
        session.close()
        return False
    
    new_entry = Watchlist(symbol=symbol)
    session.add(new_entry)
    session.commit()
    session.close()
    return True

def remove_from_watchlist(symbol: str) -> bool:
    session = SessionLocal()
    to_remove = session.query(Watchlist).filter_by(symbol=symbol).first()
    if not to_remove:
        session.close()
        return False
    
    session.delete(to_remove)
    session.commit()
    session.close()
    return True

def get_watchlist() -> List[str]:
    session = SessionLocal()
    items = [item.symbol for item in session.query(Watchlist).all()]
    session.close()
    return items
