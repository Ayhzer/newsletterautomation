#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Healthcare Watch Runner - intégré dans newsletterautomation-private
Interroge Perplexity selon les prompts définis dans config/prompts.yaml,
crée des pages Notion, envoie des notifications email, et suit last_run.json.

Ce script est indépendant de newsletter_automation.py et utilise les mêmes
secrets GitHub déjà configurés dans ce dépôt. Aucun secret supplémentaire requis.
"""

import os
import sys
import json
import yaml
import base64
import hashlib
import importlib.util
import re
from pathlib import Path
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Tuple
import requests
from notion_client import Client
import time
import pytz
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# Force UTF-8 encoding on Windows (identique à newsletter_automation.py)
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# ==================== CONSTANTS ====================
# BASE_DIR = src/newsletter_automation/
# PROJECT_DIR = racine du dépôt (même logique que healthcare_watch.py)
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR.parent.parent
CONFIG_DIR = PROJECT_DIR / 'config'
OUTPUT_DIR = PROJECT_DIR / 'data' / 'output'

# Même scope que newsletter_automation.py (gmail.modify est un superset de gmail.send)
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']


# ==================== CONFIGURATION LOADING ====================

def load_config() -> Dict:
    """Charge la configuration YAML et les secrets depuis les variables d'environnement.
    Si les variables d'environnement sont absentes (dev local), tente un fallback sur config.py.
    """
    print('Chargement de la configuration Healthcare Watch...')

    # Charger le fichier YAML
    config_file = CONFIG_DIR / 'prompts.yaml'
    if not config_file.exists():
        config_file = CONFIG_DIR / 'prompts.example.yaml'
        if not config_file.exists():
            raise FileNotFoundError(
                f"Fichier config/prompts.yaml non trouvé à {CONFIG_DIR}\n"
                "Créez-le à partir de config/prompts.example.yaml"
            )
        print(f'ATTENTION: Utilisation de {config_file.name}')

    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Charger les secrets depuis les variables d'environnement
    tavily_key = os.environ.get('TAVILY_API_KEY', '')
    gemini_key = os.environ.get('GEMINI_API_KEY', '')
    groq_key = os.environ.get('GROQ_API_KEY', '')
    notion_token = os.environ.get('NOTION_TOKEN', '')
    notion_parent_page_id = os.environ.get('NOTION_PARENT_PAGE_ID', '')
    notification_email = os.environ.get('NOTIFICATION_EMAIL', '')

    # Fallback sur config.py si variables d'environnement manquantes (dev local)
    if not notion_token:
        print('Variables env manquantes, tentative de chargement config.py...')
        config_py = CONFIG_DIR / 'config.py'
        if config_py.exists():
            spec = importlib.util.spec_from_file_location("config_module", config_py)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            cfg = config_module.CONFIG
            tavily_key = tavily_key or cfg.get('TAVILY_API_KEY', '')
            gemini_key = gemini_key or cfg.get('GEMINI_API_KEY', '')
            groq_key = groq_key or cfg.get('GROQ_API_KEY', '')
            notion_token = notion_token or cfg.get('NOTION_TOKEN', '')
            notion_parent_page_id = notion_parent_page_id or cfg.get('NOTION_PARENT_PAGE_ID', '')
            notification_email = notification_email or cfg.get('NOTIFICATION_EMAIL', '')

    config['secrets'] = {
        'TAVILY_API_KEY': tavily_key,
        'GEMINI_API_KEY': gemini_key,
        'GROQ_API_KEY': groq_key,
        'NOTION_TOKEN': notion_token,
        'NOTION_PARENT_PAGE_ID': notion_parent_page_id,
        'NOTIFICATION_EMAIL': notification_email,
        'GOOGLE_OAUTH_TOKEN_JSON': os.environ.get('GOOGLE_OAUTH_TOKEN_JSON', ''),
    }

    # Valider les secrets requis
    if not notion_token:
        raise ValueError("Secrets manquants: NOTION_TOKEN")
    if not tavily_key and not gemini_key:
        print('ATTENTION: TAVILY_API_KEY et GEMINI_API_KEY non configurées — les rapports seront indisponibles')

    # Vérifier Gmail API seulement si notifications activées
    notifications_enabled = config.get('general', {}).get('notifications', {}).get('enabled', False)
    if notifications_enabled:
        gmail_required = ['NOTIFICATION_EMAIL', 'GOOGLE_OAUTH_TOKEN_JSON']
        missing_gmail = [s for s in gmail_required if not config['secrets'].get(s)]
        if missing_gmail:
            print(f'ATTENTION: Notifications activées mais secrets Gmail manquants: {", ".join(missing_gmail)}')
            print('Les notifications email seront désactivées.')
            config['general']['notifications']['enabled'] = False

    print('Configuration Healthcare Watch chargée')
    return config


# ==================== SCHEDULING ====================

def should_run_prompt(prompt_key: str, prompt_config: Dict, last_run_file: Path) -> bool:
    """Vérifie si un prompt doit être exécuté selon sa fréquence.
    Si FORCE_RUN=true est défini en variable d'environnement, ignore les fréquences.
    """
    if not prompt_config.get('enabled', False):
        return False

    # Mode force : ignore les fréquences (utile pour les tests)
    if os.environ.get('FORCE_RUN', '').lower() == 'true':
        print(f'  FORCE_RUN activé, exécution forcée de {prompt_key}')
        return True

    frequency = prompt_config.get('frequency', 'daily')

    run_history = {}
    if last_run_file.exists():
        with open(last_run_file, 'r') as f:
            run_history = json.load(f)

    last_run = run_history.get(prompt_key)
    if not last_run:
        print(f'  Première exécution de {prompt_key}')
        return True

    # Compatibilité : ancien format { "last_run": "...", ... } ou nouveau format string ISO directe
    if isinstance(last_run, dict):
        last_run = last_run.get('last_run', '')
    if not last_run or not isinstance(last_run, str):
        print(f'  Format last_run invalide pour {prompt_key}, exécution forcée')
        return True

    try:
        last_run_date = datetime.fromisoformat(last_run)
    except (ValueError, TypeError) as e:
        print(f'  Date last_run invalide pour {prompt_key} ({last_run!r}): {e}, exécution forcée')
        return True
    now = datetime.now()
    diff = now - last_run_date
    total_seconds = diff.total_seconds()

    if frequency == 'hourly' and total_seconds >= 3600:
        return True
    elif frequency == 'daily' and total_seconds >= 86400:
        return True
    elif frequency == '3days' and total_seconds >= 259200:
        return True
    elif frequency == 'weekly' and total_seconds >= 604800:
        return True
    elif frequency == 'monthly' and diff.days >= 30:
        return True

    return False


def update_last_run(prompt_key: str, last_run_file: Path, content: str = None):
    """Met à jour la date de dernière exécution d'un prompt, et optionnellement le hash/extrait du contenu."""
    run_history = {}
    if last_run_file.exists():
        with open(last_run_file, 'r') as f:
            run_history = json.load(f)

    run_history[prompt_key] = datetime.now().isoformat()

    if content is not None:
        run_history[f'{prompt_key}__hash'] = hashlib.sha256(content.encode('utf-8')).hexdigest()
        run_history[f'{prompt_key}__snippet'] = content[:1000]

    last_run_file.parent.mkdir(parents=True, exist_ok=True)
    with open(last_run_file, 'w') as f:
        json.dump(run_history, f, indent=2)


