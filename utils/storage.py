import json
import os
from datetime import datetime
from typing import List, Dict, Any

HISTORY_FILE = "data/history.json"

def save_analysis(state: Dict[str, Any]):
    """
    Saves a completed analysis state to a local JSON file.
    """
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    
    history = []
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []
    
    # Prepare clean record
    record = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": state.get("symbol"),
        "name": state.get("stock_info", {}).get("name"),
        "price": state.get("stock_info", {}).get("current_price"),
        "recommendation": state.get("recommendation"),
        "risk_score": state.get("risk_score"),
        "sentiment_score": state.get("sentiment_score"),
        "risk_profile": state.get("risk_profile")
    }
    
    history.insert(0, record) # Most recent first
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def load_history() -> List[Dict[str, Any]]:
    """
    Loads analysis history from the local JSON file.
    """
    if not os.path.exists(HISTORY_FILE):
        return []
    
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
