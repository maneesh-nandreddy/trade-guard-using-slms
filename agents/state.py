from typing import TypedDict

class AgentState(TypedDict, total=False):
    symbol: str
    risk_profile: str
    investment_amount: float
    min_greedy_profit: float
    llm_provider: str
    market_data: dict
    technical_indicators: dict
    intraday_data: dict
    fundamentals: dict
    sentiment_score: int
    sentiment_reasoning: str
    recommendation: str
    reasoning: str
    buy_target: str
    sell_target: str
    fluctuation_analysis: str
    personalized_advice: str
    averaging_strategy: str
    profit_potential: str
    alerts_triggered: list
    error: str

class MarketState(TypedDict, total=False):
    indices: dict
    scanned_stocks: list
    market_mood: str
    top_suggestions: list
    reasoning: str
    llm_provider: str
    error: str
