"""
Centralized template helpers for HubPDF
"""
from fastapi.templating import Jinja2Templates
from app.services.i18n import get_translations, get_user_locale

def get_translation_function(locale: str):
    """Get translation function for templates"""
    translations = get_translations(locale)
    def t(key: str, default: str = None) -> str:
        return translations.get(key, default or key)
    return t

# Create centralized templates instance
templates = Jinja2Templates(directory="templates")

# Translation function for templates
def create_translate_function(locale: str = "pt"):
    """Create a translation function for specific locale"""
    translations = get_translations(locale)
    def translate(key: str, default: str = None) -> str:
        return translations.get(key, default or key)
    return translate

# Register global translation function with Portuguese as default
templates.env.globals["t"] = create_translate_function("pt")

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