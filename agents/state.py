from typing import TypedDict

class AgentState(TypedDict, total=False):
    symbol: str
    risk_profile: str
    market_data: dict
    technical_indicators: dict
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
    error: str
