# Newsletter Automation

Script Python qui automatise la récupération de newsletters Gmail, génère des synthèses via Perplexity AI et crée des pages Notion.

## 🎯 Fonctionnalités

- ✅ **Récupération automatique** des emails depuis Gmail
- ✅ **Synthèses intelligentes** via l'API Perplexity (structurées et détaillées)
- ✅ **Création de pages Notion** automatiquement
- ✅ **Pièce jointe au mail** - Synthèse prête pour NotebookLM
- ✅ **Sauvegarde locale** des synthèses en `.txt`
- ✅ **Gestion intelligente des emails** - Jusqu'à 2 par source
- ✅ **Marquage automatique** et retrait de la boite de réception/notifications
- ✅ **Gestion robuste des erreurs** avec retry automatique
- ✅ **GitHub Actions ready** - Planification automatique
- ✅ **Configuration sécurisée** - Secrets GitHub ou env variables

## 📋 Structure du projet

```
newsletter-automation/
├─ src/
│  └─ newsletter_automation/
│     ├─ __init__.py
│     ├─ newsletter_automation.py  # Script principal
│     ├─ credentials.json          # OAuth Gmail (à créer)
│     └─ token.json                # Token Gmail (auto-généré)
├─ config/
│  └─ config.example.py            # Template configuration
├─ email_sources.example.txt       # Template sources email
├─ requirements.txt                # Dépendances Python
├─ README.md                       # Ce fichier
├─ INSTALLATION.md                 # Guide installation détaillé
├─ GITHUB_SECRETS.md               # Configuration secrets GitHub
├─ QUICKSTART.md                   # Démarrage rapide
└─ NOTEBOOKLM_SETUP.md            # Intégration NotebookLM
```

## ⚡ Démarrage rapide (5 min)

```bash
# 1. Cloner
git clone https://github.com/Ayhzer/newsletter-automation.git
cd newsletter-automation

# 2. Environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 3. Dépendances
pip install -r requirements.txt

# 4. Configuration
cp config/config.example.py config/config.py
cp email_sources.example.txt email_sources.txt
# Éditer les deux fichiers avec vos paramètres

# 5. Lancer
python src/newsletter_automation/newsletter_automation.py
```

> ℹ️ Pour un guide détaillé, voir [INSTALLATION.md](INSTALLATION.md) ou [QUICKSTART.md](QUICKSTART.md)

## 🔧 Configuration

### Configuration locale

**1. Fichier config.py:**
```bash
cp config/config.example.py config/config.py
```

Remplir dans `config/config.py`:
- `PERPLEXITY_API_KEY` - Clé API Perplexity
- `NOTION_TOKEN` - Token Notion
- `NOTION_PARENT_PAGE_ID` - ID page Notion
- `NOTIFICATION_EMAIL` - Email pour les notifications

**2. Fichier email_sources.txt:**
```bash
cp email_sources.example.txt email_sources.txt
```

Ajouter vos adresses email (une par ligne):
```
newsletter@example.com
newsletter2@example.com
```

**3. Gmail OAuth:**
1. Créer un projet dans [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API Gmail
3. Créer identifiants OAuth (type "Application de bureau")
4. Placer le JSON à: `src/newsletter_automation/credentials.json`

### Configuration GitHub Actions

Pour l'automatisation GitHub, voir [GITHUB_SECRETS.md](GITHUB_SECRETS.md) avec:
- Syntaxe exacte pour chaque secret
- Où obtenir les clés API
- Options d'authentification Gmail

## 📧 Dépendances principales

- `google-auth-oauthlib` - Authentification Gmail OAuth 2.0
- `google-api-python-client` - API Gmail
- `requests` - Appels API Perplexity et Notion
- `notion-client` - Création pages Notion
- `html2text` - Conversion HTML → Markdown

## 🚀 Utilisation

### Local

```bash
python src/newsletter_automation/newsletter_automation.py
```

À la première exécution, un navigateur s'ouvre pour autoriser l'accès Gmail.

### GitHub Actions (Automatisé)

Le workflow s'exécute automatiquement selon le planning configuré. Voir [GITHUB_SECRETS.md](GITHUB_SECRETS.md) pour configurer les secrets.

## 📊 Flux de travail

1. 📧 **Récupère** les 2 derniers emails de chaque source
2. 🤖 **Synthétise** avec Perplexity en sections structurées
3. 💾 **Sauvegarde** le fichier `.txt`
4. 📝 **Crée** une page Notion
5. 🏷️ **Marque** les emails:
   - ✅ Lu
   - 📂 Retrait INBOX
   - 📬 Retrait NOTIFICATIONS
   - 🏷️ Ajout du label "newletterinnotion"
6. 📨 **Envoie** notification email avec:
   - Lien Notion
   - **Fichier synthèse en pièce jointe** (drag & drop pour NotebookLM)
   - Instructions podcast

## 🎙️ NotebookLM Integration

La synthèse est automatiquement jointe au mail. Pour générer un podcast:

1. Ouvrez l'email de notification
2. Téléchargez la pièce jointe
3. Allez sur [NotebookLM](https://notebooklm.google.com)
4. Drag & drop le fichier ou copiez-collez son contenu
5. Cliquez "Audio Overview" pour générer le podcast

Voir [NOTEBOOKLM_SETUP.md](NOTEBOOKLM_SETUP.md) pour plus de détails.

## 📚 Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Guide d'installation complet
- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage en 5 minutes
- **[GITHUB_SECRETS.md](GITHUB_SECRETS.md)** - Configuration secrets GitHub
- **[NOTEBOOKLM_SETUP.md](NOTEBOOKLM_SETUP.md)** - Intégration NotebookLM

## 🔒 Sécurité

⚠️ **Important** - Ne jamais commiter:
- `config/config.py` (clés API)
- `email_sources.txt` (adresses sensibles)
- `src/newsletter_automation/credentials.json` (OAuth)
- `src/newsletter_automation/token.json` (Token Gmail)

Ces fichiers sont automatiquement ignorés par `.gitignore`.

Seuls les fichiers `.example` sont committes.

## 💡 Améliorations récentes

- ✅ **Pièce jointe automatique** - Synthèse jointe au mail
- ✅ **Configuration simplifiée** - Email sources en fichier `.txt`
- ✅ **Synthèses structurées** - Sections, listes à puces, données
- ✅ **2 emails par source** - Meilleure couverture
- ✅ **Nettoyage auto** - Retrait INBOX/NOTIFICATIONS
- ✅ **GitHub Actions** - Automatisation complète
- ✅ **Documentation complète** - Guides détaillés

## 🤝 Contribution

Les contributions sont bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 Licence

MIT

---

**Questions ?** Consultez la documentation ou créez une [issue](https://github.com/Ayhzer/newsletter-automation/issues).