def get_previous_content(prompt_key: str, last_run_file: Path) -> Tuple[Optional[str], Optional[str]]:
    """Retourne (hash_précédent, snippet_précédent) ou (None, None) si absent.
    Gère la compatibilité avec l'ancien format imbriqué { prompt_key: { content_hash, content_text } }.
    """
    if not last_run_file.exists():
        return None, None
    with open(last_run_file, 'r') as f:
        run_history = json.load(f)

    # Nouveau format : clés plates {prompt_key}__hash / {prompt_key}__snippet
    prev_hash = run_history.get(f'{prompt_key}__hash')
    prev_snippet = run_history.get(f'{prompt_key}__snippet')

    # Ancien format imbriqué : { prompt_key: { "content_hash": ..., "content_text": ... } }
    if prev_hash is None:
        old_entry = run_history.get(prompt_key)
        if isinstance(old_entry, dict):
            prev_hash = old_entry.get('content_hash')
            prev_snippet = old_entry.get('content_text', '')[:1000] if old_entry.get('content_text') else None

    return prev_hash, prev_snippet


# ==================== LLM BACKENDS ====================

_SYSTEM_PROMPT_FR = (
    'Tu es un expert en veille réglementaire et cybersécurité dans le domaine de la santé en France. '
    'Synthétise les informations fournies en Markdown structuré, lisible et intégrable dans Notion.'
)


def _api_options(options: Dict) -> Dict:
    """Filtre les clés internes (_*) avant envoi aux APIs."""
    return {k: v for k, v in (options or {}).items() if not k.startswith('_')}


