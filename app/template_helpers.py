"""
Centralized template helpers for HubPDF
"""
from fastapi.templating import Jinja2Templates
from app.services.i18n import get_translations

# Create centralized templates instance
templates = Jinja2Templates(directory="templates")

# Add simple translation function to templates
def t(key: str) -> str:
    """Simple translation function for templates - defaults to PT"""
    translations = get_translations("pt")
    return translations.get(key, key)

# Register global functions
templates.env.globals["t"] = t

# Helper function to get templates with context
def get_template_response(template_name: str, context: dict, locale: str = "pt"):
    """Get template response with proper translation context"""
    # Add translation function that respects locale
    def t_locale(key: str) -> str:
        translations = get_translations(locale)
        return translations.get(key, key)
    
    # Add to context
    context["t"] = t_locale
    return templates.TemplateResponse(template_name, context)

def price_brl(value: float) -> str:
    """Format price in Brazilian Real (BRL) format with comma as decimal separator"""
    # Avoid depending on locale/babel in MVP
    txt = f"{value:,.2f}"
    return "R$ " + txt.replace(",", "X").replace(".", ",").replace("X", ".")

# Register price function globally
templates.env.globals["price_brl"] = price_brl