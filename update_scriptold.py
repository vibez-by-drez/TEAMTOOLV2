#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Script für das Coworking Tool.
Kann von allen Team-Mitgliedern verwendet werden.
"""

import os
import sys
import subprocess
import shutil
from datetime import datetime

def main():
    print("🚀 Coworking Tool Update Script")
    print("=" * 40)
    
    # Prüfe ob Git verfügbar ist
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git ist verfügbar")
    except:
        print("❌ Git ist nicht installiert. Bitte installieren Sie Git.")
        return False
    
    # Prüfe ob wir in einem Git-Repository sind
    if not os.path.exists('.git'):
        print("❌ Kein Git-Repository gefunden.")
        print("   Bitte klonen Sie das Repository zuerst:")
        print("   git clone <repository-url>")
        return False
    
    print("🔄 Prüfe auf Updates...")
    
    try:
        # Git fetch um remote changes zu holen
        subprocess.run(['git', 'fetch'], check=True)
        
        # Prüfe ob es neue Commits gibt
        result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], 
                              capture_output=True, text=True, check=True)
        
        new_commits = int(result.stdout.strip())
        
        if new_commits == 0:
            print("✅ Die Anwendung ist bereits auf dem neuesten Stand.")
            return True
        
        print(f"📦 {new_commits} neue Updates verfügbar!")
        
        # Zeige die letzten Commits
        print("\n📋 Letzte Änderungen:")
        result = subprocess.run(['git', 'log', '--oneline', '-5', 'origin/main'], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        
        # Frage den Benutzer
        response = input("\n🤔 Möchten Sie das Update jetzt installieren? (j/n): ")
        
        if response.lower() in ['j', 'ja', 'y', 'yes']:
            print("🔄 Installiere Updates...")
            
            # Backup erstellen
            backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            print(f"💾 Erstelle Backup: {backup_dir}")
            shutil.copytree('.', f"../{backup_dir}", ignore=shutil.ignore_patterns('.git', '__pycache__', '*.pyc'))
            
            # Git pull
            subprocess.run(['git', 'pull', 'origin', 'main'], check=True)
            
            print("✅ Update erfolgreich installiert!")
            print("🔄 Starte die Anwendung neu...")
            
            # Starte die Anwendung neu
            subprocess.run([sys.executable, 'main.py'])
            
            return True
        else:
            print("❌ Update abgebrochen.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Git-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
