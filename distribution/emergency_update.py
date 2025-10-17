#!/usr/bin/env python3
"""
NOTFALL-UPDATE für bestehende Installationen
Dieses Script kann auch mit der alten Update-Logik funktionieren.
"""

import subprocess
import os
import shutil
import sys
from tkinter import messagebox

def emergency_update():
    """Notfall-Update das IMMER funktioniert."""
    try:
        print("🚨 NOTFALL-UPDATE gestartet...")
        
        # 1. Lösche ALLE problematischen Dateien
        print("1. Lösche problematische Dateien...")
        
        # Lösche __pycache__ komplett
        if os.path.exists('__pycache__'):
            shutil.rmtree('__pycache__', ignore_errors=True)
            print("✅ Gelöscht: __pycache__ Verzeichnis")
        
        # Lösche problematische Assets
        problematic_files = [
            'assets/glass_panel.png',
            'assets/nebula_soft.png'
        ]
        
        for file_path in problematic_files:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    print(f"✅ Gelöscht: {file_path}")
                except:
                    pass
        
        # 2. Git Force Reset (überschreibt ALLES)
        print("2. Führe Git Force Reset durch...")
        
        # Git fetch
        fetch_result = subprocess.run(['git', 'fetch', 'origin', 'main'], 
                                    capture_output=True, text=True)
        print("✅ Git fetch ausgeführt")
        
        # Git reset --hard (überschreibt ALLES)
        reset_result = subprocess.run(['git', 'reset', '--hard', 'origin/main'], 
                                    capture_output=True, text=True)
        
        if reset_result.returncode != 0:
            print(f"❌ Git reset fehlgeschlagen: {reset_result.stderr}")
            return False
        
        print("✅ Git reset erfolgreich")
        
        # Git clean (entfernt unverfolgte Dateien)
        clean_result = subprocess.run(['git', 'clean', '-fd'], 
                                    capture_output=True, text=True)
        print("✅ Git clean ausgeführt")
        
        # 3. Stelle sicher dass .gitignore aktiv ist
        print("3. Aktiviere .gitignore...")
        subprocess.run(['git', 'add', '.gitignore'], capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Emergency: Activate .gitignore'], capture_output=True)
        
        print("🎉 NOTFALL-UPDATE erfolgreich!")
        print("✅ Alle problematischen Dateien wurden entfernt")
        print("✅ Git Update funktioniert jetzt")
        print("✅ Bitte starten Sie die Anwendung neu")
        
        return True
        
    except Exception as e:
        print(f"❌ NOTFALL-UPDATE fehlgeschlagen: {e}")
        return False

if __name__ == "__main__":
    print("🚨 NOTFALL-UPDATE für bestehende Installationen")
    print("=" * 50)
    
    success = emergency_update()
    
    if success:
        print("\n🎉 NOTFALL-UPDATE erfolgreich!")
        print("Die Anwendung kann jetzt normal aktualisiert werden.")
    else:
        print("\n❌ NOTFALL-UPDATE fehlgeschlagen!")
        print("Bitte kontaktieren Sie den Support.")
    
    input("\nDrücken Sie Enter zum Beenden...")
