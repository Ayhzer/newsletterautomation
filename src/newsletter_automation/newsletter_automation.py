#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script d'automatisation de traitement des newsletters
Récupère les emails, les synthétise avec Perplexity, et crée une page Notion
"""

import os
import sys
import base64
import json
from datetime import datetime, timedelta

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import requests
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from notion_client import Client
import html2text
from pathlib import Path
import sys

# Base directory (this file's directory)
BASE_DIR = Path(__file__).resolve().parent

# ==================== CHARGEMENT CONFIGURATION ====================
# Priorité aux variables d'environnement (pour GitHub Actions)
# Puis fallback sur config/config.py (pour dev local)

PERPLEXITY_API_KEY = os.environ.get('PERPLEXITY_API_KEY')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_PARENT_PAGE_ID = os.environ.get('NOTION_PARENT_PAGE_ID')
NOTIFICATION_EMAIL = os.environ.get('NOTIFICATION_EMAIL')

# Si les variables d'environnement ne sont pas définies, charger config.py
if not all([PERPLEXITY_API_KEY, NOTION_TOKEN, NOTION_PARENT_PAGE_ID, NOTIFICATION_EMAIL]):
    print('⚙️  Variables d\'environnement non trouvées, chargement de config.py...')
    
    # Essayer d'abord le chemin relatif au répertoire courant (GitHub Actions)
    config_file = Path('config') / 'config.py'
    if not config_file.exists():
        # Sinon utiliser le chemin absolu (développement local)
        config_dir = BASE_DIR.parent.parent / 'config'
        config_file = config_dir / 'config.py'
    
    if not config_file.exists():
        raise FileNotFoundError(
            f"Fichier config/config.py non trouvé à {config_file}\n"
            f"Créez-le à partir de config/config.example.py:\n"
            f"  cp config/config.example.py config/config.py"
        )
    
    # Charger le fichier config.py
    import importlib.util
    spec = importlib.util.spec_from_file_location("config_module", config_file)
    config_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config_module)
    
    CONFIG = config_module.CONFIG
    SCOPES = config_module.SCOPES
    
    PERPLEXITY_API_KEY = CONFIG.get('PERPLEXITY_API_KEY')
    GEMINI_API_KEY = GEMINI_API_KEY or CONFIG.get('GEMINI_API_KEY', '')
    GROQ_API_KEY = GROQ_API_KEY or CONFIG.get('GROQ_API_KEY', '')
    NOTION_TOKEN = CONFIG['NOTION_TOKEN']
    NOTION_PARENT_PAGE_ID = CONFIG['NOTION_PARENT_PAGE_ID']
    NOTIFICATION_EMAIL = CONFIG['NOTIFICATION_EMAIL']
else:
    print('✅ Variables d\'environnement chargées (GitHub Actions mode)')
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# ==================== CHARGEMENT EMAIL SOURCES ====================
# Charger la liste des emails sources depuis un fichier texte
def load_email_sources():
    """Charge les adresses email des newsletters depuis email_sources.txt"""
    email_sources = []
    
    # Essayer d'abord le chemin relatif (GitHub Actions)
    sources_file = Path('email_sources.txt')
    if not sources_file.exists():
        # Sinon utiliser le chemin absolu (développement local)
        sources_file = BASE_DIR.parent.parent / 'email_sources.txt'
    
    if sources_file.exists():
        print(f'📧 Chargement des emails sources depuis: {sources_file}')
        with open(sources_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Ignorer les lignes vides et les commentaires
                if line and not line.startswith('#'):
                    email_sources.append(line)
        
        if email_sources:
            print(f'✅ {len(email_sources)} source(s) email chargée(s)')
            return email_sources
        else:
            print('⚠️  Aucune email source trouvée dans le fichier')
            return []
    else:
        print(f'⚠️  Fichier email_sources.txt non trouvé')
        print(f'   Créez-le à partir de email_sources.example.txt:')
        print(f'   cp email_sources.example.txt email_sources.txt')
        return []

EMAIL_SOURCES = load_email_sources()

# Créer un objet CONFIG pour compatibilité avec le reste du code
CONFIG = {
    'PERPLEXITY_API_KEY': PERPLEXITY_API_KEY,
    'GEMINI_API_KEY': GEMINI_API_KEY,
    'GROQ_API_KEY': GROQ_API_KEY,
    'NOTION_TOKEN': NOTION_TOKEN,
    'NOTION_PARENT_PAGE_ID': NOTION_PARENT_PAGE_ID,
    'NOTIFICATION_EMAIL': NOTIFICATION_EMAIL,
    'EMAIL_SOURCES': EMAIL_SOURCES
}

if not SCOPES:
    SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# ==================== FONCTIONS GMAIL ====================
def get_gmail_service():
    """Authentification et création du service Gmail"""
    print('🔐 Authentification Gmail...')
    
    creds = None
    token_path = BASE_DIR / 'token.json'
    
    # Mode GitHub Actions : utiliser les secrets
    if os.environ.get('GITHUB_ACTIONS') == 'true':
        print('📍 Mode GitHub Actions détecté')
        
        # Priorité 1 : Token OAuth pré-généré (stocké en secret)
        token_json_env = os.environ.get('GOOGLE_OAUTH_TOKEN_JSON')
        if token_json_env:
            print('✅ Token OAuth trouvé dans GOOGLE_OAUTH_TOKEN_JSON')
            import tempfile
            import json
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                f.write(token_json_env)
                temp_token_path = f.name
            
            try:
                creds = Credentials.from_authorized_user_file(temp_token_path, SCOPES)
                return build('gmail', 'v1', credentials=creds)
            finally:
                os.unlink(temp_token_path)
        
        # Priorité 2 : Credentials JSON avec refresh token
        google_credentials_json = os.environ.get('GOOGLE_CREDENTIALS_JSON')
        if not google_credentials_json:
            raise FileNotFoundError(
                "Ni GOOGLE_OAUTH_TOKEN_JSON ni GOOGLE_CREDENTIALS_JSON trouvés.\n"
                "Ajoutez l'un d'eux dans GitHub Settings → Secrets:\n"
                "- GOOGLE_OAUTH_TOKEN_JSON: Token OAuth pré-généré (recommandé)\n"
                "- GOOGLE_CREDENTIALS_JSON: fichier credentials.json avec refresh_token"
            )
        
        print('✅ Credentials JSON trouvées, tentative d\'authentification...')
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write(google_credentials_json)
            temp_credentials_path = f.name
        
        try:
            # Essayer d'abord le mode sans navigateur
            flow = InstalledAppFlow.from_client_secrets_file(
                temp_credentials_path, SCOPES)
            # Mode sans navigateur pour GitHub Actions
            creds = flow.run_local_server(port=0, open_browser=False)
            print('⚠️  Authentification manuelle requise. Visitez l\'URL ci-dessus.')
            return build('gmail', 'v1', credentials=creds)
        finally:
            os.unlink(temp_credentials_path)
    
    # Mode développement local
    print('📍 Mode développement local')
    
    # Essayer de charger le token existant
    if token_path.exists():
        print('✅ Token local trouvé, chargement...')
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # Si pas de credentials valides, on lance l'authentification
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print('🔄 Rafraîchissement du token...')
            creds.refresh(Request())
        else:
            credentials_file = BASE_DIR / 'credentials.json'
            if not credentials_file.exists():
                raise FileNotFoundError(
                    f"Fichier {credentials_file} non trouvé.\n"
                    f"Créez-le en suivant : https://developers.google.com/gmail/api/quickstart/python"
                )
            print('🌐 Ouverture du navigateur pour authentification...')
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_file), SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Sauvegarder les credentials
        with open(str(token_path), 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
        print('💾 Token sauvegardé')
    
    return build('gmail', 'v1', credentials=creds)


def fetch_newsletters(service):
    """Récupère les newsletters non lues des dernières 24h (max 2 par source)"""
    print('📧 Récupération des emails...')
    
    # Construire la requête de recherche
    from_queries = [f'from:{email}' for email in CONFIG['EMAIL_SOURCES']]
    query = f"({' OR '.join(from_queries)}) is:unread newer_than:1d"
    
    # Rechercher les messages
    results = service.users().messages().list(
        userId='me',
        q=query,
        maxResults=100
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print('✅ Aucun nouveau email trouvé')
        return []
    
    print(f'📩 {len(messages)} email(s) trouvé(s)')
    
    # Récupérer le contenu de chaque email
    emails = []
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    
    for message in messages:
        msg = service.users().messages().get(
            userId='me',
            id=message['id'],
            format='full'
        ).execute()
        
        # Extraire les headers
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        subject = headers.get('Subject', 'Sans sujet')
        from_email = headers.get('From', 'Inconnu')
        
        # Extraire le contenu
        content = ''
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        content = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html':
                    if 'data' in part['body']:
                        html_content = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        content = h2t.handle(html_content)
                        break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            content = base64.urlsafe_b64decode(
                msg['payload']['body']['data']
            ).decode('utf-8')
        
        # Limiter la longueur pour éviter les contenus trop longs
        content = content[:5000] if len(content) > 5000 else content
        
        emails.append({
            'id': message['id'],
            'from': from_email,
            'subject': subject,
            'content': content
        })
    
    # Limiter à 2 emails par source
    emails_by_source = {}
    for email in emails:
        from_addr = email['from']
        if from_addr not in emails_by_source:
            emails_by_source[from_addr] = []
        emails_by_source[from_addr].append(email)
    
    # Garder seulement les 2 derniers de chaque source
    filtered_emails = []
    for from_addr, email_list in emails_by_source.items():
        filtered_emails.extend(email_list[:2])  # Les premiers 2 (Gmail retourne les plus récents d'abord)
    
    print(f'📩 {len(filtered_emails)} email(s) sélectionné(s) après filtrage (max 2 par source)')
    
    return filtered_emails


def get_or_create_label(service, label_name):
    """Obtient ou crée un libellé Gmail"""
    # Récupérer la liste des libellés
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])
    
    # Chercher le libellé
    for label in labels:
        if label['name'].lower() == label_name.lower():
            return label['id']
    
    # Si le libellé n'existe pas, le créer
    print(f'  📝 Création du libellé "{label_name}"...')
    label_body = {
        'name': label_name,
        'labelListVisibility': 'labelShow',
        'messageListVisibility': 'show'
    }
    created_label = service.users().labels().create(userId='me', body=label_body).execute()
    return created_label['id']


def mark_emails_as_read_and_label(service, email_ids, label_name='newletterinnotion'):
    """Marque les emails comme lus, les déplace dans un libellé et les retire de la boite de réception"""
    print('✓ Marquage des emails comme lus...')
    
    # Obtenir ou créer le libellé
    label_id = get_or_create_label(service, label_name)
    
    # Appliquer les modifications
    service.users().messages().batchModify(
        userId='me',
        body={
            'ids': email_ids,
            'removeLabelIds': ['UNREAD', 'INBOX', 'IMPORTANT'],
            'addLabelIds': [label_id]
        }
    ).execute()
    
    print(f'✅ Emails marqués comme lus, étiquetés "{label_name}" et retirés de la boite de réception')


def send_notification(service, notion_url, synthesis_path, emails=None, notebooklm_url=None, synthesis_source='perplexity', synthesis_text=None):
    """Envoie un email de notification"""
    print('📬 Envoi de la notification...')

    # Bandeau source de la synthèse
    if synthesis_source == 'perplexity':
        source_banner = '<p style="background:#eafaf1;border-left:4px solid #2ecc71;padding:10px;margin:15px 0;">🤖 <strong>Synthèse générée par Perplexity AI</strong> (modèle sonar)</p>'
        subject_source = '🤖 Perplexity AI'
    elif synthesis_source == 'gemini':
        source_banner = '<p style="background:#e8f4fd;border-left:4px solid #3498db;padding:10px;margin:15px 0;">🤖 <strong>Synthèse générée par Google Gemini</strong> (modèle gemini-2.5-flash) — Perplexity indisponible</p>'
        subject_source = '🤖 Gemini (fallback)'
    elif synthesis_source == 'groq':
        source_banner = '<p style="background:#f0ebff;border-left:4px solid #8e44ad;padding:10px;margin:15px 0;">🤖 <strong>Synthèse générée par Groq</strong> (modèle llama-3.3-70b) — Perplexity et Gemini indisponibles</p>'
        subject_source = '🤖 Groq (fallback)'
    else:
        source_banner = '<p style="background:#fef9e7;border-left:4px solid #f39c12;padding:10px;margin:15px 0;">⚠️ <strong>Tous les services AI indisponibles — Contenu brut agrégé</strong> joint en pièce jointe. Chargez-le dans <strong>NotebookLM</strong> pour en faire une synthèse.</p>'
        subject_source = '📄 Contenu brut (AI indisponible)'

    # Construire la liste des emails traités
    emails_list_html = ''
    if emails:
        emails_list_html = '<h3>📧 Emails traités :</h3><ul>'
        for email in emails:
            from_addr = email.get('from', 'Inconnu')
            subject = email.get('subject', 'Sans sujet')
            # Limiter le texte si trop long
            subject_display = subject[:80] + '...' if len(subject) > 80 else subject
            emails_list_html += f'<li><strong>{from_addr}</strong><br><em>{subject_display}</em></li>'
        emails_list_html += '</ul><hr style="margin: 20px 0;">'
    
    notebooklm_section = ''
    if notebooklm_url:
        notebooklm_section = f'''
        <h3>🎙️ Créer un podcast avec NotebookLM :</h3>
        <ol>
            <li>Allez sur <a href="{notebooklm_url}">NotebookLM</a></li>
            <li>Créez un nouveau notebook</li>
            <li>✅ <strong>Fichier joint</strong> - Drag & drop directement dans NotebookLM !</li>
            <li>Cliquez sur "Audio Overview" pour générer le podcast</li>
        </ol>
        '''
    
    # Préparer le bloc de synthèse inline si disponible
    synthesis_html = ''
    if synthesis_text and synthesis_source in ('perplexity', 'gemini', 'groq'):
        import html as html_module
        # Convertir le markdown basique en HTML lisible
        escaped = html_module.escape(synthesis_text)
        # Titres ## → <h3>, ### → <h4>
        import re
        escaped = re.sub(r'^### (.+)$', r'<h4>\1</h4>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'^## (.+)$', r'<h3>\1</h3>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'^# (.+)$', r'<h2>\1</h2>', escaped, flags=re.MULTILINE)
        # Gras **texte**
        escaped = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', escaped)
        # Bullet points
        escaped = re.sub(r'^• (.+)$', r'<li>\1</li>', escaped, flags=re.MULTILINE)
        escaped = re.sub(r'^- (.+)$', r'<li>\1</li>', escaped, flags=re.MULTILINE)
        # Sauts de ligne
        escaped = escaped.replace('\n', '<br>')
        synthesis_html = f'''
        <hr style="margin: 20px 0;">
        <h3>📋 Synthèse complète :</h3>
        <div style="background:#f9f9f9;border:1px solid #e0e0e0;border-radius:6px;padding:20px;margin:10px 0;font-size:14px;line-height:1.7;">
            {escaped}
        </div>'''

    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif;">
        <h2 style="color: #2ecc71;">✅ Votre synthèse quotidienne est prête !</h2>

        {source_banner}

        <p><strong>📝 Notion:</strong> <a href="{notion_url}">Voir la page Notion</a></p>
        <p><strong>📎 Fichier synthèse:</strong> Joint à cet email</p>

        <hr style="margin: 20px 0;">

        {emails_list_html}

        {synthesis_html}

        <hr style="margin: 20px 0;">

        <h3>📋 Ressources :</h3>
        <ul>
            <li><a href="{notion_url}">📖 Lire la synthèse Notion</a> - Accès rapide et structuré</li>
            <li>📎 <strong>Fichier texte en pièce jointe</strong> - Prêt à copier-coller dans NotebookLM</li>
        </ul>

        {notebooklm_section}

        <p style="color: #7f8c8d; margin-top: 30px;">
            <em>🤖 Généré automatiquement par votre assistant newsletter</em>
        </p>
    </body>
    </html>
    """
    
    # Créer un message multipart pour inclure la pièce jointe
    message = MIMEMultipart()
    message['from'] = 'me'
    message['to'] = CONFIG['NOTIFICATION_EMAIL']
    message['subject'] = f'✅ Synthèse newsletter — {subject_source}'
    
    # Ajouter le contenu HTML
    message.attach(MIMEText(html_content, 'html'))
    
    # Ajouter la pièce jointe si le fichier existe
    if os.path.exists(synthesis_path):
        try:
            filename = os.path.basename(synthesis_path)
            with open(synthesis_path, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={filename}')
            message.attach(part)
            print(f'  📎 Pièce jointe ajoutée: {filename}')
        except Exception as e:
            print(f'  ⚠️  Erreur lors de l\'ajout de la pièce jointe: {e}')
    
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    service.users().messages().send(
        userId='me',
        body={'raw': raw_message}
    ).execute()
    
    print('✅ Notification envoyée avec pièce jointe')


# ==================== FONCTION PERPLEXITY ====================
def synthesize_with_perplexity(emails, max_retries=3):
    """Génère une synthèse avec Perplexity AI"""
    import time
    print('🤖 Synthèse avec Perplexity...')
    
    # Vérifier que la clé API est disponible
    api_key = CONFIG.get('PERPLEXITY_API_KEY', '').strip()
    if not api_key:
        raise Exception('ERREUR: PERPLEXITY_API_KEY n\'est pas configurée. Vérifiez votre fichier .env')
    
    # Préparer le contenu (troncature déjà appliquée en amont dans fetch_newsletters)
    emails_text = '\n\n'.join([
        f"### {email['from']} - {email['subject']}\n\n{email['content']}\n\n---"
        for email in emails
    ])

    prompt = f"""Tu es un assistant expert qui synthétise des newsletters en français de manière très structurée et détaillée.
Les newsletters peuvent couvrir des domaines variés : tech, cybersécurité, santé, healthcare, etc.
Adapte le vocabulaire et les sections thématiques au contenu reçu.

Crée une synthèse COMPLÈTE et NON TRONQUÉE des newsletters reçues aujourd'hui en suivant STRICTEMENT ce format :

## SYNTHÈSE STRUCTURÉE DES NEWSLETTERS

**Source de la synthèse : Perplexity AI (modèle sonar)**

Pour chaque thème principal trouvé, crée une section avec :
- **Titre du thème** (ex: Cybersécurité Santé, Ransomware, IA Médicale, Réglementation, etc.)
- Une **introduction** courte présentant le sujet
- Une liste de **points clés** (utilise • pour chaque point important)
- Les **éléments à retenir** avec impact ou implications
- Les **chiffres ou données** pertinents s'il y en a

Structure générale demandée :
1. **Résumé exécutif** (3-5 points clés essentiels à retenir)
2. **Sections thématiques principales** (groupées par domaine/sujet — traite TOUS les sujets, ne coupe pas)
3. **Tendances émergentes** (si identifiées)
4. **Impacts et actions recommandées** (ce que cela signifie concrètement)

IMPORTANT : Ne tronque pas la synthèse. Traite intégralement CHAQUE newsletter reçue.
Sois très détaillé, utilise des sous-titres clairs, et rends le texte facile à scanner.
Ajoute des emojis pertinents pour améliorer la lisibilité.

NEWSLETTERS À SYNTHÉTISER :
{emails_text}"""

    # Appel API Perplexity avec retry et gestion d'erreurs améliorée
    for attempt in range(max_retries):
        try:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'NewsletterAutomation/1.0'
            }

            payload = {
                'model': 'sonar',
                'messages': [
                    {
                        'role': 'system',
                        'content': 'Tu es un assistant qui synthétise des newsletters (tech, cybersécurité, santé, etc.) en français de manière détaillée, structurée et COMPLÈTE sans jamais tronquer le contenu.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'max_tokens': 8000,
                'temperature': 0.2
            }
            
            print(f'  Tentative {attempt + 1}/{max_retries}...')
            response = requests.post(
                'https://api.perplexity.ai/chat/completions',
                headers=headers,
                json=payload,
                timeout=60
            )
            
            # Afficher le statut
            print(f'  Réponse API: HTTP {response.status_code}')
            
            if response.status_code == 401:
                raise Exception('ERREUR 401: Authentification échouée. Vérifiez votre PERPLEXITY_API_KEY')
            elif response.status_code == 403:
                raise Exception('ERREUR 403: Accès refusé. Vérifiez les permissions de votre clé API')
            elif response.status_code == 429:
                print('  Limite de débit atteinte, attente 30s...')
                time.sleep(30)
                continue
            elif response.status_code == 500:
                print('  Erreur serveur Perplexity, nouvelle tentative...')
                time.sleep(5)
                continue
            elif response.status_code != 200:
                print(f'  Erreur HTTP {response.status_code}')
                print(f'  Réponse: {response.text}')
                raise Exception(f'Erreur Perplexity API: {response.status_code} - {response.text}')
            
            data = response.json()
            
            # Vérifier le format de la réponse
            if 'choices' not in data or not data['choices']:
                raise Exception(f'Format de réponse invalide: {data}')
            
            synthesis = data['choices'][0]['message']['content']
            
            print('✅ Synthèse générée avec succès')
            return synthesis
            
        except requests.exceptions.Timeout:
            print(f'  Timeout (tentative {attempt + 1}/{max_retries})')
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise Exception('Timeout: Perplexity API n\'a pas répondu à temps')
        except requests.exceptions.ConnectionError as e:
            print(f'  Erreur de connexion: {e}')
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
    
    raise Exception('Impossible de contacter Perplexity API après plusieurs tentatives')


# ==================== FONCTION GEMINI (fallback 1) ====================
def synthesize_with_gemini(emails):
    """Génère une synthèse avec Google Gemini (fallback si Perplexity indisponible)"""
    import time
    print('🤖 Synthèse avec Gemini...')

    api_key = CONFIG.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        raise Exception('GEMINI_API_KEY non configurée')

    emails_text = '\n\n'.join([
        f"### {email['from']} - {email['subject']}\n\n{email['content'][:8000]}\n\n---"
        for email in emails
    ])

    prompt = f"""Tu es un assistant expert qui synthétise des newsletters en français de manière très structurée et détaillée.
Les newsletters peuvent couvrir des domaines variés : tech, cybersécurité, santé, healthcare, etc.
Adapte le vocabulaire et les sections thématiques au contenu reçu.

Crée une synthèse COMPLÈTE et NON TRONQUÉE des newsletters reçues aujourd'hui en suivant STRICTEMENT ce format :

## SYNTHÈSE STRUCTURÉE DES NEWSLETTERS

**Source de la synthèse : Google Gemini**

Pour chaque thème principal trouvé, crée une section avec :
- **Titre du thème** (ex: Cybersécurité Santé, Ransomware, IA Médicale, Réglementation, etc.)
- Une **introduction** courte présentant le sujet
- Une liste de **points clés** (utilise • pour chaque point important)
- Les **éléments à retenir** avec impact ou implications
- Les **chiffres ou données** pertinents s'il y en a

Structure générale demandée :
1. **Résumé exécutif** (3-5 points clés essentiels à retenir)
2. **Sections thématiques principales** (groupées par domaine/sujet — traite TOUS les sujets, ne coupe pas)
3. **Tendances émergentes** (si identifiées)
4. **Impacts et actions recommandées** (ce que cela signifie concrètement)

IMPORTANT : Ne tronque pas la synthèse. Traite intégralement CHAQUE newsletter reçue.
Sois très détaillé, utilise des sous-titres clairs, et rends le texte facile à scanner.
Ajoute des emojis pertinents pour améliorer la lisibilité.

NEWSLETTERS À SYNTHÉTISER :
{emails_text}"""

    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    payload = {
        'contents': [{'role': 'user', 'parts': [{'text': prompt}]}],
        'generationConfig': {
            'maxOutputTokens': 8000,
            'temperature': 0.2
        }
    }

    for attempt in range(3):
        try:
            print(f'  Tentative {attempt + 1}/3...')
            response = requests.post(url, json=payload, timeout=60)
            print(f'  Réponse API: HTTP {response.status_code}')

            if response.status_code == 429:
                print('  Limite de débit atteinte, attente 30s...')
                time.sleep(30)
                continue
            elif response.status_code != 200:
                raise Exception(f'Erreur Gemini API: {response.status_code} - {response.text}')

            data = response.json()
            synthesis = data['candidates'][0]['content']['parts'][0]['text']
            print('✅ Synthèse Gemini générée avec succès')
            return synthesis

        except requests.exceptions.Timeout:
            print(f'  Timeout (tentative {attempt + 1}/3)')
            if attempt < 2:
                time.sleep(5)
                continue
            raise Exception('Timeout: Gemini API n\'a pas répondu à temps')
        except requests.exceptions.ConnectionError as e:
            if attempt < 2:
                time.sleep(5)
                continue
            raise

    raise Exception('Impossible de contacter Gemini API après plusieurs tentatives')


# ==================== FONCTION GROQ (fallback 2) ====================
def synthesize_with_groq(emails):
    """Génère une synthèse avec Groq (fallback gratuit si Perplexity et Gemini indisponibles)"""
    import time
    print('🤖 Synthèse avec Groq...')

    api_key = CONFIG.get('GROQ_API_KEY', '').strip()
    if not api_key:
        raise Exception('GROQ_API_KEY non configurée')

    emails_text = '\n\n'.join([
        f"### {email['from']} - {email['subject']}\n\n{email['content'][:6000]}\n\n---"
        for email in emails
    ])

    prompt = f"""Tu es un assistant expert qui synthétise des newsletters en français de manière très structurée et détaillée.
Les newsletters peuvent couvrir des domaines variés : tech, cybersécurité, santé, healthcare, etc.
Adapte le vocabulaire et les sections thématiques au contenu reçu.

Crée une synthèse COMPLÈTE et NON TRONQUÉE des newsletters reçues aujourd'hui en suivant STRICTEMENT ce format :

## SYNTHÈSE STRUCTURÉE DES NEWSLETTERS

**Source de la synthèse : Groq (llama-3.3-70b)**

Pour chaque thème principal trouvé, crée une section avec :
- **Titre du thème** (ex: Cybersécurité Santé, Ransomware, IA Médicale, Réglementation, etc.)
- Une **introduction** courte présentant le sujet
- Une liste de **points clés** (utilise • pour chaque point important)
- Les **éléments à retenir** avec impact ou implications
- Les **chiffres ou données** pertinents s'il y en a

Structure générale demandée :
1. **Résumé exécutif** (3-5 points clés essentiels à retenir)
2. **Sections thématiques principales** (groupées par domaine/sujet — traite TOUS les sujets, ne coupe pas)
3. **Tendances émergentes** (si identifiées)
4. **Impacts et actions recommandées** (ce que cela signifie concrètement)

NEWSLETTERS À SYNTHÉTISER :
{emails_text}"""

    for attempt in range(3):
        try:
            print(f'  Tentative {attempt + 1}/3...')
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'llama-3.3-70b-versatile',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'Tu es un assistant qui synthétise des newsletters en français de manière détaillée, structurée et COMPLÈTE sans jamais tronquer le contenu.'
                        },
                        {'role': 'user', 'content': prompt}
                    ],
                    'max_tokens': 8000,
                    'temperature': 0.2
                },
                timeout=60
            )
            print(f'  Réponse API: HTTP {response.status_code}')

            if response.status_code == 429:
                print('  Limite de débit atteinte, attente 30s...')
                time.sleep(30)
                continue
            elif response.status_code != 200:
                raise Exception(f'Erreur Groq API: {response.status_code} - {response.text}')

            data = response.json()
            synthesis = data['choices'][0]['message']['content']
            print('✅ Synthèse Groq générée avec succès')
            return synthesis

        except requests.exceptions.Timeout:
            print(f'  Timeout (tentative {attempt + 1}/3)')
            if attempt < 2:
                time.sleep(5)
                continue
            raise Exception('Timeout: Groq API n\'a pas répondu à temps')
        except requests.exceptions.ConnectionError as e:
            if attempt < 2:
                time.sleep(5)
                continue
            raise

    raise Exception('Impossible de contacter Groq API après plusieurs tentatives')