def query_tavily(query: str, config: Dict, options: Dict = None) -> dict:
    """Interroge l'API Tavily. Retourne {'answer': str, 'results': list}."""
    api_key = config['secrets']['TAVILY_API_KEY']
    opts = _api_options(options)
    payload = {
        'api_key': api_key,
        'query': query,
        'include_answer': True,
        'include_raw_content': False,
        'max_results': opts.get('max_results', 8),
        'search_depth': opts.get('search_depth', 'basic'),
        'topic': opts.get('topic', 'news'),
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'  Appel Tavily (tentative {attempt + 1}/{max_retries})...')
            response = requests.post('https://api.tavily.com/search', json=payload, timeout=30)
            if response.status_code == 401:
                raise ValueError('Authentification Tavily échouée (401)')
            elif response.status_code == 429:
                print('  Limite de débit Tavily, attente 30s...')
                time.sleep(30)
                continue
            elif response.status_code >= 500:
                print('  Erreur serveur Tavily, nouvelle tentative...')
                time.sleep(5)
                continue
            elif response.status_code != 200:
                raise ValueError(f'Erreur API Tavily: {response.status_code} - {response.text}')
            print('  Réponse reçue de Tavily')
            return response.json()
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise TimeoutError('Timeout Tavily API')
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
    raise Exception('Impossible de contacter Tavily API après 3 tentatives')


def format_tavily_context(data: dict) -> str:
    """Formate la réponse Tavily en Markdown pour Notion."""
    lines = []
    answer = data.get('answer', '').strip()
    if answer:
        lines.append('## Synthèse Tavily\n')
        lines.append(answer)
        lines.append('')
    results = data.get('results', [])
    if results:
        lines.append('## Sources\n')
        for r in results:
            title = r.get('title', 'Sans titre')
            url = r.get('url', '')
            content = r.get('content', '')[:300].strip()
            lines.append(f'### {title}')
            if url:
                lines.append(f'> {url}')
            if content:
                lines.append(content)
            lines.append('')
    return '\n'.join(lines)


def query_gemini(system_prompt: str, user_content: str, config: Dict, options: Dict = None) -> str:
    """Synthèse via Gemini 2.5 Flash."""
    api_key = config['secrets']['GEMINI_API_KEY']
    if not api_key:
        raise ValueError("GEMINI_API_KEY n'est pas configurée")
    opts = _api_options(options)
    url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}'
    payload = {
        'contents': [{'parts': [{'text': f'{system_prompt}\n\n{user_content}'}]}],
        'generationConfig': {
            'maxOutputTokens': opts.get('max_tokens', 8192),
            'temperature': opts.get('temperature', 0.3)
        }
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'  Appel Gemini (tentative {attempt + 1}/{max_retries})...')
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code == 429:
                print('  Limite de débit Gemini, attente 65s...')
                time.sleep(65)
                continue
            elif response.status_code >= 500:
                time.sleep(5)
                continue
            elif response.status_code != 200:
                raise ValueError(f'Erreur API Gemini: {response.status_code} - {response.text}')
            data = response.json()
            candidate = data['candidates'][0]
            text = candidate['content']['parts'][0]['text']
            finish_reason = candidate.get('finishReason', 'UNKNOWN')
            if finish_reason == 'MAX_TOKENS':
                print('  AVERTISSEMENT: Gemini a atteint MAX_TOKENS — réponse peut être tronquée')
            print(f'  Réponse reçue de Gemini (finishReason: {finish_reason})')
            return text
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise TimeoutError('Timeout Gemini API')
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
    raise Exception('Impossible de contacter Gemini API après 3 tentatives')


def query_groq(system_prompt: str, user_content: str, config: Dict, options: Dict = None) -> str:
    """Synthèse via Groq (fallback, OpenAI-compatible)."""
    api_key = config['secrets']['GROQ_API_KEY']
    if not api_key:
        raise ValueError("GROQ_API_KEY n'est pas configurée")
    opts = _api_options(options)
    payload = {
        'model': 'llama-3.3-70b-versatile',
        'messages': [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_content}
        ],
        'max_tokens': opts.get('max_tokens', 2000),
        'temperature': opts.get('temperature', 0.3)
    }
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f'  Appel Groq (tentative {attempt + 1}/{max_retries})...')
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
                json=payload, timeout=60
            )
            if response.status_code == 429:
                print('  Limite de débit Groq, attente 30s...')
                time.sleep(30)
                continue
            elif response.status_code >= 500:
                time.sleep(5)
                continue
            elif response.status_code != 200:
                raise ValueError(f'Erreur API Groq: {response.status_code} - {response.text}')
            text = response.json()['choices'][0]['message']['content']
            print('  Réponse reçue de Groq')
            return text
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise TimeoutError('Timeout Groq API')
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(5)
                continue
            raise
    raise Exception('Impossible de contacter Groq API après 3 tentatives')


