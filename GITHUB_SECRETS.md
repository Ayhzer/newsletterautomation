# 🔐 Configuration des Secrets GitHub pour l'Automatisation

Ce guide explique comment configurer tous les secrets nécessaires pour que votre workflow GitHub Actions fonctionne correctement.

---

## 📍 Accès aux Secrets GitHub

1. Allez sur votre repository GitHub
2. Cliquez sur **Settings** (⚙️)
3. Dans le menu de gauche, cliquez sur **Secrets and variables** → **Actions**
4. Cliquez sur **New repository secret**

---

## 🔑 Secrets Requis

### 1. PERPLEXITY_API_KEY

**Syntaxe:** `pplx-xxxxxxxxxxxxxxxxxxxxxxxx`

**Où l'obtenir:**
1. Allez sur [https://www.perplexity.ai](https://www.perplexity.ai)
2. Créez ou connectez-vous à votre compte
3. Allez à **API Settings** ou **Account** → **API Keys**
4. Générez une nouvelle clé API
5. Copiez la clé complète commençant par `pplx-`

**Exemple:**
```
pplx-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
```

**À saisir dans GitHub:**
```
Secret name: PERPLEXITY_API_KEY
Secret value: pplx-a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p
```

---

### 2. NOTION_TOKEN

**Syntaxe:** `ntn_xxxxxxxxxxxxxxxxxxxxx`

**Où l'obtenir:**
1. Allez sur [https://www.notion.so/my-integrations](https://www.notion.so/my-integrations)
2. Cliquez sur **Create new integration**
3. Donnez-lui un nom (ex: "Newsletter Automation")
4. Sélectionnez les capacités: `Read`, `Update`, `Insert`
5. Cliquez sur **Submit**
6. Sur la page de l'intégration créée, cliquez sur **Show** (dans la section "Internal Integration Token")
7. Copiez le token complet

**Exemple:**
```
ntn_12345678901234567890123456789012345678
```

**À saisir dans GitHub:**
```
Secret name: NOTION_TOKEN
Secret value: ntn_12345678901234567890123456789012345678
```

---

### 3. NOTION_PARENT_PAGE_ID

**Syntaxe:** `xxxxxxxxxxxxxxxxxxxxxxxx` (32 caractères hexadécimaux)

**Où l'obtenir:**
1. Ouvrez la page Notion parent où vous voulez créer les newsletters
2. Cliquez sur le menu **Share** en haut à droite
3. Cliquez sur **Copy link**
4. Extrayez l'ID de l'URL: `https://www.notion.so/MonWorkspace/MonPageName-XXXXXXXXXXXXXXXXXXXXX`
5. L'ID est la partie après le dernier `-` jusqu'à la fin (32 caractères)

**Alternative (plus simple):**
1. Ouvrez la page dans Notion
2. Cliquez sur les **⋮** (trois points) en haut à droite
3. Cliquez sur **Copy page link**
4. Extrayez l'ID de l'URL

**Exemple:**
```
5f4c8b9a2d1e3f7c9b4a6d8e1f3c5b7a
```

**À saisir dans GitHub:**
```
Secret name: NOTION_PARENT_PAGE_ID
Secret value: 5f4c8b9a2d1e3f7c9b4a6d8e1f3c5b7a
```

---

### 4. NOTIFICATION_EMAIL

**Syntaxe:** `votre.email@gmail.com`

**Description:** L'adresse email où les notifications seront envoyées

**Exemple:**
```
jean.dupont@gmail.com
```

**À saisir dans GitHub:**
```
Secret name: NOTIFICATION_EMAIL
Secret value: jean.dupont@gmail.com
```

---

## 📧 Configuration des Sources Email (email_sources.txt)

**Note importante:** Les adresses email des newsletters à traiter ne sont **PAS** des secrets. Elles sont chargées depuis un fichier texte `email_sources.txt` au lieu des secrets GitHub.

### Configuration locale (développement):
```bash
cp email_sources.example.txt email_sources.txt
# Modifiez email_sources.txt et ajoutez vos adresses email
```

### Configuration GitHub Actions:
Pour que le workflow GitHub fonctionne, vous devez ajouter le fichier `email_sources.txt` à votre repository.

**Option 1: Pousser le fichier (simple)**
```bash
cp email_sources.example.txt email_sources.txt
# Modifiez email_sources.txt avec vos sources
git add email_sources.txt
git commit -m "Add email sources configuration"
git push
```

**Option 2: Créer le fichier via le workflow (avancé)**
Si vous ne voulez pas committer le fichier, créez le fichier dans votre workflow GitHub Actions via un secret GitHub nommé `EMAIL_SOURCES_CONTENT` avec un format spécifique.

---

## 🔐 Secrets Google (Authentification Gmail)

Pour l'authentification Gmail, vous avez **deux options**:

### Option A: GOOGLE_OAUTH_TOKEN_JSON (Recommandé ✅)

**Syntaxe:** Contenu JSON complet

**Comment générer:**
1. Suivez le guide: [Google Gmail API Setup](https://developers.google.com/gmail/api/quickstart/python)
2. Créez les credentials pour "Desktop Application"
3. Téléchargez le fichier `credentials.json`
4. Lancez le script une fois en local pour générer `token.json`
5. Ouvrez le fichier `src/newsletter_automation/token.json`
6. Copiez **tout le contenu** (c'est du JSON)

**Contenu du fichier token.json (format):**
```json
{
  "token": "ya29.a0...",
  "refresh_token": "1//0...",
  "token_uri": "https://oauth2.googleapis.com/token",
  "client_id": "xxx.apps.googleusercontent.com",
  "client_secret": "xxx",
  "scopes": [
    "https://www.googleapis.com/auth/gmail.modify"
  ],
  "type": "authorized_user"
}
```

**À saisir dans GitHub:**
```
Secret name: GOOGLE_OAUTH_TOKEN_JSON
Secret value: (coller le JSON complet du fichier token.json)
```

---

### Option B: GOOGLE_CREDENTIALS_JSON (Alternative)

**Syntaxe:** Contenu JSON complet

**Comment générer:**
1. Suivez le guide: [Google Gmail API Setup](https://developers.google.com/gmail/api/quickstart/python)
2. Créez les credentials pour "Desktop Application"
3. Téléchargez le fichier `credentials.json`
4. Ouvrez-le et copiez **tout le contenu** (c'est du JSON)

**Contenu du fichier credentials.json (format):**
```json
{
  "installed": {
    "client_id": "xxx.apps.googleusercontent.com",
    "client_secret": "xxx",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "redirect_uris": ["http://localhost"]
  }
}
```

**À saisir dans GitHub:**
```
Secret name: GOOGLE_CREDENTIALS_JSON
Secret value: (coller le JSON complet du fichier credentials.json)
```

---

## ✅ Checklist Finale

Avant de lancer le workflow:

- [ ] **PERPLEXITY_API_KEY** - Saisi et commence par `pplx-`
- [ ] **NOTION_TOKEN** - Saisi et commence par `ntn_`
- [ ] **NOTION_PARENT_PAGE_ID** - Saisi (32 caractères)
- [ ] **NOTIFICATION_EMAIL** - Saisi (format email valide)
- [ ] **email_sources.txt** - Créé et configuré avec vos adresses email
- [ ] **GOOGLE_OAUTH_TOKEN_JSON** OU **GOOGLE_CREDENTIALS_JSON** - L'un des deux saisi (format JSON complet)

---

## 🧪 Tester la Configuration

Une fois tous les secrets saisis:

1. Allez à **Actions** dans votre repository GitHub
2. Sélectionnez le workflow (ex: "Newsletter Automation")
3. Cliquez sur **Run workflow**
4. Choisissez la branche `main`
5. Cliquez sur **Run workflow**

Vérifiez les logs pour voir si tout fonctionne correctement.

---

## 🔒 Sécurité

⚠️ **Important:**
- Les secrets ne sont **jamais** affichés dans les logs
- Ils ne sont transmis qu'au moment du besoin
- Régénérez vos clés API régulièrement
- Ne commitez **jamais** vos secrets en dur dans le code
- Utilisez toujours les GitHub Secrets pour les valeurs sensibles

---

## ❓ Dépannage

### Le workflow échoue avec "PERPLEXITY_API_KEY not configured"
- Vérifiez que le secret `PERPLEXITY_API_KEY` est bien créé
- Vérifiez qu'il commence par `pplx-`
- Vérifiez qu'il n'y a pas d'espaces au début ou à la fin

### Erreur Gmail / Authentification
- Si vous utilisez `GOOGLE_OAUTH_TOKEN_JSON`, assurez-vous qu'il contient un `refresh_token`
- Régénérez le token en local si nécessaire

### Erreur Notion
- Vérifiez que le token commence par `ntn_`
- Vérifiez que la page parent a les bonnes permissions
- L'intégration Notion doit avoir accès à la page

---

## 📚 Ressources Utiles

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)
- [Google Gmail API Quickstart](https://developers.google.com/gmail/api/quickstart/python)
- [Notion API Documentation](https://developers.notion.com/)
- [Perplexity API Documentation](https://docs.perplexity.ai/)
