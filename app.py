import streamlit as st
from agents.graph import build_graph
from utils.storage import save_analysis, load_history
from utils.pdf_export import export_to_pdf
import pandas as pd

st.set_page_config(page_title="TradeGuard SLM", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for dark mode trading aesthetic
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    .metric-card {
        background-color: #1E2329;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .recommendation-buy { color: #00C853; font-weight: bold; font-size: 24px; }
    .recommendation-sell { color: #D50000; font-weight: bold; font-size: 24px; }
    .recommendation-hold { color: #FFD600; font-weight: bold; font-size: 24px; }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ TradeGuard SLM")
st.markdown("100% Local, Private, SLM-Powered Agentic Trading Assistant")

with st.sidebar:
    st.header("Settings")
    risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=1)
    st.markdown("---")
    st.subheader("History")
    history = load_history()
    if history:
        for idx, item in enumerate(reversed(history[-5:])):
            st.write(f"**{item['symbol']}**: {item['recommendation']} @ ₹{item['price']:.2f}")
    else:
        st.write("No history available.")

symbol = st.text_input("Enter NSE Stock Symbol (e.g., RELIANCE.NS)", "RELIANCE.NS")

if st.button("Analyze Now", type="primary"):
    with st.status("Initializing Agentic Workflow...", expanded=True) as status:
        workflow = build_graph()
        initial_state = {"symbol": symbol, "risk_profile": risk_profile}
        
        # UI Placeholders for progressive rendering
        chart_placeholder = st.empty()
        metrics_placeholder = st.empty()
        targets_placeholder = st.empty()
        recommendation_placeholder = st.empty()
        fluctuation_placeholder = st.empty()
        advice_placeholder = st.empty()
        actions_placeholder = st.empty()
        
        try:
            final_state = initial_state
            for state_update in workflow.stream(initial_state):
                if "data_fetcher" in state_update:
                    status.write("✅ Fetched market data and technical indicators.")
                    final_state.update(state_update["data_fetcher"])
                    
                    # Render chart immediately
                    market_data = final_state.get('market_data', {})
                    tv_history_json = market_data.get('tv_history', '{}')
                    try:
                        import json
                        hist_dict = json.loads(tv_history_json)
                        if hist_dict and "Close" in hist_dict:
                            with chart_placeholder.container():
                                st.markdown("### Stock Price History (Close)")
                                df_chart = pd.DataFrame(hist_dict)
                                df_chart.index = pd.to_datetime(df_chart.index)
                                st.line_chart(df_chart[['Close']])
                    except Exception: pass
                    
                    # Render metrics immediately
                    with metrics_placeholder.container():
                        col1, col2, col3 = st.columns(3)
                        price = market_data.get('current_price', 0)
                        rsi = final_state['technical_indicators'].get('rsi', 0)
                        trend = final_state['technical_indicators'].get('trend', 'Unknown')
                        col1.metric("Current Price", f"₹{price:.2f}")
                        col2.metric("RSI", f"{rsi:.2f}")
                        col3.metric("Trend", trend.capitalize())
                        
                elif "sentiment_analyzer" in state_update:
                    status.write("✅ Analyzed recent news and market sentiment.")
                    final_state.update(state_update["sentiment_analyzer"])
                    
                elif "recommendation" in state_update:
                    status.write("✅ SLM generated recommendation and targeted insights.")
                    final_state.update(state_update["recommendation"])
                    
                    # Render recommendation blocks immediately
                    with recommendation_placeholder.container():
                        st.markdown("### Recommendation")
                        rec = final_state.get('recommendation', 'HOLD')
                        rec_class = f"recommendation-{rec.lower()}"
                        st.markdown(f"<div class='metric-card'><span class='{rec_class}'>{rec}</span><br/><br/>{final_state.get('reasoning')}</div>", unsafe_allow_html=True)
                    
                    # Render Price Targets immediately
                    with targets_placeholder.container():
                        st.markdown("### Key Price Targets")
                        tcol1, tcol2 = st.columns(2)
                        tcol1.info(f"**Buy Target (Dip):** {final_state.get('buy_target', 'N/A')}")
                        tcol2.info(f"**Sell Target (Profit):** {final_state.get('sell_target', 'N/A')}")
                        
                    # Render fluctuation block immediately
                    with fluctuation_placeholder.container():
                        st.markdown("### Fluctuation Analysis")
                        st.info(final_state.get('fluctuation_analysis', 'No fluctuation analysis available.'))
                        
                elif "risk_advice" in state_update:
                    status.write("✅ Tailored personalized risk advice.")
                    final_state.update(state_update["risk_advice"])
                    
                    # Render advice immediately
                    with advice_placeholder.container():
                        st.markdown("### Personalized Advice")
                        st.info(final_state.get('personalized_advice', 'No advice available.'))
            
            if final_state.get("error"):
                status.update(label=f"Error: {final_state['error']}", state="error", expanded=True)
                st.error(f"Error: {final_state['error']}")
            else:
                status.update(label="Analysis Complete!", state="complete", expanded=False)
                st.success("Analysis Complete!")
                
                # Actions (save and pdf) at the very end
                save_analysis(symbol, final_state)
                pdf_path = export_to_pdf(final_state)
                with actions_placeholder.container():
                    with open(pdf_path, "rb") as pdf_file:
                        st.download_button(label="Download PDF Report", data=pdf_file, file_name=f"{symbol}_report.pdf", mime="application/pdf")
                    
        except Exception as e:
            status.update(label=f"Workflow failed: {str(e)}", state="error", expanded=True)
            st.error(f"Workflow failed: {str(e)}")