def query_with_fallback(prompt: str, config: Dict, options: Dict = None) -> Tuple[str, str]:
    """Recherche Tavily + synthèse LLM avec cascade Tavily→Gemini→Groq.
    Retourne un tuple (synthesis, source)."""
    opts = options or {}
    prompt_cfg = opts.get('_prompt_config', {})
    search_query = prompt_cfg.get('search_query', prompt[:200])

    # 1. Tavily search
    if config['secrets'].get('TAVILY_API_KEY', '').strip():
        try:
            tavily_data = query_tavily(search_query, config, opts)
            tavily_context = format_tavily_context(tavily_data)
            user_content = f'{tavily_context}\n\n---\n\n{prompt}'

            # 2a. Gemini synthesis
            if config['secrets'].get('GEMINI_API_KEY', '').strip():
                try:
                    synthesis = query_gemini(_SYSTEM_PROMPT_FR, user_content, config, opts)
                    return synthesis, 'tavily+gemini'
                except Exception as e:
                    print(f'  Gemini échoué: {e}')

            # 2b. Groq fallback
            if config['secrets'].get('GROQ_API_KEY', '').strip():
                try:
                    synthesis = query_groq(_SYSTEM_PROMPT_FR, user_content, config, opts)
                    return synthesis, 'tavily+groq'
                except Exception as e:
                    print(f'  Groq échoué: {e}')

            # 2c. Tavily answer seul (sans LLM)
            return tavily_context, 'tavily'

        except Exception as e:
            print(f'  Tavily échoué: {e}')
    else:
        print('  TAVILY_API_KEY non configurée, tentative Gemini direct...')

    # 3. Gemini direct (sans Tavily)
    if config['secrets'].get('GEMINI_API_KEY', '').strip():
        try:
            synthesis = query_gemini(_SYSTEM_PROMPT_FR, prompt, config, opts)
            return synthesis, 'gemini'
        except Exception as e:
            print(f'  Gemini direct échoué: {e}')

    # 4. Groq direct
    if config['secrets'].get('GROQ_API_KEY', '').strip():
        try:
            synthesis = query_groq(_SYSTEM_PROMPT_FR, prompt, config, opts)
            return synthesis, 'groq'
        except Exception as e:
            print(f'  Groq direct échoué: {e}')

    fallback_text = (
        "## Rapport indisponible\n\n"
        "Aucune source de données n'est disponible.\n\n"
        f"Prompt concerné :\n\n```\n{prompt[:500]}{'...' if len(prompt) > 500 else ''}\n```"
    )
    return fallback_text, 'unavailable'


# ==================== DELTA / NOUVEAUTÉS ====================

def extract_novelties(previous_snippet: str, new_content: str, config: Dict) -> Optional[str]:
    """Demande à Gemini d'extraire uniquement les éléments nouveaux par rapport au rapport précédent.
    Retourne None si aucune nouveauté significative détectée."""
    gemini_key = config['secrets'].get('GEMINI_API_KEY', '').strip()
    if not gemini_key:
        # Pas de Gemini : on renvoie le contenu complet
        return new_content

    prompt = f"""Tu es un assistant qui compare deux rapports de veille sanitaire.

RAPPORT PRÉCÉDENT (extrait):
{previous_snippet}

NOUVEAU RAPPORT:
{new_content}

Ta tâche :
1. Identifie UNIQUEMENT les éléments réellement nouveaux dans le nouveau rapport (nouvelles alertes, nouveaux incidents, nouvelles réglementations, nouveaux chiffres).
2. Ignore tout ce qui était déjà présent dans le rapport précédent.
3. Si aucune nouveauté significative n'est détectée, réponds EXACTEMENT : "AUCUNE_NOUVEAUTÉ"
4. Sinon, liste les nouveautés de façon concise en bullet points, sans répéter l'ancien contenu.

Réponse (nouveautés uniquement ou AUCUNE_NOUVEAUTÉ) :"""

    try:
        result = query_gemini('Tu es un assistant de comparaison de rapports.', prompt, config, {'max_tokens': 2000, 'temperature': 0.1})
        result = result.strip()
        if result == 'AUCUNE_NOUVEAUTÉ' or 'aucune nouveauté' in result.lower():
            return None
        return result
    except Exception as e:
        print(f'  Extraction nouveautés échouée ({e}), envoi du contenu complet')
        return new_content


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


