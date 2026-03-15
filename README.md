# TradeGuard SLM 🛡️

TradeGuard SLM is a 100% local, private, agentic trading assistant designed for retail traders in India. It uses Small Language Models (SLMs) to provide real-time stock analysis and personalized advice without your data ever leaving your machine.

## Features
- **Instant Insights**: Analyze NSE stocks in under 8 seconds.
- **Privacy First**: Fully local execution using Ollama and SLMs (phi3:mini).
- **Agentic Workflow**: Multi-step analysis using LangGraph (Data -> Technical -> Sentiment -> Recommendation).
- **Personalized Advice**: Tailors recommendations based on your risk profile (Conservative, Moderate, Aggressive).
- **Historical Tracking**: Keep track of your previous analyses locally.

## Multi-Step Agentic Workflow
1. **Data Fetcher Tool**: Retrieves live price, history, and news via `yfinance`.
2. **Technical Analyzer**: Calculates key indicators (RSI, MACD, Bollinger Bands) using `pandas_ta`.
3. **Sentiment Analyzer**: SLM interprets news headlines for market sentiment.
4. **Reasoning Engine**: Synthesizes data into a BUY/HOLD/SELL recommendation.
5. **Risk & Advice Node**: Provides personalized strategy based on user profile.

## Quick Start
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Prepare LLM**:
   Install [Ollama](https://ollama.com/) and pull the required model:
   ```bash
   ollama pull phi3:mini
   ```
3. **Run the App**:
   ```bash
   streamlit run app.py
   ```

## Development
- Uses **LangGraph** for structured agent control.
- **Streamlit** for the frontend dashboard.
- **pandas_ta** for technical indicator logic.
- **yfinance** for market data.

## Docker Support
Build and run the container:
```bash
docker build -t tradeguard-slm .
docker run -p 8501:8501 tradeguard-slm
```

---
*Disclaimer: This is for educational and informational purposes only. Trading stocks involves risk. Consult with a professional advisor before making investment decisions.*
