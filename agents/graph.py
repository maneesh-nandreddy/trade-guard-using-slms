from langgraph.graph import StateGraph, END
from agents.state import AgentState
from agents.nodes import data_fetcher_node, sentiment_analyzer_node, recommendation_node, risk_advice_node

def create_trade_graph():
    """
    Creates and compiles the LangGraph state machine.
    """
    workflow = StateGraph(AgentState)
    
    # Add Nodes
    workflow.add_node("data_fetcher", data_fetcher_node)
    workflow.add_node("sentiment_analyzer", sentiment_analyzer_node)
    workflow.add_node("recommendation", recommendation_node)
    workflow.add_node("risk_advice", risk_advice_node)
    
    # Define Edges (Sequential for this logic)
    workflow.set_entry_point("data_fetcher")
    workflow.add_edge("data_fetcher", "sentiment_analyzer")
    workflow.add_edge("sentiment_analyzer", "recommendation")
    workflow.add_edge("recommendation", "risk_advice")
    workflow.add_edge("risk_advice", END)
    
    # Compile
    app = workflow.compile()
    return app

# For singleton usage
trade_graph = create_trade_graph()