# ==================== NOTION API ====================

def parse_inline_markdown(text: str) -> list:
    """Parse le texte inline pour extraire les liens Markdown [texte](url) en rich_text Notion."""
    rich_text = []
    pattern = re.compile(r'\[([^\]]+)\]\((https?://[^\)]+)\)')
    last_end = 0
    for match in pattern.finditer(text):
        # Texte avant le lien
        before = text[last_end:match.start()]
        if before:
            for chunk in [before[i:i+2000] for i in range(0, len(before), 2000)]:
                rich_text.append({'type': 'text', 'text': {'content': chunk}})
        # Le lien lui-même
        link_text = match.group(1)[:2000]
        link_url = match.group(2)[:2000]
        rich_text.append({
            'type': 'text',
            'text': {'content': link_text, 'link': {'url': link_url}},
            'annotations': {'underline': True, 'color': 'blue'}
        })
        last_end = match.end()
    # Texte restant
    remaining = text[last_end:]
    if remaining:
        for chunk in [remaining[i:i+2000] for i in range(0, len(remaining), 2000)]:
            rich_text.append({'type': 'text', 'text': {'content': chunk}})
    if not rich_text:
        rich_text.append({'type': 'text', 'text': {'content': ''}})
    return rich_text


def markdown_to_notion_blocks(content: str, timestamp: str) -> list:
    """Convertit du contenu markdown en blocs Notion"""
    blocks = []

    # Bloc date/heure en italique gris
    blocks.append({
        'object': 'block',
        'type': 'paragraph',
        'paragraph': {
            'rich_text': [{
                'type': 'text',
                'text': {'content': f'Généré le {timestamp}'},
                'annotations': {'italic': True, 'color': 'gray'}
            }]
        }
    })

    # Divider
    blocks.append({
        'object': 'block',
        'type': 'divider',
        'divider': {}
    })

    lines = content.split('\n')
    current_paragraph = []

    def flush_paragraph():
        if current_paragraph:
            text = '\n'.join(current_paragraph).strip()
            if text:
                blocks.append({
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {'rich_text': parse_inline_markdown(text[:2000])}
                })
            current_paragraph.clear()

    for line in lines:
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            continue

        # Heading 1
        if stripped.startswith('# ') and not stripped.startswith('##'):
            flush_paragraph()
            blocks.append({
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {'rich_text': parse_inline_markdown(stripped[2:].strip()[:2000])}
            })
        # Heading 2
        elif stripped.startswith('## ') and not stripped.startswith('###'):
            flush_paragraph()
            blocks.append({
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {'rich_text': parse_inline_markdown(stripped[3:].strip()[:2000])}
            })
        # Heading 3
        elif stripped.startswith('### '):
            flush_paragraph()
            blocks.append({
                'object': 'block',
                'type': 'heading_3',
                'heading_3': {'rich_text': parse_inline_markdown(stripped[4:].strip()[:2000])}
            })
        # Bulleted list item
        elif stripped.startswith('- ') or stripped.startswith('* '):
            flush_paragraph()
            blocks.append({
                'object': 'block',
                'type': 'bulleted_list_item',
                'bulleted_list_item': {'rich_text': parse_inline_markdown(stripped[2:].strip()[:2000])}
            })
        # Numbered list item (ex: "1. texte")
        elif len(stripped) > 2 and stripped[0].isdigit() and '. ' in stripped[:5]:
            flush_paragraph()
            text_content = stripped.split('. ', 1)[1] if '. ' in stripped else stripped
            blocks.append({
                'object': 'block',
                'type': 'numbered_list_item',
                'numbered_list_item': {'rich_text': parse_inline_markdown(text_content.strip()[:2000])}
            })
        # Ligne horizontale
        elif stripped in ('---', '***', '___'):
            flush_paragraph()
            blocks.append({
                'object': 'block',
                'type': 'divider',
                'divider': {}
            })
        else:
            current_paragraph.append(stripped)

    flush_paragraph()
    return blocks


