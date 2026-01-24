# 📦 Guide d'Installation Complet

## ✅ Prérequis

- **Python 3.8 ou supérieur**
- **pip** (gestionnaire de paquets Python)
- **Git**
- Comptes pour : Gmail, Perplexity AI, Notion

## 🔧 Étape 1 : Installation de base

### Windows

```powershell
# Cloner le repository
git clone https://github.com/votreusername/newsletter-automation.git
cd newsletter-automation

# Créer l'environnement virtuel
python -m venv .venv

# Activer l'environnement
.venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### macOS / Linux

```bash
# Cloner le repository
git clone https://github.com/votreusername/newsletter-automation.git
cd newsletter-automation

# Créer l'environnement virtuel
python3 -m venv .venv

# Activer l'environnement
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## 🔑 Étape 2 : Configuration des services

### 2.1 Gmail (Récupérer les newsletters)

1. **Aller sur [Google Cloud Console](https://console.cloud.google.com)**
   - Créer un nouveau projet
   - Nommer le projet "Newsletter Automation"

2. **Activer l'API Gmail**
   - Aller dans "APIs & Services" → "Library"
   - Rechercher "Gmail API"
   - Cliquer sur "ENABLE"

3. **Créer les credentials**
   - Aller dans "APIs & Services" → "Credentials"
   - Cliquer sur "+ CREATE CREDENTIALS"
   - Sélectionner "OAuth 2.0 ID de client"
   - Type: "Bureau"
   - Remplir le formulaire
   - Créer

4. **Télécharger le JSON**
   - Cliquer sur l'ID créé
   - Cliquer sur le bouton "Télécharger"
   - Sauvegarder en tant que `credentials.json`
   - Placer dans `src/newsletter_automation/credentials.json`

5. **La première exécution**
   - Lancer le script
   - Un navigateur s'ouvrira pour l'authentification
   - Accepter l'accès
   - Le token sera sauvegardé automatiquement

### 2.2 Perplexity AI (Synthèse)

1. **Aller sur [Perplexity API](https://www.perplexity.ai/api)**

2. **Créer une clé API**
   - S'authentifier
   - Aller à "API Keys"
   - Créer une nouvelle clé
   - Copier la clé

3. **Ajouter à la configuration**
   ```python
   # Dans config/config.py
   "PERPLEXITY_API_KEY": "pplx-votre_clé_ici",
   ```

### 2.3 Notion (Base de connaissances)

1. **Aller sur [Notion My Integrations](https://www.notion.so/my-integrations)**

2. **Créer une intégration**
   - Cliquer sur "+ New integration"
   - Nommer "Newsletter Automation"
   - Sélectionner les capacités :
     - Read
     - Update
     - Insert
   - Créer

3. **Copier le token**
   - Dans les détails de l'intégration
   - Copier "Internal Integration Token"
   - Ajouter à `config.py` :
   ```python
   "NOTION_TOKEN": "ntn_votre_token_ici",
   ```

4. **Trouver l'ID de la page parent**
   - Aller sur notion.so
   - Créer ou ouvrir une page pour les synthèses
   - L'URL ressemble à : `https://www.notion.so/XXXXX?v=YYYYY`
   - XXXXX est l'ID de la page (sans les tirets)
   - Ajouter à `config.py` :
   ```python
   "NOTION_PARENT_PAGE_ID": "xxxxxyyyyy...",
   ```

5. **Partager la page avec l'intégration**
   - Ouvrir la page dans Notion
   - Cliquer sur "Share"
   - Inviter l'intégration "Newsletter Automation"
   - Donner les droits Edit

## 📋 Étape 3 : Configuration du projet

```bash
# Copier le fichier exemple
cp config/config.example.py config/config.py
```

Éditez `config/config.py` avec vos paramètres :

```python
CONFIG = {
    # 1. Adresses des newsletters
    "EMAIL_SOURCES": [
        "newsletter@techmeme.com",
        "newsletter@example.com",
        # Ajouter les vôtres ici
    ],
    
    # 2. Perplexity (déjà copié depuis l'étape 2.2)
    "PERPLEXITY_API_KEY": "pplx-...",
    
    # 3. Notion (tokens de l'étape 2.3)
    "NOTION_TOKEN": "ntn_...",
    "NOTION_PARENT_PAGE_ID": "xxxxx...",
    
    # 4. Email pour les notifications
    "NOTIFICATION_EMAIL": "votre.email@gmail.com",
}
```

## ✅ Étape 4 : Tester

### Test 1 : Vérifier les imports

```bash
python -c "import src.newsletter_automation.newsletter_automation"
```

Si pas d'erreur : ✅

### Test 2 : Tester NotebookLM (optionnel)

```bash
python test_notebooklm.py
```

### Test 3 : Lancer le script complet

```bash
python -m src.newsletter_automation.newsletter_automation
```

## 🎯 Premier run

1. **Le script cherchera les emails non lus des 24 dernières heures**
2. **S'il y en a, il va :**
   - Synthétiser avec Perplexity
   - Créer une page Notion
   - Sauvegarder le texte
   - Marquer comme lus dans Gmail
   - Envoyer un email

3. **Vérifier les résultats :**
   - ✅ Gmail : Emails marqués comme lus
   - ✅ Notion : Nouvelle page créée
   - ✅ Email : Notification reçue
   - ✅ Fichier : `src/newsletter_automation/syntheses/synthese-YYYY-MM-DD.txt`

## ⚙️ Configuration avancée

### Automatiser l'exécution

#### Windows (Planificateur des tâches)

1. Ouvrir "Planificateur des tâches"
2. Créer une tâche de base
3. Nommer "Newsletter Automation"
4. Dans "Actions" :
   - Ajouter une action
   - Programme : `python.exe`
   - Arguments : `-m src.newsletter_automation.newsletter_automation`
   - Répertoire : `C:\chemin\vers\newsletter-automation`
5. Planifier (tous les jours à 8h00 par exemple)

#### Linux / macOS (Cron)

```bash
# Éditer le crontab
crontab -e

# Ajouter cette ligne (tous les jours à 8h)
0 8 * * * cd /chemin/vers/newsletter-automation && /chemin/vers/.venv/bin/python -m src.newsletter_automation.newsletter_automation

# Sauvegarder et quitter
```

## 🆘 Dépannage

### "ModuleNotFoundError: No module named 'src'"

```bash
# Vérifier que vous êtes bien dans le répertoire du projet
pwd  # ou cd sur Windows
# Le output devrait se terminer par /newsletter-automation

# Réinstaller les dépendances
pip install -r requirements.txt
```

### "credentials.json not found"

```bash
# Vérifier le chemin
# Le fichier doit être ici :
# src/newsletter_automation/credentials.json

# Si absent, relancer le script
# Il vous guidera pour l'authentification
```

### "Gmail API not enabled"

```bash
# Aller sur Google Cloud Console
# Vérifier que l'API Gmail est activée
# Relancer le script
```

### "Notion token invalid"

```bash
# Vérifier le token dans config.py
# Vérifier que la page Notion est partagée avec l'intégration
# Vérifier l'ID de la page parente
```

## 📞 Support

- 📖 Consultez README.md
- 🐛 Ouvrez une issue sur GitHub
- 💬 Laissez un commentaire

## ✨ Prochain pas

- [Guide NotebookLM](NOTEBOOKLM_SETUP.md)
- [Structure du projet](PROJECT_STRUCTURE.md)
- [README complet](README.md)

---

**Besoin d'aide ? Consultez les FAQ dans les issues GitHub !**
