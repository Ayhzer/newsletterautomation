# Newsletter Automation

Script Python qui automatise la récupération de newsletters Gmail, génère des synthèses via IA et crée des pages Notion — avec cascade automatique de 3 moteurs IA.

## Fonctionnalités

- **Récupération automatique** des emails depuis Gmail
- **Synthèses intelligentes** — cascade automatique : Gemini → Groq → Tavily → brut
- **Création de pages Notion** automatiquement
- **Pièce jointe au mail** - Synthèse prête pour NotebookLM
- **Sauvegarde locale** des synthèses en `.txt`
- **Gestion intelligente des emails** - Jusqu'à 2 par source
- **Marquage automatique** et retrait de la boite de réception/notifications
- **Gestion robuste des erreurs** avec retry automatique et vérification post-marquage
- **Gitea Actions ready** - Planification automatique (7h UTC)
- **Configuration sécurisée** - Secrets Gitea/GitHub ou env variables

## Schéma du workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    NEWSLETTER AUTOMATION                        │
│                  (déclenchement : 7h UTC)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  1. COLLECTE GMAIL        │
              │  - Lit email_sources.txt  │
              │  - Récupère ≤2 emails     │
              │    non lus par source     │
              │  - Détecte nouveaux vs    │
              │    dernière exécution     │
              └───────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │  Nouveaux emails? │
                    └─────────┬─────────┘
                    OUI       │       NON → Fin
                              ▼
              ┌───────────────────────────┐
              │  2. CONVERSION CONTENU    │
              │  - HTML → Markdown        │
              │    (html2text)            │
              │  - Nettoyage du texte     │
              └───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────────────────────┐
              │  3. CASCADE IA (synthèse)                 │
              │                                           │
              │  ┌─────────────────────────────────────┐ │
              │  │  Tier 1 : GEMINI (Google)           │ │
              │  │  Synthèse directe du contenu email  │ │
              │  └──────────────┬──────────────────────┘ │
              │         Échec   │   Succès ──────────────►│
              │                 ▼                         │
              │  ┌─────────────────────────────────────┐ │
              │  │  Tier 2 : GROQ (Llama)              │ │
              │  │  Fallback si Gemini indisponible    │ │
              │  └──────────────┬──────────────────────┘ │
              │         Échec   │   Succès ──────────────►│
              │                 ▼                         │
              │  ┌─────────────────────────────────────┐ │
              │  │  Tier 3 : TAVILY (recherche web)    │ │
              │  │  Recherche + résumé automatique     │ │
              │  └──────────────┬──────────────────────┘ │
              │         Échec   │   Succès ──────────────►│
              │                 ▼                         │
              │  ┌─────────────────────────────────────┐ │
              │  │  Tier 4 : CONTENU BRUT              │ │
              │  │  Texte original pour NotebookLM     │ │
              │  └─────────────────────────────────────┘ │
              └───────────────────────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  4. SAUVEGARDE LOCALE     │
              │  - Fichier .txt           │
              │    (synthèse complète)    │
              └───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  5. CRÉATION NOTION       │
              │  - Nouvelle page          │
              │  - Contenu Markdown       │
              │    converti en blocs      │
              │  - Lien URL retourné      │
              └───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  6. MARQUAGE GMAIL        │
              │  - Marquer comme lu       │
              │  - Retrait INBOX          │
              │  - Retrait NOTIFICATIONS  │
              │  - Label "newsletter      │
              │    innotion" ajouté       │
              │  - Vérification post-     │
              │    marquage (fallback     │
              │    individuel si besoin)  │
              └───────────────────────────┘
                              │
                              ▼
              ┌───────────────────────────┐
              │  7. NOTIFICATION EMAIL    │
              │  - Lien Notion direct     │
              │  - Synthèse en pièce      │
              │    jointe (.txt)          │
              │  - Instructions podcast   │
              │    NotebookLM             │
              └───────────────────────────┘
```

## Structure du projet

```
newsletterautomation/
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
├─ GITHUB_SECRETS.md               # Configuration secrets Gitea/GitHub
├─ QUICKSTART.md                   # Démarrage rapide
└─ NOTEBOOKLM_SETUP.md            # Intégration NotebookLM
```

## Démarrage rapide (5 min)

```bash
# 1. Cloner
git clone https://papageek.hopto.org:8443/ayhzer/newsletterautomation.git
cd newsletterautomation

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