def create_notion_page(title: str, content: str, parent_page_id: str,
                       config: Dict) -> Optional[str]:
    """Crée une page Notion avec le titre et le contenu"""
    print(f'  Création page Notion: {title}')

    notion = Client(auth=config['secrets']['NOTION_TOKEN'])

    # Formater la date/heure avec timezone (format français: jj/mm/aaaa - HH:MM)
    tz = pytz.timezone(config.get('general', {}).get('timezone', 'Europe/Paris'))
    now_tz = datetime.now(tz)
    timestamp = now_tz.strftime('%d/%m/%Y - %H:%M')

    full_title = f"{title} ({timestamp})"

    blocks = markdown_to_notion_blocks(content, timestamp)

    try:
        response = notion.pages.create(
            parent={'page_id': parent_page_id},
            properties={
                'title': {
                    'title': [{
                        'type': 'text',
                        'text': {'content': full_title}
                    }]
                }
            },
            children=blocks[:100]
        )

        page_id = response['id']

        # Insérer les blocs restants par batch de 100
        for i in range(100, len(blocks), 100):
            notion.blocks.children.append(block_id=page_id, children=blocks[i:i + 100])

        print(f'  Page créée: {page_id} ({len(blocks)} blocs)')
        return page_id

    except Exception as e:
        print(f'  ERREUR création Notion: {e}')
        return None


# ==================== GMAIL API ====================

def get_gmail_service(config: Dict):
    """Initialise le service Gmail via GOOGLE_OAUTH_TOKEN_JSON.
    Utilise le même token OAuth2 que newsletter_automation.py (scope gmail.modify).
    """
    token_json = config['secrets']['GOOGLE_OAUTH_TOKEN_JSON']

    if not token_json:
        raise ValueError(
            'GOOGLE_OAUTH_TOKEN_JSON manquant. '
            'Ce secret est requis pour les notifications email.'
        )

    token_data = json.loads(token_json)
    creds = Credentials.from_authorized_user_info(token_data, GMAIL_SCOPES)

    # Rafraîchir le token si expiré
    if creds and creds.expired and creds.refresh_token:
        print('  Rafraîchissement du token Gmail...')
        creds.refresh(Request())
    elif not creds or not creds.valid:
        raise ValueError(
            'Token Gmail invalide ou expiré sans refresh_token. '
            "Regénérez GOOGLE_OAUTH_TOKEN_JSON en relançant l'authentification OAuth2."
        )

    # cache_discovery=False évite l'écriture d'un fichier cache en CI
    return build('gmail', 'v1', credentials=creds, cache_discovery=False)


def send_gmail(service, to_email: str, subject: str, text_body: str, html_body: str) -> bool:
    """Envoie un email via l'API Gmail"""
    msg = MIMEMultipart('alternative')
    msg['From'] = 'me'
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(text_body, 'plain', 'utf-8'))
    msg.attach(MIMEText(html_body, 'html', 'utf-8'))

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
    service.users().messages().send(
        userId='me',
        body={'raw': raw}
    ).execute()

    return True


# ==================== EMAIL NOTIFICATIONS ====================

