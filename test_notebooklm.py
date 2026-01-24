#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de test pour NotebookLM
Teste l'intégration avec NotebookLM via Google Drive
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire src au chemin Python
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Charger la configuration
config_dir = Path(__file__).parent / 'config'
config_file = config_dir / 'config.py'

if not config_file.exists():
    print(f'❌ Fichier config.py non trouvé à {config_file}')
    print('   Créez-le à partir de config/config.example.py')
    sys.exit(1)

import importlib.util
spec = importlib.util.spec_from_file_location("config_module", config_file)
config_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(config_module)

CONFIG = config_module.CONFIG


def test_notebooklm_availability():
    """Teste la disponibilité de NotebookLM"""
    print('🔍 Vérification de la disponibilité de NotebookLM...')
    
    try:
        import requests
        response = requests.get('https://notebooklm.google.com', timeout=10)
        
        if response.status_code == 200:
            print('✅ NotebookLM est accessible')
            return True
        else:
            print(f'⚠️  NotebookLM répondant avec le statut: {response.status_code}')
            return False
    
    except Exception as e:
        print(f'❌ Erreur: {e}')
        return False


def test_selenium_availability():
    """Teste si Selenium est installé"""
    print('\n📦 Vérification de Selenium...')
    
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        print('✅ Selenium est installé')
        return True
    except ImportError:
        print('❌ Selenium n\'est pas installé')
        print('   Installez-le avec: pip install selenium')
        return False


def test_manual_workflow():
    """Affiche le workflow manuel recommandé"""
    print('\n' + '=' * 60)
    print('📋 WORKFLOW RECOMMANDÉ POUR NOTEBOOKLM')
    print('=' * 60)
    
    print('\n⚠️  IMPORTANT: NotebookLM n\'a pas d\'API REST publique.')
    print('   Google n\'a pas encore ouvert d\'accès API public à NotebookLM.')
    print('\n✨ SOLUTIONS DISPONIBLES:\n')
    
    print('1️⃣  SOLUTION RECOMMANDÉE: Workflow semi-automatisé')
    print('   ✓ Le script sauvegarde la synthèse dans un fichier')
    print('   ✓ Envoie un email avec le fichier en pièce jointe')
    print('   ✓ Vous uploadez manuellement dans NotebookLM (5 secondes)')
    print('   ✓ NotebookLM génère automatiquement le podcast')
    
    print('\n2️⃣  SOLUTION AVANCÉE: Automatisation web (Selenium)')
    print('   ✓ Nécessite une configuration supplémentaire')
    print('   ✓ Plus fragile car dépend du design de l\'interface web')
    print('   ✓ À installer: pip install selenium')
    
    print('\n3️⃣  SOLUTION ALTERNATIVE: Utiliser une autre plateforme')
    print('   ✓ Podium AI, Descript, ou autre plateforme avec API')
    print('   ✓ Plus stable et maintenable')
    
    print('\n' + '=' * 60)


def show_current_implementation():
    """Affiche l'implémentation actuelle"""
    print('\n' + '=' * 60)
    print('✅ IMPLÉMENTATION ACTUELLE')
    print('=' * 60)
    
    print('''
    La version actuelle du script :
    
    1. 📧 Récupère les newsletters depuis Gmail
    2. 🤖 Synthétise avec Perplexity AI
    3. 📝 Crée une page Notion avec la synthèse
    4. 💾 Sauvegarde la synthèse en fichier texte
    5. 📤 Envoie un email de notification
    
    Le fichier texte peut ensuite être :
    ✨ Upload manuellement dans NotebookLM (< 5 secondes)
    🎙️ Converti en podcast Audio Overview par NotebookLM
    
    ''')


def test_google_drive_integration():
    """Teste l'intégration avec Google Drive"""
    print('\n🔗 Vérification de l\'intégration Google Drive...')
    
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        print('✅ Google Cloud Libraries disponibles')
        print('   Vous pouvez ajouter une intégration Google Drive')
        return True
    except ImportError:
        print('⚠️  google-auth-oauthlib pas disponible')
        return False


def main():
    """Fonction principale du test"""
    print('=' * 60)
    print('🧪 TEST NOTEBOOKLM - État actuel')
    print('=' * 60)
    
    # Test 1: NotebookLM accessible
    notebooklm_ok = test_notebooklm_availability()
    
    # Test 2: Selenium disponible
    selenium_ok = test_selenium_availability()
    
    # Test 3: Google Drive disponible
    gdrive_ok = test_google_drive_integration()
    
    # Afficher le workflow
    test_manual_workflow()
    
    # Afficher l'implémentation
    show_current_implementation()
    
    print('\n' + '=' * 60)
    print('📋 RÉSUMÉ')
    print('=' * 60)
    print(f'✅ NotebookLM accessible: {"OUI" if notebooklm_ok else "NON"}')
    print(f'✅ Selenium disponible: {"OUI" if selenium_ok else "NON"}')
    print(f'✅ Google Drive libs: {"OUI" if gdrive_ok else "NON"}')
    
    print('\n💡 PROCHAINES ÉTAPES:')
    print('   1. Exécutez: python -m newsletter_automation')
    print('   2. Récupérez le fichier synthèse créé')
    print('   3. Uploadez-le dans NotebookLM.google.com')
    print('   4. Générez le podcast (bouton "Audio Overview")')
    
    print('\n' + '=' * 60)


if __name__ == '__main__':
    main()

