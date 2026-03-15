import streamlit as st
import pandas as pd
import json
from agents.graph import trade_graph
from utils.storage import save_analysis, load_history
from utils.pdf_export import generate_pdf_report
from datetime import datetime

# --- Page Config ---
st.set_page_config(
    page_title="TradeGuard SLM | Agentic Trading Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom Style ---
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #1e2130;
        padding: 15px;
        border-radius: 10px;
    }
    .recommendation-box {
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
        font-size: 24px;
    }
    .buy { background-color: #006400; color: white; border: 2px solid #00ff00; }
    .hold { background-color: #8b8000; color: white; border: 2px solid #ffff00; }
    .sell { background-color: #8b0000; color: white; border: 2px solid #ff0000; }
    .advice-box {
        background-color: #262730;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #00d4ff;
    }
</style>
""", unsafe_allow_html=True)

# --- Sidebar ---
with st.sidebar:
    st.title("🛡️ TradeGuard SLM")
    st.markdown("---")
    risk_profile = st.selectbox(
        "Your Risk Profile",
        ["Conservative", "Moderate", "Aggressive"],
        index=1,
        help="Determines the cautiousness of the personalized advice."
    )
    st.info("Everything runs 100% locally on this machine using Ollama.")
    
    st.markdown("---")
    history = load_history()
    if history:
        st.subheader("📜 Recent Analyses")
        for item in history[:5]:
            st.markdown(f"**{item['symbol']}**: {item['recommendation']} ({item['timestamp']})")

# --- Tabs ---
tab1, tab2 = st.tabs(["🚀 New Analysis", "📊 History & Portfolio"])

with tab1:
    st.title("Indian Market Analyst")
    st.write("Enter an NSE stock symbol (e.g., RELIANCE.NS, INFEY.NS) or upload your portfolio.")
    
    col_input, col_upload = st.columns([1, 1])
    
    with col_input:
        symbol = st.text_input("Stock Symbol", placeholder="RELIANCE.NS").upper()
    
    with col_upload:
        portfolio_file = st.file_uploader("Upload Portfolio CSV", type=["csv"])
        if portfolio_file:
            st.success("Portfolio loaded! Analyze your holdings below.")

    if st.button("Analyze Now 🔍", type="primary"):
        if not symbol:
            st.warning("Please enter a stock symbol.")
        else:
            with st.spinner(f"Agent is analyzing {symbol}..."):
                # Run the Agentic Workflow
                initial_state = {
                    "symbol": symbol,
                    "risk_profile": risk_profile,
                    "errors": []
                }
                
                final_state = trade_graph.invoke(initial_state)
                
                if final_state.get("errors"):
                    st.error(f"Analysis failed: {final_state['errors'][-1]}")
                else:
                    # Save history
                    save_analysis(final_state)
                    
                    # Store in session state for PDF export
                    st.session_state["last_analysis"] = final_state
                    
                    # Display Results
                    info = final_state["stock_info"]
                    tech = final_state["technical_analysis"]
                    rec = final_state["recommendation"]
                    
                    # Row 1: Key Metrics
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Current Price", f"₹{info['current_price']:,}", f"{info['change_pct']:.2f}%")
                    m2.metric("RSI (14)", tech['rsi'], tech['rsi_signal'])
                    m3.metric("Trend", tech['trend'])
                    m4.metric("Risk Score", f"{final_state['risk_score']}/10")
                    
                    # Row 2: Recommendation & Reasoning
                    rec_class = "buy" if rec == "BUY" else "sell" if rec == "SELL" else "hold"
                    st.markdown(f'<div class="recommendation-box {rec_class}">{rec}</div>', unsafe_allow_html=True)
                    
                    col_reason, col_advice = st.columns([2, 1])
                    
                    with col_reason:
                        st.subheader("Why this recommendation?")
                        for bullet in final_state['reasoning']:
                            st.markdown(f"- {bullet}")
                    
                    with col_advice:
                        st.subheader("Today's Strategy")
                        st.markdown(f'<div class="advice-box">{final_state["personalized_advice"]}</div>', unsafe_allow_html=True)
                    
                    # Technical Detail Expanders
                    with st.expander("Detailed Technical Summary"):
                        st.json(tech)
                    
                    with st.expander("Market Sentiment Analysis"):
                        st.write(final_state.get("sentiment_analysis", "No detailed sentiment available."))
                        st.write(f"Sentiment Score: {final_state.get('sentiment_score', 0)}")
                    
                    # PDF Export
                    pdf_bytes = generate_pdf_report(final_state)
                    st.download_button(
                        label="📄 Export Analysis as PDF",
                        data=pdf_bytes,
                        file_name=f"TradeGuard_{symbol}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )

with tab2:
    st.header("Activity Log")
    history = load_history()
    if not history:
        st.write("No analysis history found.")
    else:
        df_history = pd.DataFrame(history)
        st.dataframe(df_history, use_container_width=True)
        
        if st.button("Clear History"):
            if os.path.exists("data/history.json"):
                os.remove("data/history.json")
                st.rerun()

# --- Footer ---
st.markdown("---")
st.caption("TradeGuard SLM v1.0 | Powered by Ollama & LangGraph | 100% Local Inference")
