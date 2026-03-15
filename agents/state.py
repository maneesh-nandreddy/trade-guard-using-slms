from typing import TypedDict, List, Dict, Any, Annotated
import operator

class AgentState(TypedDict):
    """
    Represents the state of the agentic workflow.
    """
    symbol: str
    risk_profile: str # Conservative, Moderate, Aggressive
    
    # Tool Outputs
    stock_info: Dict[str, Any]
    technical_analysis: Dict[str, Any]
    news: List[Dict[str, str]]
    
    # Node Outputs
    sentiment_score: float # -1 to 1
    sentiment_analysis: str
    recommendation: str # BUY, HOLD, SELL
    risk_score: int # 1 to 10
    reasoning: List[str]
    personalized_advice: str
    
    # Metadata
    errors: Annotated[List[str], operator.add]
