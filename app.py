import streamlit as st
from agents.graph import build_graph
from utils.storage import save_analysis, load_history
from utils.pdf_export import export_to_pdf
from utils.portfolio import load_portfolio, add_stock, remove_stock
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

# Tabs for separate features
tab1, tab2 = st.tabs(["Stock Analyzer", "Portfolio Manager"])

with tab1:
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
                        status.write("✅ Fetched market data and technical indicators via MCP Tool.")
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
                        status.write("✅ Tailored personalized risk advice using Portfolio context.")
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

with tab2:
    st.header("Portfolio Manager")
    
    col_add, col_list = st.columns([1, 2])
    
    with col_add:
        st.subheader("Add Holding")
        new_symbol = st.text_input("Symbol (e.g., RELIANCE.NS)", key="add_sym").upper()
        qty = st.number_input("Quantity", min_value=1, value=1)
        avg_p = st.number_input("Avg Purchase Price", min_value=0.0, value=0.0)
        if st.button("Add to Portfolio"):
            add_stock(new_symbol, qty, avg_p)
            st.success(f"Added {new_symbol} to portfolio.")
            st.rerun()
            
    with col_list:
        st.subheader("Current Holdings")
        portfolio = load_portfolio()
        if portfolio:
            df_portfolio = pd.DataFrame(portfolio)
            st.dataframe(df_portfolio, hide_index=True, use_container_width=True)
            
            st.markdown("---")
            if st.button("🚀 Run Full Portfolio Audit", type="primary"):
                audit_results = []
                with st.status("Auditing Full Portfolio...", expanded=True) as audit_status:
                    workflow = build_graph()
                    for item in portfolio:
                        sym = item['symbol']
                        audit_status.write(f"🔍 Analyzing {sym}...")
                        try:
                            # We can use invoke here since it's a batch process inside a loop
                            result = workflow.invoke({"symbol": sym, "risk_profile": risk_profile})
                            audit_results.append({
                                "symbol": sym,
                                "recommendation": result.get("recommendation"),
                                "avg_price": item['avg_price'],
                                "qty": item['quantity'],
                                "advice": result.get("personalized_advice"),
                                "averaging": result.get("averaging_strategy"),
                                "profit": result.get("profit_potential")
                            })
                        except Exception as e:
                            audit_status.write(f"❌ Failed to analyze {sym}: {str(e)}")
                    
                    if audit_results:
                        from utils.storage import save_portfolio_report
                        save_portfolio_report(audit_results)
                        audit_status.update(label="Full Audit Complete!", state="complete", expanded=False)
                        st.success("Portfolio Audit Saved!")
                        
                        st.subheader("Latest Audit Deep Dive")
                        for res in audit_results:
                            with st.expander(f"📊 {res['symbol']} - {res['recommendation']}"):
                                c1, c2 = st.columns(2)
                                c1.write(f"**Current Avg:** ₹{res['avg_price']:.2f}")
                                c1.write(f"**Quantity:** {res['qty']}")
                                c2.info(f"**Target Profit:** {res['profit']}")
                                st.write(f"**Advice:** {res['advice']}")
                                st.success(f"**Averaging Plan:** {res['averaging']}")
            
            st.markdown("---")
            rm_symbol = st.selectbox("Select symbol to remove", [i['symbol'] for i in portfolio])
            if st.button("Remove Selected"):
                remove_stock(rm_symbol)
                st.warning(f"Removed {rm_symbol} from portfolio.")
                st.rerun()
        else:
            st.info("Your portfolio is currently empty.")

        # Show historical audits
        from utils.storage import load_portfolio_reports
        reports = load_portfolio_reports()
        if reports:
            st.markdown("---")
            st.subheader("📜 Historical Audit Logs")
            for rep in reversed(reports[-3:]):
                with st.expander(f"Audit from {rep['timestamp'][:16].replace('T', ' ')}"):
                    for entry in rep['report']:
                        st.write(f"**{entry['symbol']}**: {entry['recommendation']} - {entry['profit']}")
