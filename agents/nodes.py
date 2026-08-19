from agents.state import AgentState
from langchain_core.messages import HumanMessage
import json
import re
import subprocess
import sys
from utils.llm_factory import get_llm
from feature_engine.feature_engine import generate_features
from data_layer.data_fetcher import fetch_ohlcv
from strategy_engine.strategy_engine import get_simulation_recommendation
from execution_engine.trade_executor import execute_buy, execute_sell
from alert_engine.alert_engine import evaluate_alerts
from storage.database import SessionLocal, Trade, Position

def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    # Simulating MCP call for now to keep it lightweight, or we can use the actual SDK.
    # For this local prototype, we will import and call tools directly as if via MCP.
    from mcp_server import get_stock_info, analyze_data, analyze_fundamentals, get_market_insights, scan_markets
    if tool_name == "get_stock_info":
        return json.loads(get_stock_info(**arguments))
    elif tool_name == "analyze_data":
        return json.loads(analyze_data(**arguments))
    elif tool_name == "analyze_fundamentals":
        return json.loads(analyze_fundamentals(**arguments))
    elif tool_name == "get_market_insights":
        return json.loads(get_market_insights())
    elif tool_name == "scan_markets":
        return json.loads(scan_markets())
    return {"error": "Tool not found"}

def get_mcp_resource(uri: str) -> str:
    from mcp_server import get_portfolio
    if uri == "portfolio://current":
        return get_portfolio()
    return "{}"

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
    # Call MCP Tool
    data = call_mcp_tool("get_stock_info", {"symbol": symbol})
    if "error" in data:
        return {"error": data["error"]}
        
    # Call MCP Tool
    tech_data = call_mcp_tool("analyze_data", {"hist_json": data.get("tv_history", "{}")})
    
    # NEW: Call MCP Tool for Fundamentals
    fundamentals = call_mcp_tool("analyze_fundamentals", {"symbol": symbol})
    
    return {
        "market_data": data, 
        "technical_indicators": tech_data, 
        "fundamentals": fundamentals,
        "error": None
    }

