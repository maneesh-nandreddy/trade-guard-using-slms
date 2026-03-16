from fpdf import FPDF
from datetime import datetime
import os

def export_to_pdf(data: dict) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    symbol = data.get("symbol", "UNKNOWN")
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"TradeGuard SLM Report: {symbol}", ln=True, align="C")
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Recommendation", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=f"Action: {data.get('recommendation', 'N/A')}")
    pdf.multi_cell(0, 10, txt=f"Reasoning: {data.get('reasoning', 'N/A')}")
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Personalized Advice", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=str(data.get("personalized_advice", "N/A")))
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Technical Data", ln=True)
    pdf.set_font("Arial", size=12)
    tech = data.get("technical_indicators", {})
    pdf.multi_cell(0, 10, txt=f"RSI: {tech.get('rsi', 'N/A')}")
    pdf.multi_cell(0, 10, txt=f"MACD: {tech.get('macd', 'N/A')}")
    pdf.multi_cell(0, 10, txt=f"Trend: {tech.get('trend', 'N/A')}")
    
    os.makedirs("exports", exist_ok=True)
    filename = f"exports/{symbol}_report.pdf"
    pdf.output(filename)
    return filename
