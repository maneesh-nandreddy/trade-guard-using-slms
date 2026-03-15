from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any

class TradeGuardPDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'TradeGuard SLM - Analysis Report', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Generated on {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 0, 'C')

def generate_pdf_report(state: Dict[str, Any], filename: str = "report.pdf"):
    """
    Generates a PDF report of the trade analysis.
    """
    pdf = TradeGuardPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    info = state.get("stock_info", {})
    technicals = state.get("technical_analysis", {})
    
    # Summary Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Summary: {info.get('symbol')} - {info.get('name')}", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Recommendation: {state.get('recommendation')}", ln=True)
    pdf.cell(0, 10, f"Risk Score: {state.get('risk_score')}/10", ln=True)
    pdf.cell(0, 10, f"Current Price: {info.get('currency')} {info.get('current_price')}", ln=True)
    pdf.ln(5)
    
    # Reasoning
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Reasoning & Logic:", ln=True)
    pdf.set_font("Arial", size=12)
    for bullet in state.get("reasoning", []):
        pdf.multi_cell(0, 10, f"- {bullet}")
    pdf.ln(5)
    
    # Technicals
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Technical Indicators:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"RSI: {technicals.get('rsi')} ({technicals.get('rsi_signal')})", ln=True)
    pdf.cell(0, 10, f"Trend: {technicals.get('trend')}", ln=True)
    pdf.cell(0, 10, f"EMA 50: {technicals.get('ema_50')} | EMA 200: {technicals.get('ema_200')}", ln=True)
    pdf.ln(5)
    
    # Personalized Advice
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Personalized Advice ({state.get('risk_profile')} Profile):", ln=True)
    pdf.set_font("Arial", 'I', 12)
    pdf.multi_cell(0, 10, state.get("personalized_advice", "N/A"))
    
    return pdf.output(dest='S').encode('latin-1') # Return bytes for streamlit download
