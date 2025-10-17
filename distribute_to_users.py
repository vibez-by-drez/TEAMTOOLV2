#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Distributions-Script für Entwickler.
Erstellt ein Paket für Nutzer-Installation.
"""

import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

def main():
    print("📦 Coworking Tool - Distribution für Nutzer")
    print("=" * 50)
    
    # Erstelle Distributions-Ordner
    dist_dir = Path("distribution")
    dist_dir.mkdir(exist_ok=True)
    
    # Dateien für Nutzer kopieren
    user_files = [
        "main.py",
        "ui.py", 
        "backend.py",
        "config.py",
        "utils.py",
        "update_manager.py",
        "update_script.py",
        "install_for_users.py",
        "requirements.txt",
        "NUTZER_INSTALLATION.md",
        "cowork_config.json"
    ]
    
    print("📋 Kopiere Dateien für Nutzer...")
    for file in user_files:
        if os.path.exists(file):
            shutil.copy2(file, dist_dir / file)
            print(f"✅ {file}")
        else:
            print(f"⚠️  {file} nicht gefunden")
    
    # Nutzer-README erstellen
    create_user_readme(dist_dir)
    
    # ZIP-Datei erstellen
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"coworking_tool_v6.6dev_{timestamp}.zip"
    
    print(f"\n📦 Erstelle ZIP-Datei: {zip_name}")
    with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in dist_dir.rglob("*"):
            if file_path.is_file():
                arcname = file_path.relative_to(dist_dir)
                zipf.write(file_path, arcname)
    
    print(f"✅ Distribution erstellt: {zip_name}")
    print(f"📁 Größe: {os.path.getsize(zip_name) / 1024:.1f} KB")
    
    # Anweisungen
    print("\n" + "="*50)
    print("📋 Nächste Schritte:")
    print("1. Repository auf GitHub pushen:")
    print("   git add .")
    print("   git commit -m 'Update'")
    print("   git push origin main")
    print("2. Nutzer klonen das Repository:")
    print("   git clone https://github.com/vibez-by-drez/TEAMTOOLV2.git")
    print("3. Nutzer führen aus: python install_for_users.py")
    print("4. Das Tool richtet sich automatisch ein!")
    
    return zip_name

def create_user_readme(dist_dir):
    """Erstellt eine README für Nutzer."""
    readme_content = """# 🚀 Coworking Tool - Installation

## Schnellstart

1. **Installation starten:**
   ```bash
   python install_for_users.py
   ```

2. **Tool starten:**
   - Windows: Doppelklick auf `Start_CoworkingTool.bat`
   - Mac/Linux: Doppelklick auf `Start_CoworkingTool.sh`

## 🔄 Automatische Updates

Das Tool prüft **automatisch alle 5 Minuten** auf Updates!

### Tastatur-Shortcuts:
- **F1**: Einstellungen
- **F2**: Fokus-Modus  
- **F3**: Nach Updates suchen
- **ESC**: Fokus-Modus verlassen

## 🆕 Neue Features

- ✅ Multi-Assignee System (bis zu 4 Personen pro Task)
- ✅ Asteroiden für To-Do-Items
- ✅ Automatische Updates
- ✅ Proportional farbige Ringe

## 🛠️ Systemanforderungen

- Python 3.7+
- Git (wird automatisch geprüft)
- Internetverbindung

Bei Problemen: F3 drücken für Update-Check!
"""
    
    with open(dist_dir / "README.md", 'w', encoding='utf-8') as f:
        f.write(readme_content)

if __name__ == "__main__":
    zip_file = main()
    print(f"\n🎉 Fertig! Sende {zip_file} an deine Nutzer.")
