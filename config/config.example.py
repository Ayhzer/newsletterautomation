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
    # Gmail - Adresses email des newsletters à traiter
    "EMAIL_SOURCES": [
        "newsletter@techmeme.com",
        "newsletter@update.insideevs.com",
        "dan@tldrnewsletter.com",
        "noreply@medium.com",
    ],
    
    # Perplexity AI API
    "PERPLEXITY_API_KEY": "pplx-xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    
    # Notion API
    "NOTION_TOKEN": "ntn_xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    "NOTION_PARENT_PAGE_ID": "xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    
    # NotebookLM API (optionnel - pour génération automatique de podcasts)
    "NOTEBOOKLM_API_KEY": "",  # À remplir si vous utilisez l'API NotebookLM
    
    # Email de notification
    "NOTIFICATION_EMAIL": "votre.email@example.com",  # À remplir
}