# ==================== FONCTION FALLBACK RAW (pour NotebookLM) ====================
def aggregate_raw_content(emails):
    """Agrège le contenu brut des emails parsés pour traitement manuel dans NotebookLM"""
    from datetime import date
    print('📄 Agrégation du contenu brut pour NotebookLM...')

    today = date.today().strftime('%d/%m/%Y')
    header = f'# CONTENU BRUT DES NEWSLETTERS - {today}\n\n'
    header += f'Nombre de newsletters: {len(emails)}\n\n'
    header += '---\n\n'

    sections = []
    for i, email in enumerate(emails, 1):
        section = f'## [{i}] {email["subject"]}\n'
        section += f'**De:** {email["from"]}\n\n'
        section += email['content'].strip()
        section += '\n\n---'
        sections.append(section)

    raw_text = header + '\n\n'.join(sections)
    print(f'✅ Contenu brut agrégé ({len(emails)} newsletters, {len(raw_text)} caractères)')
    return raw_text


# ==================== FONCTION SYNTHÈSE AVEC FALLBACK ====================
def synthesize_with_fallback(emails):
    """Cascade de synthèse : Perplexity → Gemini → Groq → contenu brut (NotebookLM).
    Retourne un tuple (synthesis, source) où source vaut 'perplexity', 'gemini', 'groq' ou 'raw'."""
    if CONFIG.get('PERPLEXITY_API_KEY', '').strip():
        try:
            return synthesize_with_perplexity(emails), 'perplexity'
        except Exception as e:
            print(f'⚠️  Perplexity a échoué: {e}')
            print('🔄 Basculement sur Gemini...')
    else:
        print('ℹ️  PERPLEXITY_API_KEY non configurée, tentative Gemini...')

    if CONFIG.get('GEMINI_API_KEY', '').strip():
        try:
            return synthesize_with_gemini(emails), 'gemini'
        except Exception as e:
            print(f'⚠️  Gemini a échoué: {e}')
            print('🔄 Basculement sur Groq...')
    else:
        print('ℹ️  GEMINI_API_KEY non configurée, tentative Groq...')

    if CONFIG.get('GROQ_API_KEY', '').strip():
        try:
            return synthesize_with_groq(emails), 'groq'
        except Exception as e:
            print(f'⚠️  Groq a échoué: {e}')
            print('🔄 Basculement sur agrégation brute pour NotebookLM...')
    else:
        print('ℹ️  GROQ_API_KEY non configurée, agrégation brute pour NotebookLM.')

    return aggregate_raw_content(emails), 'raw'