> Pour un guide détaillé, voir [INSTALLATION.md](INSTALLATION.md) ou [QUICKSTART.md](QUICKSTART.md)

## Configuration

### Fichier config.py

```bash
cp config/config.example.py config/config.py
```

Remplir dans `config/config.py` :

| Clé | Description | Requis |
|-----|-------------|--------|
| `GEMINI_API_KEY` | Clé API Google Gemini (Tier 1) | Recommandé |
| `GROQ_API_KEY` | Clé API Groq/Llama (Tier 2) | Recommandé |
| `TAVILY_API_KEY` | Clé API Tavily recherche web (Tier 3) | Optionnel |
| `NOTION_TOKEN` | Token intégration Notion | Requis |
| `NOTION_PARENT_PAGE_ID` | ID de la page Notion parente | Requis |
| `NOTIFICATION_EMAIL` | Email pour les notifications | Requis |

> Au moins une clé IA (Gemini ou Groq) est recommandée. Sans aucune clé, le script produit le contenu brut pour NotebookLM.

### Fichier email_sources.txt

```bash
cp email_sources.example.txt email_sources.txt
```

Ajouter une adresse email par ligne :

```
newsletter@example.com
newsletter2@example.com
```

### Gmail OAuth

1. Créer un projet dans [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API Gmail
3. Créer identifiants OAuth (type "Application de bureau")
4. Placer le JSON à : `src/newsletter_automation/credentials.json`

### Gitea Actions (automatisation)

Configurer les secrets dans les paramètres du dépôt Gitea :
- `GEMINI_API_KEY`
- `GROQ_API_KEY`
- `TAVILY_API_KEY`
- `NOTION_TOKEN`
- `NOTION_PARENT_PAGE_ID`
- `NOTIFICATION_EMAIL`
- `GMAIL_TOKEN` (token OAuth Gmail encodé en base64)

Voir [GITHUB_SECRETS.md](GITHUB_SECRETS.md) pour les détails.

## Dépendances principales

- `google-auth-oauthlib` - Authentification Gmail OAuth 2.0
- `google-api-python-client` - API Gmail
- `google-generativeai` - API Google Gemini
- `groq` - API Groq (Llama)
- `requests` - Appels API Tavily et Notion
- `notion-client` - Création pages Notion
- `html2text` - Conversion HTML → Markdown

## Utilisation

### Local

```bash
python src/newsletter_automation/newsletter_automation.py
```

À la première exécution, un navigateur s'ouvre pour autoriser l'accès Gmail.

### Gitea Actions (automatisé)

Le workflow s'exécute automatiquement tous les jours à **7h UTC**. Configurer les secrets Gitea pour activer l'automatisation.

## NotebookLM Integration

La synthèse est automatiquement jointe au mail. Pour générer un podcast :

1. Ouvrez l'email de notification
2. Téléchargez la pièce jointe `.txt`
3. Allez sur [NotebookLM](https://notebooklm.google.com)
4. Drag & drop le fichier
5. Cliquez "Audio Overview" pour générer le podcast

Voir [NOTEBOOKLM_SETUP.md](NOTEBOOKLM_SETUP.md) pour plus de détails.

## Sécurité

**Ne jamais commiter :**
- `config/config.py` (clés API)
- `email_sources.txt` (adresses sensibles)
- `src/newsletter_automation/credentials.json` (OAuth)
- `src/newsletter_automation/token.json` (Token Gmail)

Ces fichiers sont automatiquement ignorés par `.gitignore`. Seuls les fichiers `.example` sont commités.

## Documentation

- **[INSTALLATION.md](INSTALLATION.md)** - Guide d'installation complet
- **[QUICKSTART.md](QUICKSTART.md)** - Démarrage en 5 minutes
- **[GITHUB_SECRETS.md](GITHUB_SECRETS.md)** - Configuration secrets Gitea/GitHub
- **[NOTEBOOKLM_SETUP.md](NOTEBOOKLM_SETUP.md)** - Intégration NotebookLM

## Licence

MIT
