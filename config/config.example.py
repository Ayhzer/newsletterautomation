"""
Configuration pour Newsletter Automation
Copier ce fichier en config.py et remplir vos vraies valeurs
"""

# ==================== GMAIL ====================
# Scopes d'accès Gmail
SCOPES = [
    "https://www.googleapis.com/auth/gmail.modify"
]

# ==================== CONFIGURATION ====================
CONFIG = {
    # === Synthèse AI (cascade automatique : Perplexity → Gemini → Groq → brut) ===
    # Tier 1 — Perplexity AI (recommandé)
    "PERPLEXITY_API_KEY": "pplx-xxxxxxxxxxxxxxxxxxxxx",  # À remplir (optionnel)

    # Tier 2 — Google Gemini (fallback si Perplexity indisponible)
    "GEMINI_API_KEY": "AIzaxxxxxxxxxxxxxxxxxxxxx",  # À remplir (optionnel)

    # Tier 3 — Groq (fallback si Gemini indisponible)
    "GROQ_API_KEY": "gsk_xxxxxxxxxxxxxxxxxxxxx",  # À remplir (optionnel)

    # === Notion API ===
    "NOTION_TOKEN": "ntn_xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    "NOTION_PARENT_PAGE_ID": "xxxxxxxxxxxxxxxxxxxxx",  # À remplir

    # === Email de notification ===
    "NOTIFICATION_EMAIL": "votre.email@example.com",  # À remplir
}

# Note: Les EMAIL_SOURCES sont maintenant chargées depuis email_sources.txt
# Copiez email_sources.example.txt en email_sources.txt et modifiez-le selon vos besoins

