# Newsletter Automation

Script Python qui automatise la récupération de newsletters Gmail, génère des synthèses via Perplexity AI et crée des pages Notion.

## Fonctionnalités

- Récupération automatique des emails depuis Gmail
- Génération de synthèses intelligentes via l'API Perplexity
- Création automatique de pages Notion
- Sauvegarde locale des synthèses
- Marquage des emails traités

## Structure du projet

```
newsletter-automation/
├─ src/
│  └─ newsletter_automation/
│     ├─ __init__.py
│     └─ newsletter_automation.py
├─ config/
│  ├─ config.example.py
│  └─ config.py  (ignoré par Git)
├─ data/
│  ├─ input/
│  └─ output/  (ignoré par Git)
├─ credentials/  (ignoré par Git)
│  ├─ credentials.json
│  └─ token.json
├─ .env.example
├─ .gitignore
├─ requirements.txt
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

#### a. Créer les fichiers de configuration

```bash
cp config/config.example.py config/config.py
cp .env.example .env
```

#### b. Configurer les clés API dans `.env`

```
PERPLEXITY_API_KEY=votre_clé_perplexity
NOTION_API_KEY=votre_clé_notion
NOTION_DATABASE_ID=id_de_votre_database
```

#### c. Configurer Gmail OAuth

1. Créer un projet dans [Google Cloud Console](https://console.cloud.google.com/)
2. Activer l'API Gmail
3. Créer des identifiants OAuth 2.0
4. Télécharger le fichier et le placer dans `credentials/credentials.json`

#### d. Modifier `config/config.py`

Ajouter les adresses email des newsletters à traiter dans `EMAIL_SOURCES`.

### 5. Créer les dossiers nécessaires

```bash
mkdir -p data/input data/output credentials
```

## Utilisation

```bash
python -m newsletter_automation.newsletter_automation
```

Lors de la première exécution, une fenêtre de navigateur s'ouvrira pour autoriser l'accès à Gmail.

## Dépendances principales

- `google-auth-oauthlib` : Authentification Gmail
- `google-api-python-client` : API Gmail
- `requests` : Appels API Perplexity et Notion
- `beautifulsoup4` : Parsing HTML des emails

## Sécurité

⚠️ **Important** : Ne jamais commiter les fichiers suivants :
- `config/config.py`
- `credentials/`
- `.env`
- `data/output/`

Ces fichiers sont automatiquement ignorés par `.gitignore`.

## Licence

MIT