# ==================== FONCTION NOTION ====================
def create_notion_page(synthesis):
    """Crée une page Notion avec la synthèse"""
    print('📝 Création de la page Notion...')
    
    notion = Client(auth=CONFIG['NOTION_TOKEN'])
    
    # Formater la date en français avec heure et minutes
    import locale
    try:
        locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_TIME, 'fr_FR')
        except:
            pass
    
    now = datetime.now()
    date_fr = now.strftime('%A %d %B %Y').capitalize()
    today = f"{date_fr} - {now.strftime('%H:%M')}"
    
    # Découper la synthèse en blocs pour Notion
    paragraphs = [p.strip() for p in synthesis.split('\n\n') if p.strip()]
    
    # Créer les blocs de contenu
    children = [
        {
            'object': 'block',
            'type': 'heading_1',
            'heading_1': {
                'rich_text': [{'type': 'text', 'text': {'content': '📰 Synthèse quotidienne'}}]
            }
        }
    ]
    
    for paragraph in paragraphs:
        children.append({
            'object': 'block',
            'type': 'paragraph',
            'paragraph': {
                'rich_text': [{'type': 'text', 'text': {'content': paragraph}}]
            }
        })
    
    # Créer la page avec les 100 premiers blocs (limite API Notion)
    page = notion.pages.create(
        parent={'page_id': CONFIG['NOTION_PARENT_PAGE_ID']},
        properties={
            'title': {
                'title': [
                    {'text': {'content': f'Newsletter - {today}'}}
                ]
            }
        },
        children=children[:100]
    )

    # Ajouter les blocs restants par tranches de 100
    for i in range(100, len(children), 100):
        notion.blocks.children.append(
            block_id=page['id'],
            children=children[i:i + 100]
        )

    print('✅ Page Notion créée')
    return page['url']


