# Newsletter Automation

Script Python qui automatise la récupération de newsletters Gmail, génère des synthèses via Perplexity AI et crée des pages Notion.

## Fonctionnalités

- ✅ Récupération automatique des emails depuis Gmail
- ✅ Génération de synthèses intelligentes via l'API Perplexity
- ✅ Création automatique de pages Notion
- ✅ Sauvegarde locale des synthèses
- ✅ Marquage des emails traités
- ✅ Gestion robuste des erreurs avec retry automatique
- ✅ Chemins absolus (fonctionne partout)
- ✅ Configuration sécurisée (variables d'env)

## Structure du projet

```
newsletter-automation/
├─ src/
│  └─ newsletter_automation/
│     ├─ __init__.py
│     ├─ config.py              # Configuration (variables d'env)
│     ├─ newsletter_automation.py # Script principal
│     ├─ credentials.json       # OAuth Gmail (à créer)
│     └─ token.json             # Token Gmail (auto-généré)
├─ .env                         # À créer (copier .env.example)
├─ .env.example                 # Template configuration
├─ requirements.txt             # Dépendances Python
├─ validate.py                  # Script de validation
├─ test_perplexity.py          # Test connexion API Perplexity
├─ VERIFICATION_REPORT.md      # Rapport des corrections
├─ TROUBLESHOOTING_PERPLEXITY.md # Guide de dépannage
└─ README.md
```

## Installation

### 1. Cloner le dépôt

```bash
git clone https://github.com/Ayhzer/newsletterautomation.git
cd newsletterautomation
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration

#### a. Créer le fichier de configuration

```bash
# Copier le template
cp config/config.example.py config/config.py
```

#### b. Remplir les valeurs dans `config/config.py`

```python
CONFIG = {
    # Gmail - Sources newsletters
    "EMAIL_SOURCES": [
        "newsletter1@example.com",
        "newsletter2@example.com",
    ],
    
    # Perplexity API
    "PERPLEXITY_API_KEY": "pplx-xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    
    # Notion API
    "NOTION_TOKEN": "ntn_xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    "NOTION_PARENT_PAGE_ID": "xxxxxxxxxxxxxxxxxxxxx",  # À remplir
    
    # Email de notification
    "NOTIFICATION_EMAIL": "votre.email@example.com",  # À remplir
}
```

#### c. Configurer Gmail OAuth

1. Créer un projet dans [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API Gmail
3. Créer des identifiants OAuth 2.0 (type "Application de bureau")
4. Télécharger le fichier JSON et le placer à:
   ```
   src/newsletter_automation/credentials.json
   ```

### 5. Valider la configuration

```bash
# Vérifier tous les fichiers et dépendances
python validate.py

# Tester la connexion Perplexity API
python test_perplexity.py
```

## Utilisation

```bash
python src/newsletter_automation/newsletter_automation.py
```

Lors de la première exécution, une fenêtre de navigateur s'ouvrira pour autoriser l'accès à Gmail.

## Dépendances principales

- `google-auth-oauthlib` : Authentification Gmail OAuth 2.0
- `google-api-python-client` : API Gmail
- `requests` : Appels API Perplexity et Notion
- `notion-client` : Création de pages Notion
- `html2text` : Conversion HTML → Markdown
- `python-dotenv` : Gestion variables d'environnement

## Dépannage

### Erreur Perplexity API

Consultez [TROUBLESHOOTING_PERPLEXITY.md](TROUBLESHOOTING_PERPLEXITY.md) pour:
- Erreur 401 (authentification)
- Erreur 403 (permissions)
- Erreur 429 (limite de débit)
- Erreur 500 (serveur)
- Timeout de connexion

### Diagnostic

```bash
# Valider configuration et chemins
python validate.py

# Tester API Perplexity
python test_perplexity.py

# Voir le rapport complet des corrections
cat VERIFICATION_REPORT.md
```

## Améliorations récentes

- ✅ Chemins absolus pour tous les fichiers
- ✅ Configuration sécurisée (variables d'env)
- ✅ Retry automatique avec backoff exponentiel
- ✅ Gestion détaillée des erreurs API
- ✅ Validation de configuration au démarrage
- ✅ Scripts de test et diagnostic

## Sécurité

⚠️ **Important** : Ne jamais commiter les fichiers sensibles:
- `config/config.py` (contient les clés API)
- `src/newsletter_automation/credentials.json` (OAuth)
- `src/newsletter_automation/token.json` (Token Gmail)
- `src/newsletter_automation/syntheses/` (Synthèses générées)

Ces fichiers sont automatiquement ignorés par `.gitignore`.

Seul `config/config.example.py` est commité pour servir de template.

## Licence

MIT