def sentiment_analyzer_node(state: AgentState):
    if state.get("error"):
        return state
    news = state.get("market_data", {}).get("news", [])
    if not news:
        return {"sentiment_score": 0, "sentiment_reasoning": "No news available."}
        
    prompt = f"Analyze the following recent news headlines for the stock {state['symbol']}. Return a pure JSON object with exactly two keys: 'score' (number: 1 for bullish, 0 for neutral, -1 for bearish) and 'reasoning' (short string explanation). News: {news}"
    
    try:
        llm = get_llm(state.get("llm_provider", "Ollama"))
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
        
        recent_data = {}
        for col, timeline in data.items():
            if isinstance(timeline, dict):
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
    Stock Fundamentals: {state.get('fundamentals')}
    News Sentiment Score (1=bullish, 0=neutral, -1=bearish): {state['sentiment_score']}
    
    TradingView Recent OHLCV (Last 5 Days): {tv_recent}
    YFinance Recent OHLCV (Last 5 Days): {yf_recent}
    
    Must return exactly JSON: {{"recommendation": "BUY|HOLD|SELL", "reasoning": "Why?", "buy_target": "e.g. ₹XXX", "sell_target": "e.g. ₹XXX", "fluctuation_analysis": "Detailed explanation of recent price fluctuations."}}
    """
    
    try:
        llm = get_llm(state.get("llm_provider", "Ollama"))
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
    
    # Fetch Portfolio Resource from MCP
    portfolio_json = get_mcp_resource("portfolio://current")
    portfolio = json.loads(portfolio_json)
    
    # Check if stock is in portfolio
    holding = next((item for item in portfolio if item['symbol'] == state['symbol']), None)
        
    prompt = f"""
    The user has a {state.get('risk_profile', 'moderate')} risk profile. 
    The recommendation for {state['symbol']} is to {state.get('recommendation', 'HOLD')} because {state.get('reasoning', 'No reason')}.
    
    User context:
    Portfolio Holdings: {portfolio_json}
    Symbol to Analyze: {state['symbol']}
    
    Provide a personalized short advice paragraph taking their risk profile and current portfolio into account.
    If they already own the stock, you MUST provide:
    1. "averaging_strategy": A clear instruction like "If it hits ₹XXX, buy Y more shares to bring average to ₹ZZZ."
    2. "profit_potential": An estimate of "Target profit is ₹AAAA if held for [Timeframe]."
    
    Return as JSON: {{"advice": "Concise paragraph", "averaging_strategy": "Plan", "profit_potential": "Estimate"}}
    """
    try:
        llm = get_llm(state.get("llm_provider", "Ollama"))
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)
        if not parsed:
            return {"personalized_advice": response.content.strip(), "averaging_strategy": "N/A", "profit_potential": "N/A"}
            
        return {
            "personalized_advice": parsed.get("advice", ""), 
            "averaging_strategy": parsed.get("averaging_strategy", "N/A"),
            "profit_potential": parsed.get("profit_potential", "N/A")
        }
    except Exception as e:
        return {"personalized_advice": "Unable to generate personalized advice.", "averaging_strategy": "N/A", "profit_potential": "N/A"}
def intraday_analyzer_node(state: AgentState):
    if state.get("error"):
        return state
        
    symbol = state.get("symbol")
    investment = state.get("investment_amount", 10000.0)
    min_profit_pct = state.get("min_greedy_profit", 1.0)
    
    # 1. Fetch Intraday Data (5m) via MCP
    # We call get_stock_info with interval="5"
    data = call_mcp_tool("get_stock_info", {"symbol": symbol, "interval": "5"})
    if "error" in data:
        return {"error": data.get("error")}
        
    # 2. Analyze via SLM
    current_price = data.get("current_price", 0)
    tv_recent = extract_recent_history(data.get("tv_history", "{}"), days=1) # 1 day of 5m bars
    
    prompt = f"""
    You are an Intraday Trading expert for the Indian Market. 
    Symbol: {symbol}
    Current Price: ₹{current_price}
    Investment Amount: ₹{investment}
    Target Profit: {min_profit_pct}%
    
    Recent 5-minute OHLCV Data: {tv_recent}
    
    Your task:
    1. Analyze the momentum and trend from the last few 5-minute bars.
    2. Calculate the exact quantity to buy based on investment (Investment / Current Price).
    3. Determine a precise 'buy_entry' price (e.g. current or a slight dip).
    4. Determine a 'sell_exit' price that guarantees at least {min_profit_pct}% profit after entry.
    5. Provide a 'stop_loss' recommendation.
    6. Give a 'short_logic' explanation.
    
    Return a pure JSON object:
    {{
        "quantity": int,
        "buy_entry": "₹XXX.XX",
        "sell_exit": "₹XXX.XX",
        "stop_loss": "₹XXX.XX",
        "logic": "The reasoning based on 5m trend",
        "expected_profit": "₹XXX.XX"
    }}
    """
    
    try:
        llm = get_llm(state.get("llm_provider", "Ollama"))
        response = llm.invoke([HumanMessage(content=prompt)])
        parsed = extract_json(response.content)
        if not parsed:
            parsed = {
                "quantity": int(investment / current_price) if current_price > 0 else 0,
                "buy_entry": f"₹{current_price}",
                "sell_exit": f"₹{current_price * (1 + min_profit_pct/100):.2f}",
                "stop_loss": f"₹{current_price * 0.99:.2f}",
                "logic": "Fallback logic: Scalping based on target percentage.",
                "expected_profit": f"₹{investment * (min_profit_pct/100):.2f}"
            }
            
        # Format for state
        advice = f"Intraday Strategy: Buy {parsed.get('quantity')} units at {parsed.get('buy_entry')}. Exit at {parsed.get('sell_exit')} with Stop Loss at {parsed.get('stop_loss')}. \nLogic: {parsed.get('logic')}"
        
        return {
            "intraday_data": data,
            "recommendation": "INTRADAY",
            "reasoning": parsed.get("logic"),
            "buy_target": parsed.get("buy_entry"),
            "sell_target": parsed.get("sell_exit"),
            "personalized_advice": advice,
            "profit_potential": parsed.get("expected_profit")
        }
    except Exception as e:
        return {"error": f"Intraday Analysis failed: {str(e)}"}

def feature_engine_node(state: AgentState):
    symbol = state.get("symbol")
    df = fetch_ohlcv(symbol)
    if df.empty:
        return {"error": "Could not fetch data for feature engine"}
    
    features = generate_features(df)
    return {"technical_indicators": features}

def regime_detection_node(state: AgentState):
    """
    Detects market regime: Bullish, Bearish, or Volatile.
    """
    tech = state.get("technical_indicators", {})
    rsi = tech.get("rsi", 50)
    trend = tech.get("trend", "sideways")
    
    if trend == "up" and rsi > 40:
        regime = "Bullish"
    elif trend == "down" and rsi < 60:
        regime = "Bearish"
    else:
        regime = "Volatile/Ranging"
        
    return {"market_mood": regime}

def execution_node(state: AgentState):
    """
    Automated execution node for paper trading simulation.
    Uses the recommendation to enter/exit trades.
    """
    symbol = state.get("symbol")
    rec = state.get("recommendation")
    
    session = SessionLocal()
    pos = session.query(Position).filter_by(symbol=symbol).first()
    
    if rec == "BUY" and not pos:
        # Simple rule: buy 100 shares if recommended and not holding
        execute_buy(symbol, 100, float(state.get("buy_target", 0).replace('₹','')), float(state.get("sell_target", 0).replace('₹','')))
    elif rec == "SELL" and pos:
        trade = session.query(Trade).filter_by(symbol=symbol, result=None).first()
        if trade:
            execute_sell(symbol, pos.quantity, trade.id)
            
    session.close()
    return {}

def alert_node(state: AgentState):
    """
    Checks if any alerts were triggered for the current symbol.
    """
    triggered = evaluate_alerts()
    # In a real app, this might send a notification
    return {"alerts_triggered": triggered}