# ==================== FONCTION SAUVEGARDE ====================
def save_synthesis(synthesis):
    """Sauvegarde la synthèse dans un fichier"""
    synth_dir = BASE_DIR / 'syntheses'
    synth_dir.mkdir(parents=True, exist_ok=True)

    date_str = datetime.now().strftime('%Y-%m-%d')
    filepath = synth_dir / f'synthese-{date_str}.txt'

    with open(str(filepath), 'w', encoding='utf-8') as f:
        f.write(f"# Synthèse Newsletter - {date_str}\n\n")
        f.write(synthesis)

    return str(filepath.resolve())


# ==================== FONCTION NOTEBOOKLM ====================
def create_notebooklm_podcast(synthesis_path):
    """
    Génère un lien pour uploader la synthèse dans NotebookLM
    
    NOTE: NotebookLM n'a pas d'API REST publique. Cette fonction prépare
    simplement le fichier et fournit des instructions pour l'upload manuel.
    """
    print('🎙️ Préparation pour NotebookLM...')
    
    try:
        # Vérifier que le fichier existe
        if not os.path.exists(synthesis_path):
            print('⚠️  Fichier de synthèse non trouvé')
            return None
        
        # Informer l'utilisateur
        file_size = os.path.getsize(synthesis_path)
        print(f'  📄 Fichier prêt: {synthesis_path}')
        print(f'  📊 Taille: {file_size / 1024:.1f} KB')
        print(f'  ✅ Le fichier est prêt pour NotebookLM')
        
        # Retourner l'URL de NotebookLM
        notebooklm_url = 'https://notebooklm.google.com'
        return notebooklm_url
        
    except Exception as e:
        print(f'⚠️  Erreur lors de la préparation: {e}')
        return None


