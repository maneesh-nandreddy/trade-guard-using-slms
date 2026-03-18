from langgraph.graph import StateGraph, END
from agents.state import MarketState
from agents.nodes import call_mcp_tool, extract_json, HumanMessage
from utils.llm_factory import get_llm
from tools.market_scan import MARKET_CAP_SEGMENTS, get_market_summary, scan_segment
import json

def market_data_fetcher_node(state: MarketState):
    """Fetches broad market data via MCP Tools."""
    indices = call_mcp_tool("get_market_insights", {})
    error = "error" in indices
    return {
        "indices": indices,
        "scanned_stocks": [],
        "error": "Index data fetch failed" if error else None
    }

def market_analyst_node(state: MarketState):
    """Analyzes market mood and structures stock suggestions from all segments."""
    if state.get("error"):
        return state

    indices = state.get("indices", {})
    all_stocks = state.get("scanned_stocks", [])

    prompt = f"""
    You are an expert Indian Market Analyst. Analyze the current market state and suggest the 3-5 best stocks to look at for buying/investing.
    
    Market Indices: {indices}
    Scanned Stocks Data (across Large Cap, Mid Cap, Small Cap): {all_stocks}
    
    Your Task:
    1. Determine the 'market_mood' (Bullish, Bearish, or Neutral) and explain why in 'reasoning'.
    2. Suggest 3-5 stocks from the scanned list that show the best potential (e.g. low RSI oversold bounce, strong sector momentum, or resilient movers).
    3. For each suggestion include 'symbol', 'segment' (Large/Mid/Small Cap), 'logic', and 'target_zone'.
    
    Return a pure JSON object:
    {{
        "market_mood": "...",
        "reasoning": "...",
        "suggestions": [
            {{"symbol": "...", "segment": "...", "logic": "...", "target_zone": "..."}},
            ...
        ]
    }}
    """

    try:
        llm = get_llm(state.get("llm_provider", "Groq"))
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)

        if not parsed:
            return {"error": "Failed to parse market analysis."}

        return {
            "market_mood": parsed.get("market_mood", "Neutral"),
            "reasoning": parsed.get("reasoning", ""),
            "top_suggestions": parsed.get("suggestions", [])
        }
    except Exception as e:
        return {"error": f"Market analysis failed: {str(e)}"}

def build_market_graph():
    """Builds the market analyst LangGraph."""
    workflow = StateGraph(MarketState)
    workflow.add_node("fetcher", market_data_fetcher_node)
    workflow.add_node("analyst", market_analyst_node)
    workflow.set_entry_point("fetcher")
    workflow.add_edge("fetcher", "analyst")
    workflow.add_edge("analyst", END)
    return workflow.compile()
