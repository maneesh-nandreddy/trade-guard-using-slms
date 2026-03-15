import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.curdir))

from tools.stock_data import fetch_stock_basic_info, fetch_stock_history, fetch_stock_news
from tools.technical_analysis import analyze_technical_indicators
from agents.graph import trade_graph

def test_workflow():
    print("🚀 Starting Local Workflow Test...")
    symbol = "RELIANCE.NS"
    
    print(f"\n1. Testing Data Fetcher for {symbol}...")
    info = fetch_stock_basic_info(symbol)
    if "error" in info:
        print(f"❌ Error: {info['error']}")
        return
    print(f"✅ Basic Info: {info['name']} @ ₹{info['current_price']}")
    
    print("\n2. Testing Technical Analysis...")
    history = fetch_stock_history(symbol)
    tech = analyze_technical_indicators(history)
    print(f"✅ Technicals: RSI={tech['rsi']}, Trend={tech['trend']}")
    
    print("\n3. Testing LangGraph State Machine (requires Ollama running phi3:mini)...")
    try:
        initial_state = {
            "symbol": symbol,
            "risk_profile": "Moderate",
            "errors": []
        }
        # Using a timeout or similar if possible, but basic invoke for now
        final_state = trade_graph.invoke(initial_state)
        
        if final_state.get("errors"):
            print(f"❌ Graph Errors: {final_state['errors']}")
        else:
            print(f"✅ Recommendation: {final_state['recommendation']}")
            print(f"✅ Risk Score: {final_state['risk_score']}")
            print(f"✅ Advice: {final_state['personalized_advice']}")
            print("\n🚀 Test Completed Successfully!")
    except Exception as e:
        print(f"❌ Agent Invocation Failed: {str(e)}")
        print("Note: Ensure 'ollama pull phi3:mini' has been run and Ollama is active.")

if __name__ == "__main__":
    test_workflow()
