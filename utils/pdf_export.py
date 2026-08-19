from fpdf import FPDF
from datetime import datetime
import os

def sanitize_text(text: str) -> str:
    """Replace problematic Unicode characters for FPDF."""
    if not isinstance(text, str):
        return str(text)
    replacements = {
        '’': "'", '‘': "'", '“': '"', '”': '"', '–': '-', '—': '-', '…': '...'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    # Encode to latin-1 and ignore errors to strip any remaining invalid chars
    # Ensure it's explicitly cast to str
    return str(text.encode('latin-1', 'ignore').decode('latin-1'))

def export_to_pdf(data: dict) -> str:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    symbol = sanitize_text(data.get("symbol", "UNKNOWN"))
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, txt=f"TradeSentinel Report: {symbol}", ln=True, align="C")
    
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True)
    pdf.ln(10)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Recommendation", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=sanitize_text(f"Action: {data.get('recommendation', 'N/A')}"), ln=True)
    pdf.ln(5)
    pdf.multi_cell(0, 10, txt=sanitize_text(f"Reasoning: {data.get('reasoning', 'N/A')}"))
    
    if "buy_target" in data and "sell_target" in data:
        pdf.ln(5)
        pdf.cell(200, 10, txt=sanitize_text(f"Buy Target (Dip): {data['buy_target']}"), ln=True)
        pdf.cell(200, 10, txt=sanitize_text(f"Sell Target (Profit): {data['sell_target']}"), ln=True)
    
    if "fluctuation_analysis" in data:
        pdf.ln(5)
        pdf.multi_cell(0, 10, txt=sanitize_text(f"Fluctuation Analysis: {data['fluctuation_analysis']}"))
        
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Personalized Advice", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=sanitize_text(str(data.get("personalized_advice", "N/A"))))
    pdf.ln(5)
    
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(200, 10, txt="Technical Data", ln=True)
    pdf.set_font("Arial", size=12)
    tech = data.get("technical_indicators", {})
    
    # Safely format floats
    def fmt_val(v):
        try:
            return f"{float(v):.2f}"
        except:
            return str(v)
            
    pdf.cell(200, 10, txt="RSI: " + sanitize_text(fmt_val(tech.get('rsi', 'N/A'))), ln=True)
    pdf.cell(200, 10, txt="MACD: " + sanitize_text(fmt_val(tech.get('macd', 'N/A'))), ln=True)
    pdf.cell(200, 10, txt="Trend: " + sanitize_text(str(tech.get('trend', 'N/A'))), ln=True)
    
    os.makedirs("exports", exist_ok=True)
    filename = f"exports/{symbol}_report.pdf"
    pdf.output(filename)
    return filename
