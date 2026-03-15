import json
from langchain_ollama import OllamaLLM
from agents.state import AgentState
from tools.stock_data import fetch_stock_basic_info, fetch_stock_history, fetch_stock_news
from tools.technical_analysis import analyze_technical_indicators

# Initialize SLM
llm = OllamaLLM(model="phi3:mini", temperature=0.3)

def data_fetcher_node(state: AgentState) -> AgentState:
    """
    Fetches raw market data, technical indicators, and news.
    """
    symbol = state["symbol"]
    
    # Basic Info
    info = fetch_stock_basic_info(symbol)
    if "error" in info:
        return {**state, "errors": [info["error"]]}
    
    # History & Technicals
    history = fetch_stock_history(symbol)
    technicals = analyze_technical_indicators(history)
    
    # News
    news = fetch_stock_news(symbol)
    
    return {
        **state,
        "stock_info": info,
        "technical_analysis": technicals,
        "news": news
    }

def sentiment_analyzer_node(state: AgentState) -> AgentState:
    """
    SLM-based sentiment analysis of news headlines.
    """
    news_items = state.get("news", [])
    if not news_items:
        return {**state, "sentiment_score": 0.0, "sentiment_analysis": "No news found for analysis."}
    
    headlines = "\n".join([f"- {item['title']}" for item in news_items])
    
    prompt = f"""
    Analyze the sentiment of the following news headlines for stock {state['symbol']}.
    Return a JSON object with:
    1. "score": float between -1.0 (very bearish) and 1.0 (very bullish)
    2. "analysis": a 1-sentence summary of the overall sentiment.

    Headlines:
    {headlines}

    Output JSON:
    """
    
    try:
        response = llm.invoke(prompt)
        # Simple extraction if LLM doesn't return pure JSON
        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])
        
        return {
            **state,
            "sentiment_score": data.get("score", 0.0),
            "sentiment_analysis": data.get("analysis", "Sentiment analysis complete.")
        }
    except Exception as e:
        return {
            **state, 
            "errors": [f"Sentiment Node Error: {str(e)}"],
            "sentiment_score": 0.0,
            "sentiment_analysis": "Sentiment analysis failed due to system error."
        }

def recommendation_node(state: AgentState) -> AgentState:
    """
    SLM-based reasoning engine to decide recommendation.
    """
    info = state["stock_info"]
    technicals = state["technical_analysis"]
    sentiment_score = state.get("sentiment_score", 0.0)
    
    prompt = f"""
    Acting as a professional market analyst for the Indian Stock Market (NSE), provide a trade recommendation for {info['symbol']}.
    Consider the following data:
    
    Price: {info['current_price']} ({info['change_pct']:.2f}% change)
    Technicals: {json.dumps(technicals)}
    Sentiment Score: {sentiment_score} (-1 to 1)

    Return a JSON object with exactly these keys:
    1. "recommendation": "BUY", "HOLD", or "SELL"
    2. "risk_score": integer from 1 to 10
    3. "reasoning": list of 3 concise bullet points explaining why.

    Output JSON:
    """
    
    try:
        response = llm.invoke(prompt)
        start = response.find("{")
        end = response.rfind("}") + 1
        data = json.loads(response[start:end])
        
        return {
            **state,
            "recommendation": data.get("recommendation", "HOLD"),
            "risk_score": data.get("risk_score", 5),
            "reasoning": data.get("reasoning", ["Data synthesis failed."])
        }
    except Exception as e:
        return {
            **state, 
            "errors": [f"Recommendation Node Error: {str(e)}"],
            "recommendation": "HOLD",
            "risk_score": 5,
            "reasoning": ["Error in processing recommendation."]
        }

def risk_advice_node(state: AgentState) -> AgentState:
    """
    SLM-based personalized advice based on user risk profile.
    """
    risk_profile = state.get("risk_profile", "Moderate")
    recommendation = state.get("recommendation", "HOLD")
    info = state.get("stock_info", {})
    
    if not info:
        return {**state, "personalized_advice": "No stock data available."}
    
    prompt = f"""
    The user has a '{risk_profile}' risk profile. 
    The system recommended '{recommendation}' for {info.get('symbol')} at price {info.get('current_price')}.
    
    Provide a concise (max 2 sentences) personalized piece of advice for this trader today.
    Focus on position sizing or stop-loss based on their risk profile.
    
    Output Advice:
    """
    
    try:
        advice = llm.invoke(prompt).strip()
        return {**state, "personalized_advice": advice}
    except Exception as e:
        return {**state, "personalized_advice": f"Consult your financial advisor. (Error: {str(e)})"}
