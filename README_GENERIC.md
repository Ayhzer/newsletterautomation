# Newsletter Automation Hub 🚀

Automatisez vos newsletters : synthèse IA + Notion + Podcast

## ✨ Fonctionnalités

- 📧 **Récupère** les newsletters depuis Gmail
- 🤖 **Synthétise** avec Perplexity AI
- 📝 **Crée** une page Notion automatiquement
- 🏷️ **Organise** les mails (libellé + marquage comme lus)
- 💾 **Sauvegarde** les synthèses en fichier texte
- 🎙️ **Prépare** les fichiers pour NotebookLM (podcast)
- 📤 **Notifie** via email avec un résumé complet

## 🎯 Cas d'usage

Parfait pour :
- Synthétiser plusieurs newsletters tech/actualités
- Organiser automatiquement vos emails
- Créer une base de connaissance dans Notion
- Générer des podcasts à partir de synthèses

## 🚀 Installation rapide

### 1. Prérequis
- Python 3.8+
- Compte Gmail
- Compte Perplexity AI (clé API)
- Compte Notion (token + page parent)

### 2. Cloner et installer

```bash
git clone https://github.com/votreusername/newsletter-automation.git
cd newsletter-automation
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configurer

```bash
cp config/config.example.py config/config.py
# Éditez config/config.py avec vos paramètres
```

### 4. Configuration des services

#### Gmail
1. Allez sur [Google Cloud Console](https://console.cloud.google.com)
2. Créez un projet
3. Activez l'API Gmail
4. Créez un OAuth 2.0 ID de client (Bureau)
5. Téléchargez le JSON en tant que `credentials.json`
6. Placez-le dans `src/newsletter_automation/`

#### Perplexity AI
1. Allez sur [Perplexity API](https://www.perplexity.ai/api)
2. Créez une clé API
3. Copiez-la dans `config.py` sous `PERPLEXITY_API_KEY`

#### Notion
1. Allez sur [Notion Integrations](https://www.notion.so/my-integrations)
2. Créez une nouvelle intégration
3. Copier le token dans `NOTION_TOKEN`
4. Trouvez l'ID d'une page parent dans `NOTION_PARENT_PAGE_ID`

### 5. Lancer

```bash
python -m src.newsletter_automation.newsletter_automation
```

## 📋 Configuration

Éditez `config/config.py` :

```python
CONFIG = {
    # Gmail - Adresses email des newsletters
    "EMAIL_SOURCES": [
        "newsletter@example1.com",
        "newsletter@example2.com",
    ],
    
    # Perplexity AI API
    "PERPLEXITY_API_KEY": "pplx-xxxxx",
    
    # Notion API
    "NOTION_TOKEN": "ntn_xxxxx",
    "NOTION_PARENT_PAGE_ID": "xxxxx",
    
    # Email de notification
    "NOTIFICATION_EMAIL": "votre.email@gmail.com",
}
```

## 🧪 Tests

Tester l'intégration NotebookLM :

```bash
python test_notebooklm.py
```

## 📁 Structure

```
newsletter-automation/
├── src/newsletter_automation/     # Code principal
├── config/
│   ├── config.example.py         # Template de config
│   └── config.py                 # Config réelle (ignorée)
├── test_notebooklm.py            # Tests
├── README.md                      # Ce fichier
└── requirements.txt              # Dépendances
```

## 📚 Documentation

- [INSTALLATION.md](INSTALLATION.md) - Guide d'installation détaillé
- [NOTEBOOKLM_SETUP.md](NOTEBOOKLM_SETUP.md) - Intégration NotebookLM
- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Structure du projet

## 🔧 Dépannage

### Erreur 401 Gmail
```
Vérifiez que credentials.json est bien placé et valide
```

### Erreur Perplexity API
```
Vérifiez votre clé API et votre solde de crédit
```

### Notion ne crée pas la page
```
Vérifiez que le token est valide et que la page parente est accessible
```

## 🎯 Flux de travail

```
1. Gmail reçoit les newsletters
   ↓
2. Script les récupère (non lues)
   ↓
3. Perplexity génère une synthèse
   ↓
4. Notion crée une page
   ↓
5. Synthèse sauvegardée en .txt
   ↓
6. Emails marqués comme lus + libellé
   ↓
7. Email de notification avec résumé
   ↓
8. (Optionnel) Upload dans NotebookLM pour podcast
```

## 🤝 Contribution

Les contributions sont bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer des améliorations
- Soumettre des pull requests

## 📄 Licence

MIT License - Libre d'utilisation

## 💬 Support

- 📖 Consultez la documentation
- 🐛 Ouvrez une issue sur GitHub
- 💡 Partagez vos retours

## 🌟 Améliorations futures

- [ ] Support d'autres sources d'emails (Outlook, etc.)
- [ ] Intégration avec d'autres services de synthèse
- [ ] Interface web pour configurer
- [ ] Automation complète du podcast (API NotebookLM quand disponible)
- [ ] Multi-langues
- [ ] Support de plusieurs comptes

## ⭐ Si vous aimez ce projet

N'oubliez pas de laisser une étoile ⭐ sur GitHub !

---

**Créé avec ❤️ pour les lecteurs de newsletters**
