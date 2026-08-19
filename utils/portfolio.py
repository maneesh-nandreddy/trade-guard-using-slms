import json
import os

PORTFOLIO_FILE = "portfolio.json"

def load_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        return []
    with open(PORTFOLIO_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def add_stock(symbol, quantity, avg_price):
    portfolio = load_portfolio()
    # Check if exists
    for item in portfolio:
        if item['symbol'] == symbol.upper():
            # Update avg price and quantity
            total_cost = (item['quantity'] * item['avg_price']) + (quantity * avg_price)
            item['quantity'] += quantity
            item['avg_price'] = total_cost / item['quantity']
            save_portfolio(portfolio)
            return
    
    portfolio.append({
        "symbol": symbol.upper(),
        "quantity": quantity,
        "avg_price": avg_price
    })
    save_portfolio(portfolio)

def remove_stock(symbol):
    portfolio = load_portfolio()
    portfolio = [item for item in portfolio if item['symbol'] != symbol.upper()]
    save_portfolio(portfolio)
