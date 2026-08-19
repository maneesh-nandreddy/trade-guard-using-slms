from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

Base = declarative_base()

class Watchlist(Base):
    __tablename__ = 'watchlist'
    symbol = Column(String, primary_key=True)
    added_at = Column(DateTime, default=datetime.datetime.utcnow)

class Alert(Base):
    __tablename__ = 'alerts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    condition = Column(String)
    value = Column(Float)
    triggered = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Trade(Base):
    __tablename__ = 'trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String)
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Integer)
    stop_loss = Column(Float)
    target = Column(Float)
    result = Column(String, nullable=True)
    entry_timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    exit_timestamp = Column(DateTime, nullable=True)

class Portfolio(Base):
    __tablename__ = 'portfolio'
    id = Column(Integer, primary_key=True)
    cash = Column(Float, default=100000.0)

class Position(Base):
    __tablename__ = 'positions'
    symbol = Column(String, primary_key=True)
    quantity = Column(Integer)
    avg_price = Column(Float)

DATABASE_URL = "sqlite:///trade_sentinel.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    if not session.query(Portfolio).first():
        session.add(Portfolio(cash=100000.0))
        session.commit()
    session.close()
