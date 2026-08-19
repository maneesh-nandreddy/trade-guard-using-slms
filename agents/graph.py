from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.nodes import (
    data_fetcher_node, sentiment_analyzer_node, recommendation_node, 
    risk_advice_node, intraday_analyzer_node, feature_engine_node,
    regime_detection_node, execution_node, alert_node
)

def build_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("sentiment_analyzer", sentiment_analyzer_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("risk_advice", risk_advice_node)
    
    workflow.add_edge(START, "data_fetcher")
    
    def conditional_next(state: AgentState):
        if state.get("error"):
            return END
        return "sentiment_analyzer"
        
    workflow.add_conditional_edges("data_fetcher", conditional_next)
    workflow.add_edge("sentiment_analyzer", "recommendation")
    workflow.add_edge("recommendation", "risk_advice")
    workflow.add_edge("risk_advice", END)
    
    return workflow.compile()

def build_advanced_graph():
    """
    Advanced agentic workflow with feature engine, regime detection, 
    paper trading execution, and alerts.
    """
    workflow = StateGraph(AgentState)
    
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("feature_engine", feature_engine_node)
    workflow.add_node("regime_detection", regime_detection_node)
    workflow.add_node("sentiment_analyzer", sentiment_analyzer_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("risk_advice", risk_advice_node)
    workflow.add_node("execution", execution_node)
    workflow.add_node("alerts", alert_node)
    
    # Flow
    workflow.add_edge(START, "data_fetcher")
    workflow.add_edge("data_fetcher", "feature_engine")
    workflow.add_edge("feature_engine", "regime_detection")
    workflow.add_edge("regime_detection", "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", "recommendation")
    workflow.add_edge("recommendation", "risk_advice")
    workflow.add_edge("risk_advice", "execution")
    workflow.add_edge("execution", "alerts")
    workflow.add_edge("alerts", END)
    
    return workflow.compile()

def build_intraday_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("intraday_analyzer", intraday_analyzer_node)
    
    workflow.add_edge(START, "intraday_analyzer")
    workflow.add_edge("intraday_analyzer", END)
    
    return workflow.compile()
