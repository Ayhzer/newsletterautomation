# 📊 Structure du projet après nettoyage

## 📁 Répertoire racine
```
newsletterautomation/
├── README.md                    # Documentation principale
├── NOTEBOOKLM_SETUP.md         # Guide d'intégration NotebookLM
├── requirements.txt            # Dépendances Python
├── test_notebooklm.py          # Tests de l'intégration NotebookLM
│
├── config/                     # Configuration
│   ├── config.py              # Configuration réelle (à remplir)
│   ├── config.example.py      # Template de configuration
│   └── __pycache__/
│
├── src/                       # Code source
│   └── newsletter_automation/
│       ├── __init__.py
│       ├── newsletter_automation.py  # Script principal
│       ├── credentials.json          # Credentials Gmail (ignoré)
│       ├── token.json               # Token Gmail (ignoré)
│       ├── syntheses/               # Synthèses générées
│       └── __pycache__/
│
├── data/                      # Données
│   ├── input/                # Entrées (vides)
│   └── output/               # Sorties (vides)
│
├── .venv/                    # Environnement Python (ignoré)
├── .git/                     # Git (ignoré)
└── .gitignore
```

## 🗑️ Fichiers supprimés

Les fichiers suivants ont été supprimés car ils n'étaient utilisés que pour du troubleshooting :
- `CHANGELOG.md` - Historique des changements
- `check_env.py` - Vérification d'environnement
- `INDEX.md` - Index obsolète
- `PERPLEXITY_FIXES.md` - Notes de fix Perplexity
- `QUICK_FIX.md` - Notes de quick fix
- `show_simplification.py` - Script de debug
- `show_summary.py` - Script de debug
- `SIMPLIFICATION.md` - Notes de simplification
- `STATUS.txt` - Statut de développement
- `test_notion.py` - Tests Notion obsolètes
- `test_perplexity.py` - Tests Perplexity obsolètes
- `TROUBLESHOOTING_PERPLEXITY.md` - Guide de troubleshooting
- `validate.py` - Script de validation
- `VERIFICATION_REPORT.md` - Rapport de vérification
- `.env.example` - Fichier d'exemple

## ✅ Fichiers conservés

### 📚 Documentation
- **README.md** - Documentation complète du projet
- **NOTEBOOKLM_SETUP.md** - Guide pour configurer NotebookLM

### 📦 Configuration
- **requirements.txt** - Toutes les dépendances Python
- **config/config.example.py** - Template pour la configuration
- **config/config.py** - Configuration réelle (à remplir)

### 🧪 Tests
- **test_notebooklm.py** - Tests de l'intégration NotebookLM

### 🚀 Code principal
- **src/newsletter_automation/newsletter_automation.py** - Script d'automatisation

## 🏃 Utilisation

```bash
# 1. Installer les dépendances
pip install -r requirements.txt

# 2. Configurer le projet
cp config/config.example.py config/config.py
# Éditer config/config.py avec vos paramètres

# 3. Tester NotebookLM (optionnel)
python test_notebooklm.py

# 4. Lancer l'automatisation
python -m src.newsletter_automation.newsletter_automation
```

## 📊 Fonctionnalités

Le script fait automatiquement :
1. 📧 Récupère les newsletters depuis Gmail
2. 🤖 Synthétise avec Perplexity AI
3. 📝 Crée une page Notion
4. 💾 Sauvegarde en fichier texte
5. 🏷️ Marque comme lus + libellé "newletterinnotion"
6. 📤 Envoie un email de notification

## 📝 Notes

- Tous les secrets (clés API, tokens) sont dans `config/config.py` (ignoré par git)
- Les credentials Gmail sont générés automatiquement
- Les synthèses sont sauvegardées dans `src/newsletter_automation/syntheses/`
