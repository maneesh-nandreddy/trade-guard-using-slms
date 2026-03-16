from typing import TypedDict

class AgentState(TypedDict, total=False):
    symbol: str
    risk_profile: str
    market_data: dict
    technical_indicators: dict
    sentiment_score: int
    sentiment_reasoning: str
    recommendation: str
    reasoning: str
    personalized_advice: str
    error: str
