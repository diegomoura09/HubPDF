"""
Internationalization service for HubPDF
"""
import json
import os
from typing import Dict, Any
from fastapi import Request

# Cache for translations
_translations_cache: Dict[str, Dict[str, Any]] = {}

def load_translations(locale: str) -> Dict[str, Any]:
    """Load translations from JSON file"""
    if locale in _translations_cache:
        return _translations_cache[locale]
    
    translations_file = f"locales/{locale}.json"
    if os.path.exists(translations_file):
        with open(translations_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
            _translations_cache[locale] = translations
            return translations
    
    # Fallback to Portuguese if locale not found
    if locale != "pt":
        return load_translations("pt")
    
    return {}

def get_translations(locale: str = "pt") -> Dict[str, Any]:
    """Get translations for a specific locale"""
    return load_translations(locale)

def get_user_locale(request: Request) -> str:
    """Get user's preferred locale from cookie or default to PT-BR"""
    if request:
        # Check for language cookie
        locale = request.cookies.get("language", "pt")
        # Validate locale
        if locale in ["pt", "en"]:
            return locale
    
    return "pt"  # Default to Portuguese

def set_user_locale(response, locale: str):
    """Set user's locale in cookie"""
    if locale in ["pt", "en"]:
        response.set_cookie(
            "language",
            locale,
            max_age=30 * 24 * 60 * 60,  # 30 days
            httponly=True,
            secure=True,
            samesite="strict"
        )

def translate(key: str, locale: str = "pt", **kwargs) -> str:
    """Translate a key to the specified locale with optional formatting"""
    translations = get_translations(locale)
    text = translations.get(key, key)
    
    # Simple string formatting
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Ignore missing format keys
    
    return text

def get_available_locales() -> list:
    """Get list of available locales"""
    locales = []
    for filename in os.listdir("locales"):
        if filename.endswith(".json"):
            locale = filename[:-5]  # Remove .json extension
            locales.append(locale)
    return sorted(locales)
