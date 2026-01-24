# 🚀 QuickStart (5 minutes)

## ⚡ Installation (2 minutes)

```bash
# Cloner
git clone https://github.com/votreusername/newsletter-automation.git
cd newsletter-automation

# Setup (Windows)
python -m venv .venv
.venv\Scripts\activate

# Setup (macOS/Linux)
python3 -m venv .venv
source .venv/bin/activate

# Installer
pip install -r requirements.txt
```

## 🔑 Configuration (3 minutes)

### 1. Préparer les fichiers

```bash
# Copier le config template
cp config/config.example.py config/config.py

# Copier le credentials template
cp src/newsletter_automation/credentials.example.json src/newsletter_automation/credentials.json
```

### 2. Remplir les secrets

Éditez `config/config.py` :

```python
CONFIG = {
    "EMAIL_SOURCES": ["newsletter1@example.com", "newsletter2@example.com"],
    "PERPLEXITY_API_KEY": "votre_clé_perplexity",
    "NOTION_TOKEN": "votre_token_notion",
    "NOTION_PARENT_PAGE_ID": "votre_page_id",
    "NOTIFICATION_EMAIL": "votre@email.com",
}
```

Éditez `src/newsletter_automation/credentials.json` :
- Copier le contenu du fichier JSON téléchargé depuis Google Cloud Console

## ▶️ Lancer

```bash
python -m src.newsletter_automation.newsletter_automation
```

La première exécution :
1. Ouvrira un navigateur pour l'authentification Gmail
2. Accepter et autoriser
3. C'est bon !

## ✅ Vérifier

Vous devriez voir :
- 📧 Emails récupérés depuis Gmail
- 🤖 Synthèse générée
- 📝 Page Notion créée
- 💾 Fichier sauvegardé
- 📤 Email de notification envoyé

## 📖 Pour plus de détails

- [Installation complète](INSTALLATION.md)
- [Documentation complète](README_GENERIC.md)
- [Structure du projet](PROJECT_STRUCTURE.md)

## 🆘 Problème ?

**Erreur d'authentification Gmail ?**
- Supprimer `src/newsletter_automation/token.json`
- Relancer le script
- Accepter l'authentification

**Erreur Notion ?**
- Vérifier le token et la page parente
- Vérifier que la page est partagée avec l'intégration

**Autre erreur ?**
- Consulter [INSTALLATION.md](INSTALLATION.md) → Dépannage

---

**Prêt ? Lancez le script et profitez de vos synthèses automatiques ! 🎉**
