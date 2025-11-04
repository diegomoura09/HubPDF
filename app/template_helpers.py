"""
Centralized template helpers for HubPDF
"""
from fastapi.templating import Jinja2Templates

# Create centralized templates instance
templates = Jinja2Templates(directory="templates")

def price_brl(value: float) -> str:
    """Format price in Brazilian Real (BRL) format with comma as decimal separator"""
    # Avoid depending on locale/babel in MVP
    txt = f"{value:,.2f}"
    return "R$ " + txt.replace(",", "X").replace(".", ",").replace("X", ".")

# Register price function globally
templates.env.globals["price_brl"] = price_brl
