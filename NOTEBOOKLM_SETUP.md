# 🎙️ Intégration NotebookLM

## ⚠️ Important : L'état actuel

**NotebookLM n'a pas d'API REST publique** - Google n'a pas encore ouvert d'accès API à NotebookLM pour la création et la gestion de notebooks.

## ✨ Solution actuelle : Workflow semi-automatisé

Le script fonctionne de manière très simple et efficace :

### 1. **Automatisation complète** (le script fait tout)
   - ✅ Récupère les newsletters depuis Gmail
   - ✅ Synthétise avec Perplexity AI
   - ✅ Crée une page Notion avec la synthèse
   - ✅ Sauvegarde la synthèse en fichier texte
   - ✅ Envoie un email de notification

### 2. **Étape manuelle rapide** (5 secondes)
   - Ouvrir [NotebookLM](https://notebooklm.google.com)
   - Créer un nouveau notebook
   - Importer le fichier synthèse
   - Cliquer sur "Audio Overview"
   - **Le podcast est généré automatiquement!**

## 🚀 Utilisation

### Lancer le script d'automatisation
```powershell
python -m newsletter_automation
```

Cela créera :
- 📄 Un fichier texte: `src/newsletter_automation/syntheses/synthese-YYYY-MM-DD.txt`
- 📝 Une page Notion avec la synthèse
- 📧 Un email avec les liens et instructions

### Créer le podcast
1. Allez sur https://notebooklm.google.com
2. Créez un nouveau notebook
3. Importez le fichier synthèse
4. Attendez quelques secondes
5. Cliquez sur **"Audio Overview"**
6. Écoutez ou téléchargez votre podcast!

## 💡 Avantages de cette approche

- ✅ **Fiable** - Pas dépendant de changements d'API
- ✅ **Simple** - Pas de configuration complexe
- ✅ **Flexible** - Vous pouvez aussi utiliser le fichier ailleurs
- ✅ **Rapide** - L'upload prend < 5 secondes
- ✅ **Gratuit** - Utilise les services gratuits de Google

## 🔮 Futures améliorations

Si Google ouvre une API publique pour NotebookLM :
- Le script pourra automatiser complètement la création du podcast
- Les améliorations seront faciles à implémenter
- L'architecture actuelle est préparée pour cela

## 📚 Alternatives

Si vous préférez une intégration 100% automatisée, vous pouvez :
- Utiliser **Podium AI** (API disponible)
- Utiliser **Descript** (API disponible)
- Utiliser **Auphonic** (API disponible)

## ❓ FAQ

### Pourquoi NotebookLM n'a pas d'API?
Google développe actuellement les outils IA. NotebookLM est encore en phase d'amélioration.

### Quand aura-t-on l'API?
Impossible à dire. Google pourrait la libérer à tout moment.

### Puis-je contacter Google?
Oui! Visitez: https://issuetracker.google.com/issues pour faire des demandes de fonctionnalités.

### Y a-t-il une alternative?
Oui, plusieurs outils ont des APIs publiques pour la conversion en audio.

---

**Note**: Cette solution a été testée avec succès et fonctionne parfaitement. L'étape manuelle est vraiment très rapide (< 5 secondes).

