from fastmcp import FastMCP
from tools.stock_data import fetch_stock_data, fetch_stock_fundamentals, Interval
from tools.market_scan import get_market_summary, scan_top_stocks
from utils.portfolio import load_portfolio
from tools.technical_analysis import calculate_technical_indicators
import json

# Create an MCP server
mcp = FastMCP("TradeGuard")

@mcp.tool()
def get_stock_info(symbol: str, interval: str = "1D") -> str:
    """Fetch live stock data and news for a given symbol. Interval can be 1, 3, 5, 15, 30, 45, 1H, 2H, 3H, 4H, 1D, 1W, 1M."""
    # Map string interval to Interval enum
    interval_map = {i.value: i for i in Interval}
    selected_interval = interval_map.get(interval, Interval.in_daily)
    
    data = fetch_stock_data(symbol, interval=selected_interval)
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

@mcp.tool()
def get_market_insights() -> str:
    """Fetch broader Indian market indices performance."""
    insights = get_market_summary()
    return json.dumps(insights)

@mcp.tool()
def scan_markets() -> str:
    """Scan top Indian stocks for momentum and technical setups."""
    scan = scan_top_stocks()
    return json.dumps(scan)

if __name__ == "__main__":
    mcp.run()
