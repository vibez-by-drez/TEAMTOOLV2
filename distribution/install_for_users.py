#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Installations-Script für Coworking Tool Nutzer.
Lädt die neueste Version herunter und richtet Auto-Updates ein.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    print("🚀 Coworking Tool - Installation für Nutzer")
    print("=" * 50)
    
    # Repository-URL (HIER DEINE GITHUB-URL EINTRAGEN!)
    REPO_URL = "https://github.com/DEIN-USERNAME/coworking-tool.git"  # ← ÄNDERE DIESE URL!
    
    print("📋 Installation startet...")
    print(f"🔗 Repository: {REPO_URL}")
    
    # Prüfe ob Git verfügbar ist
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        print("✅ Git ist verfügbar")
    except:
        print("❌ Git ist nicht installiert!")
        print("   Bitte installieren Sie Git zuerst:")
        print("   - Windows: https://git-scm.com/download/win")
        print("   - macOS: brew install git")
        print("   - Linux: sudo apt install git")
        return False
    
    # Installationsverzeichnis
    install_dir = Path.home() / "CoworkingTool"
    
    print(f"📁 Installationsverzeichnis: {install_dir}")
    
    # Prüfe ob bereits installiert
    if install_dir.exists():
        print("⚠️  Coworking Tool ist bereits installiert.")
        response = input("Möchten Sie es aktualisieren? (j/n): ")
        if response.lower() not in ['j', 'ja', 'y', 'yes']:
            print("❌ Installation abgebrochen.")
            return False
    
    try:
        # Repository klonen/aktualisieren
        if install_dir.exists():
            print("🔄 Aktualisiere bestehende Installation...")
            os.chdir(install_dir)
            subprocess.run(['git', 'pull'], check=True)
        else:
            print("📥 Lade Coworking Tool herunter...")
            subprocess.run(['git', 'clone', REPO_URL, str(install_dir)], check=True)
            os.chdir(install_dir)
        
        print("✅ Download erfolgreich!")
        
        # Update-Script ausführbar machen
        update_script = install_dir / "update_script.py"
        if update_script.exists():
            os.chmod(update_script, 0o755)
            print("✅ Update-Script konfiguriert")
        
        # Start-Script erstellen
        create_start_script(install_dir)
        
        print("\n🎉 Installation erfolgreich!")
        print("=" * 50)
        print("📋 Nächste Schritte:")
        print(f"1. Öffnen Sie: {install_dir}")
        print("2. Doppelklick auf 'Start_CoworkingTool.bat' (Windows)")
        print("   oder 'Start_CoworkingTool.sh' (Mac/Linux)")
        print("3. Das Tool startet automatisch und prüft auf Updates!")
        print("\n🔧 Tastatur-Shortcuts:")
        print("   F1: Einstellungen")
        print("   F2: Fokus-Modus")
        print("   F3: Nach Updates suchen")
        print("   ESC: Fokus-Modus verlassen")
        
        # Frage ob sofort starten
        response = input("\n🤔 Möchten Sie das Tool jetzt starten? (j/n): ")
        if response.lower() in ['j', 'ja', 'y', 'yes']:
            print("🚀 Starte Coworking Tool...")
            subprocess.run([sys.executable, 'main.py'])
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Installation fehlgeschlagen: {e}")
        return False

def create_start_script(install_dir):
    """Erstellt Start-Scripts für verschiedene Betriebssysteme."""
    
    # Windows Batch-Script
    bat_content = f"""@echo off
cd /d "{install_dir}"
echo 🚀 Starte Coworking Tool...
python main.py
pause
"""
    
    bat_file = install_dir / "Start_CoworkingTool.bat"
    with open(bat_file, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    # Unix Shell-Script
    sh_content = f"""#!/bin/bash
cd "{install_dir}"
echo "🚀 Starte Coworking Tool..."
python3 main.py
"""
    
    sh_file = install_dir / "Start_CoworkingTool.sh"
    with open(sh_file, 'w', encoding='utf-8') as f:
        f.write(sh_content)
    os.chmod(sh_file, 0o755)
    
    print("✅ Start-Scripts erstellt")

if __name__ == "__main__":
    success = main()
    if not success:
        input("Drücken Sie Enter zum Beenden...")
        sys.exit(1)
