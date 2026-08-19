from tools.market_scan import get_market_summary, scan_top_stocks

def test_market_tools():
    print("Testing Market Summary...")
    summary = get_market_summary()
    print("Indices found:", list(summary.keys()))
    for k, v in summary.items():
        print(f"  {k}: {v}")

    print("\nTesting Sector Scan...")
    scan = scan_top_stocks()
    if "error" in scan:
        print("❌ Scan failed:", scan["error"])
    else:
        stocks = scan.get("stocks", [])
        print(f"✅ Found {len(stocks)} stocks across sectors.")
        for stock in stocks[:5]:
            print(f"  {stock['symbol']} ({stock['sector']}): ₹{stock['price']} | Change: {stock['change_pct']}% | RSI: {stock['rsi']}")

if __name__ == "__main__":
    test_market_tools()
