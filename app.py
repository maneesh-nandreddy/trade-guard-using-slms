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
    with st.spinner("Initializing Agentic Workflow..."):
        workflow = build_graph()
        initial_state = {"symbol": symbol, "risk_profile": risk_profile}
        
        try:
            final_state = workflow.invoke(initial_state)
            
            if final_state.get("error"):
                st.error(f"Error: {final_state['error']}")
            else:
                st.success("Analysis Complete!")
                
                # Layout
                col1, col2, col3 = st.columns(3)
                with col1:
                    price = final_state['market_data'].get('current_price', 0)
                    st.metric("Current Price", f"₹{price:.2f}")
                with col2:
                    rsi = final_state['technical_indicators'].get('rsi', 0)
                    st.metric("RSI", f"{rsi:.2f}")
                with col3:
                    trend = final_state['technical_indicators'].get('trend', 'Unknown')
                    st.metric("Trend", trend.capitalize())
                
                st.markdown("### Recommendation")
                rec = final_state.get('recommendation', 'HOLD')
                rec_class = f"recommendation-{rec.lower()}"
                st.markdown(f"<div class='metric-card'><span class='{rec_class}'>{rec}</span><br/><br/>{final_state.get('reasoning')}</div>", unsafe_allow_html=True)
                
                st.markdown("### Personalized Advice")
                st.info(final_state.get('personalized_advice'))
                
                # Actions
                save_analysis(symbol, final_state)
                pdf_path = export_to_pdf(final_state)
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(label="Download PDF Report", data=pdf_file, file_name=f"{symbol}_report.pdf", mime="application/pdf")
                    
        except Exception as e:
            st.error(f"Workflow failed: {str(e)}")
