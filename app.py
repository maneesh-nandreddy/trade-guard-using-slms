import streamlit as st
from agents.graph import build_graph, build_intraday_graph
from agents.market_analyst import build_market_graph
from tools.market_scan import MARKET_CAP_SEGMENTS, get_market_summary, scan_segment
from utils.storage import save_analysis, load_history
from utils.pdf_export import export_to_pdf
from utils.portfolio import load_portfolio, add_stock, remove_stock
import pandas as pd

st.set_page_config(page_title="TradeGuard SLM", layout="wide", initial_sidebar_state="expanded")

# ──────────────────────────────────────────────────────────────
# SVG ICON LIBRARY  (Feather / Lucide style — 20×20 stroked)
# ──────────────────────────────────────────────────────────────
ICONS = {
    "shield":        '<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4F9BE8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',
    "settings":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>',
    "trending_up":   '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00C853" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"/><polyline points="17 6 23 6 23 12"/></svg>',
    "bar_chart":     '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F9BE8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>',
    "target":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFD600" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>',
    "briefcase":     '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>',
    "zap":           '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#FFD600" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>',
    "globe":         '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F9BE8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',
    "clock":         '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>',
    "check":         '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00C853" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    "alert":         '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#FFD600" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>',
    "dollar":        '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#00C853" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>',
    "list":          '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>',
    "pie_chart":     '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F9BE8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21.21 15.89A10 10 0 1 1 8 2.83"/><path d="M22 12A10 10 0 0 0 12 2v10z"/></svg>',
    "activity":      '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#4F9BE8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/></svg>',
    "search":        '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>',
    "arrow_up":      '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#00C853" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="19" x2="12" y2="5"/><polyline points="5 12 12 5 19 12"/></svg>',
    "arrow_down":    '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D50000" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><polyline points="19 12 12 19 5 12"/></svg>',
    "plus":          '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>',
    "trash":         '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#D50000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4h6v2"/></svg>',
    "cpu":           '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#9CA3AF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/></svg>',
}

def icon(name, label="", size="sm"):
    """Returns icon + optional label wrapped in an inline-flex row."""
    svg = ICONS.get(name, "")
    label_html = f'<span>{label}</span>' if label else ""
    return f'<span class="tg-icon-row">{svg}{label_html}</span>'

def section_header(icon_name, text, color="#E2E8F0"):
    """Renders a styled section header with an aligned SVG icon."""
    return st.markdown(
        f'<div class="tg-section-h" style="color:{color};">'
        f'{ICONS.get(icon_name,"")}'
        f'<span>{text}</span>'
        f'</div>',
        unsafe_allow_html=True
    )

