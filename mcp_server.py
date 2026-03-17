from fastmcp import FastMCP
from tools.stock_data import fetch_stock_data, fetch_stock_fundamentals
from tools.technical_analysis import calculate_technical_indicators
from utils.portfolio import load_portfolio
import json

# Create an MCP server
mcp = FastMCP("TradeGuard")

@mcp.tool()
def get_stock_info(symbol: str) -> str:
    """Fetch live stock data and news for a given symbol."""
    data = fetch_stock_data(symbol)
    return json.dumps(data)

@mcp.tool()
def analyze_data(hist_json: str) -> str:
    """Perform technical analysis on historical price data."""
    results = calculate_technical_indicators(hist_json)
    return json.dumps(results)

@mcp.tool()
def analyze_fundamentals(symbol: str) -> str:
    """Fetch fundamental stock data like PE, Market Cap, and Business Summary."""
    results = fetch_stock_fundamentals(symbol)
    return json.dumps(results)

@mcp.resource("portfolio://current")
def get_portfolio() -> str:
    """Get the current user portfolio holdings."""
    portfolio = load_portfolio()
    return json.dumps(portfolio)

if __name__ == "__main__":
    mcp.run()
