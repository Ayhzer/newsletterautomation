# Contribution au projet

Merci de contribuer à Newsletter Automation ! 🎉

## 🚀 Comment contribuer

### Signaler un bug

1. Vérifier que le bug n'a pas déjà été signalé
2. Ouvrir une nouvelle issue
3. Inclure :
   - Une description claire du bug
   - Les étapes pour le reproduire
   - Le comportement attendu
   - Le comportement réel
   - Votre environnement (OS, version Python, etc.)

### Proposer une amélioration

1. Ouvrir une issue avec le label "enhancement"
2. Décrire l'amélioration proposée
3. Expliquer pourquoi c'est utile
4. Si possible, donner des exemples d'utilisation

### Soumettre un code

1. **Fork le repository**
   ```bash
   git clone https://github.com/votreusername/newsletter-automation.git
   cd newsletter-automation
   ```

2. **Créer une branche**
   ```bash
   git checkout -b feature/ma-fonctionnalite
   ```

3. **Faire vos modifications**
   - Suivre le style de code existant
   - Ajouter des commentaires
   - Tester votre code

4. **Commiter vos changements**
   ```bash
   git add .
   git commit -m "Ajouter: description claire de la feature"
   ```

5. **Pousser et créer une Pull Request**
   ```bash
   git push origin feature/ma-fonctionnalite
   ```
   - Aller sur GitHub
   - Cliquer "New Pull Request"
   - Décrire clairement votre PR

## 📝 Règles de style

- Utiliser `black` pour le formatage
- Ajouter des docstrings aux fonctions
- Commenter le code complexe
- Nommer les variables de manière claire
- Tester avant de soumettre

## ✅ Checklist avant de soumettre

- [ ] Code testé et fonctionnel
- [ ] Pas d'erreurs ou warnings
- [ ] Docstring ajoutée/mise à jour
- [ ] Commit message clair et concis
- [ ] Pas de données sensibles dans le code

## 🎓 Architecture

### Structure des fonctions

```python
def faire_quelquechose(param1, param2):
    """
    Description courte.
    
    Paramètres:
        param1: Description
        param2: Description
    
    Retourne:
        Description du retour
    """
    # Code ici
    pass
```

### Nommage

- Fonctions : `snake_case`
- Classes : `PascalCase`
- Constantes : `UPPER_CASE`

## 🧪 Tester

```bash
# Avant de soumettre
python test_notebooklm.py

# Vérifier les imports
python -c "import src.newsletter_automation.newsletter_automation"
```

## 📚 Ressources

- [Style Guide PEP 8](https://pep8.org/)
- [Python Documentation](https://docs.python.org/)
- [README du projet](README.md)

## 🎯 Domaines à améliorer

Nous cherchons des contributions pour :

- [ ] Support d'autres sources d'emails (Outlook, Thunderbird)
- [ ] Interface web pour configurer
- [ ] Documentation en d'autres langues
- [ ] Intégration avec d'autres services (Slack, Teams)
- [ ] Tests unitaires supplémentaires
- [ ] Performance et optimisations

## 👥 Reconnaissance

Tous les contributeurs seront reconnus dans :
- Le README.md
- Les releases notes

## ❓ Questions

Si vous avez des questions :
1. Consultez la documentation
2. Ouvrez une issue "question"
3. Demandez dans les discussions

---

**Merci de rendre ce projet meilleur ! ❤️**
