"""Configuration example file"""
from pathlib import Path
import os
from dotenv import load_dotenv

# Chemin racine du projet
ROOT = Path(__file__).resolve().parents[1]

# Charger les variables d'environnement
load_dotenv(ROOT / ".env", override=False)

# Scopes Gmail
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.modify",
]

# Configuration
CONFIG = {
    # Adresses email des newsletters à traiter
    "EMAIL_SOURCES": [
        "newsletter@example.com",
        "info@example.com",
    ],
    
    # Clés API (chargées depuis .env)
    "PERPLEXITY_API_KEY": os.getenv("PERPLEXITY_API_KEY"),
    "NOTION_API_KEY": os.getenv("NOTION_API_KEY"),
    "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID"),
    
    # Chemins
    "SYNTHESIS_DIR": ROOT / "data" / "output",
    "CREDENTIALS_DIR": ROOT / "credentials",
}