def send_notification_email(prompt_key: str, synthesis: str, page_title: str,
                             config: Dict, novelties: Optional[str] = None,
                             notion_page_id: Optional[str] = None,
                             synthesis_source: str = 'tavily+gemini') -> bool:
    """Envoie un email de notification via Gmail API.
    Si novelties est fourni, n'envoie que les nouveautés. Si None, aucune nouveauté → skip.
    Si novelties vaut synthesis (premier run ou Gemini absent), envoie le contenu complet.
    """
    if not config.get('general', {}).get('notifications', {}).get('enabled', False):
        print('  Notifications email désactivées')
        return True

    to_email = config['secrets']['NOTIFICATION_EMAIL']
    if not to_email:
        print('  NOTIFICATION_EMAIL non configuré, notification ignorée')
        return False

    # novelties=None signifie "aucune nouveauté" → pas d'email
    if novelties is None:
        print('  Aucune nouveauté détectée, email ignoré')
        return True

    print("  Envoi de l'email de notification (Gmail API)...")

    is_full = (novelties == synthesis)
    section_label = 'Synthèse complète' if is_full else 'Nouveautés détectées'
    subject = f'Healthcare Watch - {page_title}' if is_full else f'[Nouveautés] Healthcare Watch - {page_title}'

    # Lien vers la page Notion
    notion_url = None
    if notion_page_id:
        notion_url = f"https://notion.so/{notion_page_id}"

    # Bandeau source
    if synthesis_source == 'tavily+gemini':
        source_banner = '<p style="background:#eafaf1;border-left:4px solid #2ecc71;padding:10px;margin:15px 0;">🤖 <strong>Rapport généré par Tavily + Gemini</strong></p>'
    elif synthesis_source == 'tavily+groq':
        source_banner = '<p style="background:#eafaf1;border-left:4px solid #27ae60;padding:10px;margin:15px 0;">🤖 <strong>Rapport généré par Tavily + Groq</strong> (fallback)</p>'
    elif synthesis_source == 'tavily':
        source_banner = '<p style="background:#ebf5fb;border-left:4px solid #3498db;padding:10px;margin:15px 0;">🔍 <strong>Rapport basé sur Tavily</strong> (synthèse LLM indisponible)</p>'
    elif synthesis_source == 'gemini':
        source_banner = '<p style="background:#e8f4fd;border-left:4px solid #3498db;padding:10px;margin:15px 0;">🤖 <strong>Rapport généré par Gemini</strong> (sans recherche web)</p>'
    elif synthesis_source == 'groq':
        source_banner = '<p style="background:#f0ebff;border-left:4px solid #8e44ad;padding:10px;margin:15px 0;">🤖 <strong>Rapport généré par Groq</strong> (fallback)</p>'
    else:
        source_banner = '<p style="background:#fef9e7;border-left:4px solid #f39c12;padding:10px;margin:15px 0;">⚠️ <strong>Sources indisponibles</strong> — Vérifiez la configuration.</p>'

    try:
        service = get_gmail_service(config)

        notion_link_text = f"\n\nVoir le rapport complet sur Notion : {notion_url}" if notion_url else ""
        text = f"""Bonjour,

Le rapport "{page_title}" a été généré et ajouté à Notion.{notion_link_text}

{section_label}:
{novelties}

---
Healthcare Watch - Newsletter automatisée
"""

        header_color = '#2c3e50' if is_full else '#e67e22'
        notion_button = f'<p><a href="{notion_url}" style="display:inline-block; background-color:#2c3e50; color:#fff; padding:10px 20px; border-radius:5px; text-decoration:none; font-weight:bold;">&#128196; Voir le rapport complet sur Notion</a></p>' if notion_url else ''
        html_body = ''
        for line in novelties.splitlines():
            line_esc = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if line_esc.startswith('## '):
                html_body += f'<h3 style="color:{header_color};">{line_esc[3:]}</h3>\n'
            elif line_esc.startswith('# '):
                html_body += f'<h2 style="color:{header_color};">{line_esc[2:]}</h2>\n'
            elif line_esc.startswith('* ') or line_esc.startswith('- '):
                html_body += f'<li style="margin-bottom:6px;">{line_esc[2:]}</li>\n'
            elif line_esc.strip() == '':
                html_body += '<br>\n'
            else:
                html_body += f'<p style="margin:4px 0;">{line_esc}</p>\n'
        html = f"""<html><body style="font-family:Arial,sans-serif; max-width:700px; margin:0 auto; padding:20px;">
<h2 style="color: {header_color};">{section_label}</h2>
{source_banner}
<p>Le rapport <strong>{page_title}</strong> a été généré et ajouté à Notion.</p>
{notion_button}
<h3 style="border-bottom:2px solid {header_color}; padding-bottom:6px;">{section_label} :</h3>
<div style="background-color:#f9f9f9; padding:15px; border-radius:5px; border-left:4px solid {header_color};">
{html_body}
</div>
<hr style="margin-top:30px;">
<p style="color: #888; font-size: 0.9em;"><em>Healthcare Watch - Newsletter automatisée</em></p>
</body></html>"""

        send_gmail(service, to_email, subject, text, html)
        print('  Email envoyé via Gmail API')
        return True

    except Exception as e:
        print(f'  ERREUR envoi email: {e}')
        return False


def send_error_email(prompt_key: str, error_msg: str, config: Dict) -> bool:
    """Envoie un email de notification en cas d'erreur via Gmail API"""
    if not config.get('general', {}).get('notifications', {}).get('email_on_error', False):
        return True

    to_email = config['secrets'].get('NOTIFICATION_EMAIL', '')
    if not to_email:
        return False

    try:
        service = get_gmail_service(config)

        subject = f'[ERREUR] Healthcare Watch - {prompt_key}'

        text = f"""Bonjour,

Une erreur s'est produite lors de la génération du rapport "{prompt_key}".

Erreur: {error_msg}

---
Healthcare Watch - Newsletter automatisée
"""

        html = f"""<html><body>
<h2 style="color: #c0392b;">Erreur Healthcare Watch</h2>
<p>Une erreur s'est produite lors de la génération de <strong>{prompt_key}</strong>.</p>
<pre style="background-color: #fdf2f2; padding: 15px; border-radius: 5px;">{error_msg}</pre>
<hr>
<p style="color: #888; font-size: 0.9em;"><em>Healthcare Watch - Newsletter automatisée</em></p>
</body></html>"""

        send_gmail(service, to_email, subject, text, html)
        print(f"  Email d'erreur envoyé pour {prompt_key}")
        return True
    except Exception as e:
        print(f"  ERREUR envoi email d'erreur pour {prompt_key}: {e}")
        return False


