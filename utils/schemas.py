from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class TradeSchema(BaseModel):
    symbol: str
    entry_price: float
    exit_price: Optional[float] = None
    quantity: int
    stop_loss: float
    target: float
    result: Optional[str] = None # "win" or "loss"
    timestamp: datetime = Field(default_factory=datetime.now)

class AlertSchema(BaseModel):
    symbol: str
    condition: str # "rsi_above" | "price_below" | "volume_spike"
    value: float
    triggered: bool = False

class PositionSchema(BaseModel):
    symbol: str
    quantity: int
    avg_price: float

class PortfolioSchema(BaseModel):
    cash: float
    positions: List[PositionSchema] = []
    history: List[TradeSchema] = []

class StockDataSchema(BaseModel):
    symbol: str
    price: float
    rsi: float
    trend: str # "up" | "down" | "sideways"
    momentum_score: float
    cached_sentiment: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