# ==================== FONCTION PRINCIPALE ====================
def main():
    """Fonction principale du script"""
    try:
        print('🚀 Démarrage de l\'automatisation...\n')
        
        # 1. Vérifier la configuration
        print('📋 Vérification de la configuration...')
        if not CONFIG.get('PERPLEXITY_API_KEY'):
            print('ℹ️  PERPLEXITY_API_KEY non configurée — le contenu brut sera agrégé pour NotebookLM en cas d\'échec')
        if not CONFIG.get('NOTION_TOKEN'):
            raise Exception('NOTION_TOKEN non configuré. Ajoutez-le à votre fichier .env')
        if not CONFIG.get('NOTION_PARENT_PAGE_ID'):
            raise Exception('NOTION_PARENT_PAGE_ID non configuré. Ajoutez-le à votre fichier .env')
        if not CONFIG.get('NOTIFICATION_EMAIL'):
            raise Exception('NOTIFICATION_EMAIL non configuré. Ajoutez-le à votre fichier .env')
        if not CONFIG.get('EMAIL_SOURCES'):
            raise Exception('EMAIL_SOURCES non configuré. Ajoutez-le à votre fichier .env')
        print('✅ Configuration validée\n')
        
        # 2. Connexion Gmail
        gmail_service = get_gmail_service()
        
        # 3. Récupération des newsletters
        emails = fetch_newsletters(gmail_service)
        
        if not emails:
            print('ℹ️  Aucune newsletter à traiter aujourd\'hui')
            return
        
        # 4. Synthèse avec Perplexity (fallback contenu brut pour NotebookLM si indisponible)
        synthesis, synthesis_source = synthesize_with_fallback(emails)

        # 5. Sauvegarde de la synthèse
        synthesis_path = save_synthesis(synthesis)
        print(f'💾 Synthèse sauvegardée: {synthesis_path}')

        # 6. Création de la page Notion
        notion_url = create_notion_page(synthesis)

        # 7. Marquer les emails comme lus et les étiqueter
        mark_emails_as_read_and_label(gmail_service, [e['id'] for e in emails])

        # 8. Créer le podcast NotebookLM
        notebooklm_url = create_notebooklm_podcast(synthesis_path)

        # 9. Envoyer la notification avec la liste des mails
        send_notification(gmail_service, notion_url, synthesis_path, emails, notebooklm_url, synthesis_source, synthesis_text=synthesis)
        
        print('\n🎉 Automatisation terminée avec succès !')
        print(f'📊 {len(emails)} newsletter(s) traitée(s)')
        print(f'🔗 Page Notion: {notion_url}')
        print(f'📄 Fichier: {synthesis_path}')
        
    except Exception as e:
        print(f'\n❌ Erreur: {str(e)}')
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()