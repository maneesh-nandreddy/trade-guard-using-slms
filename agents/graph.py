from langgraph.graph import StateGraph, START, END
from agents.state import AgentState
from agents.nodes import data_fetcher_node, sentiment_analyzer_node, recommendation_node, risk_advice_node, intraday_analyzer_node

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

def build_intraday_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("intraday_analyzer", intraday_analyzer_node)
    
    workflow.add_edge(START, "intraday_analyzer")
    workflow.add_edge("intraday_analyzer", END)
    
    return workflow.compile()