# ──────────────────────────────────────────────────────────────
# Global CSS
# ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .stApp { background-color: #0E1117; color: #E2E8F0; }

    /* Cards */
    .tg-card {
        background: #1A1F2E;
        border: 1px solid #2D3748;
        border-radius: 10px;
        padding: 18px 22px;
        margin-bottom: 12px;
    }
    .tg-card-accent { border-left: 4px solid #4F9BE8; }
    .tg-card-profit { border-left: 4px solid #00C853; }

    /* Recommendations */
    .rec-buy  { color:#00C853; font-weight:700; font-size:26px; letter-spacing:1px; }
    .rec-sell { color:#D50000; font-weight:700; font-size:26px; letter-spacing:1px; }
    .rec-hold { color:#FFD600; font-weight:700; font-size:26px; letter-spacing:1px; }

    /* Dividers */
    .tg-divider { border:none; border-top:1px solid #2D3748; margin:18px 0; }

    /* Segment badge */
    .seg-badge {
        display:inline-block;
        padding:2px 10px;
        border-radius:20px;
        font-size:11px;
        font-weight:600;
        letter-spacing:0.5px;
        text-transform:uppercase;
        margin-bottom:8px;
    }
    .seg-large { background:#1E3A5F; color:#4F9BE8; }
    .seg-mid   { background:#3D2B00; color:#FFB300; }
    .seg-small { background:#1B3A2A; color:#00C853; }

    /* Mood banner */
    .mood-bullish { background:#0D2E1A; border:1px solid #00C853; border-radius:8px; padding:14px 18px; }
    .mood-bearish { background:#2E0D0D; border:1px solid #D50000; border-radius:8px; padding:14px 18px; }
    .mood-neutral { background:#2E2A0D; border:1px solid #FFD600; border-radius:8px; padding:14px 18px; }

    /* Profit indicator */
    .profit-bar {
        background:#0D2E1A;
        border-left:3px solid #00C853;
        border-radius:6px;
        padding:10px 16px;
        font-size:0.9rem;
        color:#E2E8F0;
        margin-bottom:16px;
        display:flex;
        align-items:center;
        gap:10px;
    }

    /* History items */
    .hist-item {
        padding:6px 0;
        border-bottom:1px solid #2D3748;
        font-size:0.85rem;
        color:#9CA3AF;
    }

    /* Global SVG vertical alignment fix */
    svg { display:inline-block; vertical-align:-0.15em; flex-shrink:0; }

    .tg-icon-row {
        display:inline-flex;
        align-items:center;
        gap:7px;
        line-height:1.4;
    }
    .tg-section-h {
        display:flex;
        align-items:center;
        gap:8px;
        font-size:1rem;
        font-weight:600;
        color:#E2E8F0;
        margin:14px 0 6px;
        line-height:1.4;
    }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────
st.markdown(
    f'<div style="display:flex;align-items:center;gap:12px;padding-bottom:4px;">'
    f'{ICONS["shield"]}'
    f'<span style="font-size:1.7rem;font-weight:700;color:#E2E8F0;">TradeGuard SLM</span>'
    f'</div>',
    unsafe_allow_html=True
)
st.caption("Private · Agentic · SLM-Powered Trading Intelligence for Indian Retail Investors")
st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'{icon("settings", "Configuration")}', unsafe_allow_html=True)
    st.markdown("")

    risk_profile = st.selectbox("Risk Profile", ["Conservative", "Moderate", "Aggressive"], index=1)
    llm_provider = st.selectbox(
        "Inference Engine",
        ["Ollama", "Groq"],
        index=0,
        help="Ollama runs fully offline. Groq is a high-speed cloud API."
    )

    if llm_provider == "Groq":
        import os
        if not os.getenv("GROQ_API_KEY"):
            st.markdown(
                f'<div class="tg-card" style="border-left:3px solid #FFD600;padding:10px 14px;">'
                f'{ICONS["alert"]} <span style="font-size:0.85rem;color:#FFD600;">&nbsp;GROQ_API_KEY not set in .env</span>'
                f'</div>',
                unsafe_allow_html=True
            )

    st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
    st.markdown(f'{icon("clock", "Recent Analyses")}', unsafe_allow_html=True)
    st.markdown("")

    history = load_history()
    if history:
        for item in reversed(history[-5:]):
            rec_color = {"BUY": "#00C853", "SELL": "#D50000", "HOLD": "#FFD600"}.get(item.get("recommendation",""), "#9CA3AF")
            st.markdown(
                f'<div class="hist-item">'
                f'<strong style="color:#E2E8F0;">{item["symbol"]}</strong>'
                f' &nbsp;<span style="color:{rec_color};font-weight:600;">{item["recommendation"]}</span>'
                f' &nbsp;<span>@ ₹{item["price"]:.2f}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
    else:
        st.caption("No analysis history yet.")

# ──────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "Stock Analyzer",
    "Portfolio Manager",
    "Intraday Insights",
    "Market Discoverer"
])

# ══════════════════════════════════════════════════════════════
# TAB 1 · Stock Analyzer
# ══════════════════════════════════════════════════════════════
with tab1:
    st.markdown(f'{icon("activity")} &nbsp;<strong style="font-size:1.15rem;">Stock Analyzer</strong>', unsafe_allow_html=True)
    st.caption("Full agentic analysis — sentiment, technicals, recommendation & risk advice.")
    st.markdown("")

    symbol = st.text_input("NSE Symbol", "RELIANCE.NS", placeholder="e.g. RELIANCE.NS · TCS.NS · INFY.NS")

    if st.button("Run Analysis", type="primary"):
        with st.status("Initializing workflow…", expanded=True) as status:
            workflow = build_graph()
            initial_state = {"symbol": symbol, "risk_profile": risk_profile, "llm_provider": llm_provider}

            chart_placeholder       = st.empty()
            metrics_placeholder     = st.empty()
            targets_placeholder     = st.empty()
            recommendation_placeholder = st.empty()
            fluctuation_placeholder = st.empty()
            advice_placeholder      = st.empty()
            actions_placeholder     = st.empty()

            try:
                final_state = initial_state
                for state_update in workflow.stream(initial_state):

                    if "data_fetcher" in state_update:
                        status.write(f'{icon("check")} Market data fetched.', unsafe_allow_html=True)
                        final_state.update(state_update["data_fetcher"])

                        market_data = final_state.get('market_data', {})
                        tv_history_json = market_data.get('tv_history', '{}')
                        try:
                            import json
                            hist_dict = json.loads(tv_history_json)
                            if hist_dict and "Close" in hist_dict:
                                with chart_placeholder.container():
                                    section_header("bar_chart", "Price History — Close")
                                    df_chart = pd.DataFrame(hist_dict)
                                    df_chart.index = pd.to_datetime(df_chart.index)
                                    st.line_chart(df_chart[['Close']])
                        except Exception: pass

                        with metrics_placeholder.container():
                            col1, col2, col3 = st.columns(3)
                            price = market_data.get('current_price', 0)
                            rsi   = final_state['technical_indicators'].get('rsi', 0)
                            trend = final_state['technical_indicators'].get('trend', 'Unknown')
                            col1.metric("Current Price", f"₹{price:.2f}")
                            col2.metric("RSI (14)", f"{rsi:.2f}")
                            col3.metric("Trend", trend.capitalize())

                    elif "sentiment_analyzer" in state_update:
                        status.write("News sentiment analyzed.")
                        final_state.update(state_update["sentiment_analyzer"])

                    elif "recommendation" in state_update:
                        status.write("Recommendation generated.")
                        final_state.update(state_update["recommendation"])

                        with recommendation_placeholder.container():
                            section_header("target", "Recommendation")
                            rec = final_state.get('recommendation', 'HOLD')
                            rec_class = f"rec-{rec.lower()}"
                            st.markdown(
                                f'<div class="tg-card tg-card-accent">'
                                f'<span class="{rec_class}">{rec}</span>'
                                f'<p style="margin-top:10px;color:#CBD5E0;line-height:1.6;">{final_state.get("reasoning","")}</p>'
                                f'</div>',
                                unsafe_allow_html=True
                            )

                        with targets_placeholder.container():
                            section_header("trending_up", "Price Targets")
                            tcol1, tcol2 = st.columns(2)
                            tcol1.info(f"**Entry (Dip Buy):** {final_state.get('buy_target', 'N/A')}")
                            tcol2.info(f"**Exit (Profit Target):** {final_state.get('sell_target', 'N/A')}")

                        with fluctuation_placeholder.container():
                            section_header("activity", "Volatility & Fluctuation")
                            st.info(final_state.get('fluctuation_analysis', 'No data available.'))

                    elif "risk_advice" in state_update:
                        status.write("Personalized advice ready.")
                        final_state.update(state_update["risk_advice"])

                        with advice_placeholder.container():
                            section_header("shield", "Personalized Advice")
                            st.info(final_state.get('personalized_advice', 'No advice available.'))

                if final_state.get("error"):
                    status.update(label=f"Error: {final_state['error']}", state="error", expanded=True)
                    st.error(f"Error: {final_state['error']}")
                else:
                    status.update(label="Analysis complete.", state="complete", expanded=False)
                    st.success("Analysis complete.")
                    save_analysis(symbol, final_state)
                    pdf_path = export_to_pdf(final_state)
                    with actions_placeholder.container():
                        with open(pdf_path, "rb") as pdf_file:
                            st.download_button(
                                label="Download PDF Report",
                                data=pdf_file,
                                file_name=f"{symbol}_report.pdf",
                                mime="application/pdf"
                            )

            except Exception as e:
                status.update(label=f"Workflow error: {str(e)}", state="error", expanded=True)
                st.error(f"Workflow error: {str(e)}")

# ══════════════════════════════════════════════════════════════
# TAB 2 · Portfolio Manager
# ══════════════════════════════════════════════════════════════
with tab2:
    st.markdown(f'{icon("briefcase")} &nbsp;<strong style="font-size:1.15rem;">Portfolio Manager</strong>', unsafe_allow_html=True)
    st.caption("Track your holdings and run an AI-powered audit across your entire portfolio.")
    st.markdown("")

    col_add, col_list = st.columns([1, 2])

    with col_add:
        section_header("plus", "Add Position")
        new_symbol = st.text_input("Symbol (e.g., RELIANCE.NS)", key="add_sym").upper()
        qty   = st.number_input("Quantity", min_value=1, value=1)
        avg_p = st.number_input("Avg. Purchase Price (₹)", min_value=0.0, value=0.0)
        if st.button("Add to Portfolio"):
            add_stock(new_symbol, qty, avg_p)
            st.success(f"{new_symbol} added.")
            st.rerun()

    with col_list:
        section_header("pie_chart", "Current Holdings")
        portfolio = load_portfolio()
        if portfolio:
            df_portfolio = pd.DataFrame(portfolio)
            st.dataframe(df_portfolio, hide_index=True, use_container_width=True)

            st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
            if st.button("Run Full Portfolio Audit", type="primary"):
                audit_results = []
                with st.status("Auditing portfolio…", expanded=True) as audit_status:
                    workflow = build_graph()
                    for item in portfolio:
                        sym = item['symbol']
                        audit_status.write(f"{icon('search')} Analyzing {sym}…", unsafe_allow_html=True)
                        try:
                            result = workflow.invoke({"symbol": sym, "risk_profile": risk_profile, "llm_provider": llm_provider})
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
                            audit_status.write(f"Failed: {sym} — {str(e)}")

                    if audit_results:
                        from utils.storage import save_portfolio_report
                        save_portfolio_report(audit_results)
                        audit_status.update(label="Audit complete.", state="complete", expanded=False)
                        st.success("Portfolio audit saved.")

                        section_header("list", "Audit Results")
                        for res in audit_results:
                            rec_color = {"BUY":"#00C853","SELL":"#D50000","HOLD":"#FFD600"}.get(res["recommendation"],"#9CA3AF")
                            with st.expander(f"{res['symbol']}  ·  {res['recommendation']}"):
                                c1, c2 = st.columns(2)
                                c1.write(f"**Avg. Cost:** ₹{res['avg_price']:.2f}")
                                c1.write(f"**Quantity:** {res['qty']}")
                                c2.info(f"**Profit Target:** {res['profit']}")
                                st.write(f"**Advice:** {res['advice']}")
                                st.success(f"**Averaging Plan:** {res['averaging']}")

            st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
            section_header("trash", "Remove Position")
            rm_symbol = st.selectbox("Select position to remove", [i['symbol'] for i in portfolio])
            if st.button("Remove Selected"):
                remove_stock(rm_symbol)
                st.warning(f"{rm_symbol} removed.")
                st.rerun()
        else:
            st.info("Your portfolio is empty. Add positions using the panel on the left.")

        from utils.storage import load_portfolio_reports
        reports = load_portfolio_reports()
        if reports:
            st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
            section_header("clock", "Audit History")
            for rep in reversed(reports[-3:]):
                with st.expander(f"Audit — {rep['timestamp'][:16].replace('T', ' ')}"):
                    for entry in rep['report']:
                        st.write(f"**{entry['symbol']}**: {entry['recommendation']} · {entry['profit']}")

# ══════════════════════════════════════════════════════════════
# TAB 3 · Intraday Insights
# ══════════════════════════════════════════════════════════════
with tab3:
    st.markdown(f'{icon("zap")} &nbsp;<strong style="font-size:1.15rem;">Intraday Insights</strong>', unsafe_allow_html=True)
    st.caption("5-minute momentum analysis with precise entry, exit and stop-loss targets.")
    st.markdown("")

    icol1, icol2, icol3 = st.columns(3)
    intraday_symbol = icol1.text_input("NSE Symbol", "RELIANCE.NS", key="intraday_sym")
    investment      = icol2.number_input("Capital to Deploy (₹)", min_value=100.0, value=10000.0, step=500.0)
    greedy_profit   = icol3.slider("Target Profit (%)", 0.5, 5.0, 1.5, 0.1)

    expected_profit_val = investment * (greedy_profit / 100)
    st.markdown(
        f'<div class="profit-bar">'
        f'{ICONS["dollar"]}'
        f'<span>Target Return &nbsp;·&nbsp; <strong>₹{expected_profit_val:,.2f}</strong>'
        f' &nbsp;<span style="color:#9CA3AF;">({greedy_profit}% on ₹{investment:,.0f})</span></span>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.button("Run Intraday Analysis", type="primary"):
        with st.status("Analyzing 5-minute momentum…", expanded=True) as status:
            workflow = build_intraday_graph()
            initial_state = {
                "symbol": intraday_symbol,
                "investment_amount": investment,
                "min_greedy_profit": greedy_profit,
                "llm_provider": llm_provider
            }

            try:
                final_state = workflow.invoke(initial_state)

                if final_state.get("error"):
                    status.update(label=f"Error: {final_state['error']}", state="error", expanded=True)
                else:
                    status.update(label="Intraday analysis complete.", state="complete", expanded=False)

                    section_header("trending_up", "Entry & Exit Strategy")
                    rcol1, rcol2, rcol3 = st.columns(3)
                    rcol1.metric("Entry Price",     final_state.get('buy_target', 'N/A'))
                    rcol2.metric("Exit Target",     final_state.get('sell_target', 'N/A'))
                    rcol3.metric("Expected Return", final_state.get('profit_potential', 'N/A'))

                    st.info(final_state.get('personalized_advice', 'No advice available.'))

                    intraday_data = final_state.get('intraday_data', {})
                    tv_hist_json  = intraday_data.get('tv_history', '{}')
                    try:
                        import json
                        hist_dict = json.loads(tv_hist_json)
                        if hist_dict and "Close" in hist_dict:
                            section_header("activity", "5-Minute Price Action")
                            df_chart = pd.DataFrame(hist_dict)
                            df_chart.index = pd.to_datetime(df_chart.index)
                            st.line_chart(df_chart[['Close']])
                    except Exception: pass

            except Exception as e:
                status.update(label=f"Workflow error: {str(e)}", state="error", expanded=True)
                st.error(f"Workflow error: {str(e)}")

# ══════════════════════════════════════════════════════════════
# TAB 4 · Market Discoverer
# ══════════════════════════════════════════════════════════════
with tab4:
    st.markdown(f'{icon("globe")} &nbsp;<strong style="font-size:1.15rem;">Market Discoverer</strong>', unsafe_allow_html=True)
    st.caption("Scan Large, Mid and Small Cap stocks across sectors. Surfaces oversold setups and momentum opportunities.")
    st.markdown("")

    if st.button("Scan Indian Market", type="primary"):
        with st.status("Fetching major indices…", expanded=True) as status:
            try:
                # Phase 1 — Indices
                indices = get_market_summary()
                status.write("Indices loaded: Nifty 50 · Nifty Bank · Nifty IT")

                if indices:
                    section_header("bar_chart", "Market Indices")
                    dcols = st.columns(len(indices))
                    for i, (idx_name, idx_data) in enumerate(indices.items()):
                        if isinstance(idx_data, dict):
                            delta_color = "normal" if idx_data['change_pct'] >= 0 else "inverse"
                            dcols[i].metric(idx_name, f"₹{idx_data['price']:,}", f"{idx_data['change_pct']}%", delta_color=delta_color)

                # Phase 2 — Segment scans
                st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
                all_scanned = []

                seg_badge = {
                    "Large Cap": ("seg-large", "Large Cap"),
                    "Mid Cap":   ("seg-mid",   "Mid Cap"),
                    "Small Cap": ("seg-small",  "Small Cap"),
                }

                for seg_name in MARKET_CAP_SEGMENTS:
                    status.write(f"Scanning {seg_name} universe…")
                    seg_result = scan_segment(seg_name)
                    seg_stocks = seg_result.get("stocks", [])
                    all_scanned.extend(seg_stocks)

                    if seg_stocks:
                        sectors_covered = list({s['sector'] for s in seg_stocks})
                        status.write(f"  {len(seg_stocks)} stocks · Sectors: {', '.join(sectors_covered)}")

                        oversold = [s for s in seg_stocks if s.get('rsi') and s['rsi'] < 35]
                        momentum = [s for s in seg_stocks if s.get('change_pct') and s['change_pct'] > 1.5]
                        if oversold:
                            status.write(f"  Oversold (RSI < 35): {', '.join(s['symbol'] for s in oversold[:3])}")
                        if momentum:
                            status.write(f"  Strong Momentum (> +1.5%): {', '.join(s['symbol'] for s in momentum[:3])}")

                # Phase 3 — AI analysis
                status.write(f"Running {llm_provider} analysis across {len(all_scanned)} stocks…")
                from agents.market_analyst import market_analyst_node
                import json
                result = market_analyst_node({
                    "indices": indices,
                    "scanned_stocks": all_scanned,
                    "llm_provider": llm_provider
                })

                if result.get("error"):
                    status.update(label=f"Analysis error: {result['error']}", state="error", expanded=True)
                else:
                    status.update(label="Scan complete.", state="complete", expanded=False)

                    # Mood Card
                    mood = result.get('market_mood', 'Neutral')
                    mood_class  = f"mood-{mood.lower()}"
                    mood_colors = {"Bullish": "#00C853", "Bearish": "#D50000", "Neutral": "#FFD600"}
                    mood_icons  = {
                        "Bullish": ICONS["trending_up"],
                        "Bearish": ICONS["arrow_down"],
                        "Neutral": ICONS["activity"]
                    }
                    st.markdown(
                        f'<div class="{mood_class}" style="display:flex;align-items:flex-start;gap:12px;">'
                        f'<span style="margin-top:2px;">{mood_icons.get(mood, "")}</span>'
                        f'<div>'
                        f'<span style="color:{mood_colors.get(mood,"#fff")};font-weight:700;font-size:1.1rem;">Market Mood: {mood}</span>'
                        f'<p style="margin:6px 0 0;color:#CBD5E0;font-size:0.9rem;line-height:1.6;">{result.get("reasoning","")}</p>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )

                    st.markdown('<hr class="tg-divider">', unsafe_allow_html=True)
                    section_header("target", "Recommended Watchlist")
                    suggestions = result.get("top_suggestions", [])

                    if suggestions:
                        seg_groups = {"Large Cap": [], "Mid Cap": [], "Small Cap": [], "Other": []}
                        for sug in suggestions:
                            key = sug.get("segment", "Other")
                            seg_groups.setdefault(key, []).append(sug)

                        for seg_label, picks in seg_groups.items():
                            if not picks:
                                continue
                            badge_cls, badge_txt = seg_badge.get(seg_label, ("seg-large", seg_label))
                            st.markdown(
                                f'<span class="seg-badge {badge_cls}">{badge_txt}</span>',
                                unsafe_allow_html=True
                            )
                            for sug in picks:
                                with st.expander(f"{sug.get('symbol')}  ·  {sug.get('target_zone', 'Under Review')}"):
                                    st.markdown(f"**Rationale:** {sug.get('logic')}")
                                    st.markdown(f"**Target Zone:** {sug.get('target_zone')}")
                    else:
                        st.info("No strong setups identified today. Market may be in a consolidation phase.")

            except Exception as e:
                status.update(label=f"Scan error: {str(e)}", state="error", expanded=True)
                st.error(f"Scan error: {str(e)}")
