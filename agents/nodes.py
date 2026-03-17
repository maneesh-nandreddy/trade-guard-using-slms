from agents.state import AgentState
from tools.stock_data import fetch_stock_data
from tools.technical_analysis import calculate_technical_indicators
from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
import json
import re

llm = ChatOllama(model="phi3:mini", temperature=0)

def extract_json(text):
    match = re.search(r'\{.*\}', text.replace('\n', ' '))
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass
    return None

def data_fetcher_node(state: AgentState):
    symbol = state.get("symbol")
    data = fetch_stock_data(symbol)
    if "error" in data:
        return {"error": data["error"]}
        
    tech_data = calculate_technical_indicators(data.get("tv_history", "{}"))
    return {"market_data": data, "technical_indicators": tech_data, "error": None}

def sentiment_analyzer_node(state: AgentState):
    if state.get("error"):
        return state
    news = state.get("market_data", {}).get("news", [])
    if not news:
        return {"sentiment_score": 0, "sentiment_reasoning": "No news available."}
        
    prompt = f"Analyze the following recent news headlines for the stock {state['symbol']}. Return a pure JSON object with exactly two keys: 'score' (number: 1 for bullish, 0 for neutral, -1 for bearish) and 'reasoning' (short string explanation). News: {news}"
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)
        if not parsed:
            parsed = {"score": 0, "reasoning": "Could not parse SLM output."}
        return {"sentiment_score": parsed.get('score', 0), "sentiment_reasoning": parsed.get('reasoning', '')}
    except Exception as e:
        return {"sentiment_score": 0, "sentiment_reasoning": f"SLM Error: {str(e)}"}

def extract_recent_history(hist_str: str, days: int = 5) -> str:
    try:
        data = json.loads(hist_str)
        if not data: return "{}"
        
        # We assume data is {"Close": {"date": price, ...}, "Open": ...} based on df.to_json()
        recent_data = {}
        for col, timeline in data.items():
            if isinstance(timeline, dict):
                # Sort by date and take the last 'days' items
                sorted_dates = sorted(timeline.keys())[-days:]
                recent_data[col] = {date: timeline[date] for date in sorted_dates}
        return json.dumps(recent_data)
    except Exception:
        return "{}"

def recommendation_node(state: AgentState):
    if state.get("error"):
        return state
        
    market_data = state.get("market_data", {})
    tv_recent = extract_recent_history(market_data.get("tv_history", "{}"), days=5)
    yf_recent = extract_recent_history(market_data.get("yf_history", "{}"), days=5)
        
    prompt = f"""
    You are an expert Indian stock market analyst. Based on this data, return a pure JSON object recommending BUY, HOLD, or SELL for {state['symbol']}.
    It is extremely important that you perform thorough research based on the provided data. Provide deep strategic insights into WHY the stock is fluctuating and what this downward/upward momentum means for retail investors.
    Also, analyze the support and resistance to provide specific "buy_target" (the price level to buy the dip) and "sell_target" (the price level to take profits).
    
    Current Price: {market_data.get('current_price')}
    Technical Indicators: {state['technical_indicators']}
    News Sentiment Score (1=bullish, 0=neutral, -1=bearish): {state['sentiment_score']}
    
    TradingView Recent OHLCV (Last 5 Days): {tv_recent}
    YFinance Recent OHLCV (Last 5 Days): {yf_recent}
    
    Must return exactly JSON: {{"recommendation": "BUY|HOLD|SELL", "reasoning": "Why?", "buy_target": "e.g. ₹XXX", "sell_target": "e.g. ₹XXX", "fluctuation_analysis": "Detailed explanation of recent price fluctuations."}}
    """
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)
        if not parsed:
            parsed = {"recommendation": "HOLD", "reasoning": "Failed to parse recommendation from SLM.", "buy_target": "N/A", "sell_target": "N/A", "fluctuation_analysis": "Data unavailable."}
            
        return {
            "recommendation": parsed.get("recommendation", "HOLD").upper(), 
            "reasoning": parsed.get("reasoning", ""),
            "buy_target": str(parsed.get("buy_target", "N/A")),
            "sell_target": str(parsed.get("sell_target", "N/A")),
            "fluctuation_analysis": parsed.get("fluctuation_analysis", "No fluctuation analysis provided by SLM.")
        }
    except Exception as e:
        return {"error": str(e)}

def risk_advice_node(state: AgentState):
    if state.get("error"):
        return state
        
    prompt = f"""
    The user has a {state.get('risk_profile', 'moderate')} risk profile. 
    The recommendation for {state['symbol']} is to {state.get('recommendation', 'HOLD')} because {state.get('reasoning', 'No reason')}.
    Provide a personalized short advice paragraph taking their risk profile into account.
    """
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return {"personalized_advice": response.content.strip()}
    except Exception as e:
        return {"personalized_advice": "Unable to generate personalized advice."}