# ==================== MAIN ====================

def main():
    """Fonction principale"""
    print('\n' + '=' * 60)
    print('HEALTHCARE WATCH RUNNER - Newsletter Sanitaire')
    print('=' * 60)
    print(f'Démarrage: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n')

    # Créer les répertoires de sortie si nécessaire
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        config = load_config()

        last_run_file = OUTPUT_DIR / '.last_run.json'

        executed_prompts = []
        errors = []

        prompts_config = config.get('prompts', {})
        print(f'{len(prompts_config)} prompt(s) configuré(s)\n')

        for prompt_key, prompt_config in prompts_config.items():
            print(f'\n--- Prompt: {prompt_key} ---')

            try:
                if not should_run_prompt(prompt_key, prompt_config, last_run_file):
                    freq = prompt_config.get('frequency', 'daily')
                    print(f'  Fréquence {freq} non atteinte, skip')
                    continue

                # 1. Recherche Tavily + synthèse LLM
                prompt_text = prompt_config.get('prompt', '')
                options = {
                    **prompt_config.get('options', {}),
                    '_prompt_key': prompt_key,
                    '_prompt_config': prompt_config,
                }
                synthesis, synthesis_source = query_with_fallback(prompt_text, config, options)

                # 2. Détecter les nouveautés vs rapport précédent
                prev_hash, prev_snippet = get_previous_content(prompt_key, last_run_file)
                new_hash = content_hash(synthesis)

                if prev_hash is None:
                    # Premier run : envoyer le contenu complet
                    print('  Premier run, envoi du contenu complet')
                    novelties = synthesis
                elif prev_hash == new_hash:
                    # Contenu identique : créer quand même la page Notion, mais pas d'email
                    print('  Contenu identique au rapport précédent, pas de notification')
                    novelties = None
                else:
                    # Nouveau contenu : extraire le delta via Gemini
                    print('  Nouveau contenu détecté, extraction des nouveautés...')
                    novelties = extract_novelties(prev_snippet or '', synthesis, config)

                # 3. Créer la page Notion (toujours, même si pas de nouveautés)
                page_title = prompt_config.get('page_title', f'Rapport {prompt_key}')
                parent_id = prompt_config.get('parent_page_id') or config['secrets'].get('NOTION_PARENT_PAGE_ID')

                if not parent_id:
                    raise ValueError(f'parent_page_id non défini pour {prompt_key}')

                page_id = create_notion_page(page_title, synthesis, parent_id, config)

                if not page_id:
                    raise Exception('Échec de la création de la page Notion')

                # 4. Envoyer email uniquement si des nouveautés ont été détectées
                send_notification_email(prompt_key, synthesis, page_title, config, novelties, page_id, synthesis_source)

                # 5. Mettre à jour la date d'exécution + hash du contenu
                update_last_run(prompt_key, last_run_file, synthesis)

                executed_prompts.append({
                    'key': prompt_key,
                    'title': page_title,
                    'page_id': page_id,
                    'success': True
                })

                print(f'  {prompt_key} exécuté avec succès')

            except Exception as e:
                error_msg = f'{prompt_key}: {str(e)}'
                print(f'  ERREUR: {error_msg}')
                errors.append(error_msg)
                executed_prompts.append({
                    'key': prompt_key,
                    'success': False,
                    'error': str(e)
                })
                send_error_email(prompt_key, str(e), config)

        # Résumé final
        print('\n' + '=' * 60)
        print('RÉSUMÉ')
        print('=' * 60)
        successes = len([p for p in executed_prompts if p['success']])
        print(f'Exécutions réussies: {successes}')
        print(f'Erreurs: {len(errors)}')

        if errors:
            print('\nErreurs détectées:')
            for error in errors:
                print(f'  - {error}')

        print(f'\nTerminé: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        print('=' * 60 + '\n')

        return 0 if not errors else 1

    except Exception as e:
        print(f'\nERREUR FATALE: {e}')
        import traceback
        traceback.print_exc()
        print('=' * 60 + '\n')
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
