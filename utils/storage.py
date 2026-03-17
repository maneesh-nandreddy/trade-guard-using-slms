import json
import os
from datetime import datetime

HISTORY_FILE = "trade_history.json"

def save_analysis(symbol: str, data: dict):
    history = load_history()
    record = {
        "timestamp": datetime.now().isoformat(),
        "symbol": symbol,
        "recommendation": data.get("recommendation", "N/A"),
        "reasoning": data.get("reasoning", ""),
        "price": data.get("market_data", {}).get("current_price", 0)
    }
    history.append(record)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
PORTFOLIO_REPORTS_FILE = "portfolio_reports.json"

def save_portfolio_report(report_data: list):
    reports = load_portfolio_reports()
    record = {
        "timestamp": datetime.now().isoformat(),
        "report": report_data
    }
    reports.append(record)
    with open(PORTFOLIO_REPORTS_FILE, "w") as f:
        json.dump(reports, f, indent=4)

def load_portfolio_reports() -> list:
    if not os.path.exists(PORTFOLIO_REPORTS_FILE):
        return []
    with open(PORTFOLIO_REPORTS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
