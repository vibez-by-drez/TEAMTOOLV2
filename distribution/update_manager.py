# -*- coding: utf-8 -*-
"""
Update Manager für das Coworking Tool.
Verwaltet automatische Updates über Git und Cloud-Synchronisation.
"""

import os
import subprocess
import json
import requests
from datetime import datetime
from tkinter import messagebox
import threading

class UpdateManager:
    def __init__(self, config_data):
        self.config_data = config_data
        self.current_version = "6.6dev"
        self.update_check_interval = 300  # 5 Minuten
        self.update_thread = None
        self.running = False
        
    def start_auto_update_check(self):
        """Startet den automatischen Update-Check im Hintergrund."""
        if self.update_thread and self.update_thread.is_alive():
            return
            
        self.running = True
        self.update_thread = threading.Thread(target=self._auto_update_loop, daemon=True)
        self.update_thread.start()
        
    def stop_auto_update_check(self):
        """Stoppt den automatischen Update-Check."""
        self.running = False
        
    def _auto_update_loop(self):
        """Hauptschleife für automatische Updates."""
        while self.running:
            try:
                self.check_for_updates()
            except Exception as e:
                print(f"Update-Check Fehler: {e}")
            
            # Warte bis zum nächsten Check
            import time
            time.sleep(self.update_check_interval)
    
    def check_for_updates(self):
        """Prüft auf verfügbare Updates."""
        try:
            # Git-basierte Update-Prüfung
            if self._is_git_repo():
                return self._check_git_updates()
            
            # Cloud-basierte Update-Prüfung
            return self._check_cloud_updates()
            
        except Exception as e:
            print(f"Update-Prüfung fehlgeschlagen: {e}")
            return False
    
    def _is_git_repo(self):
        """Prüft ob das Verzeichnis ein Git-Repository ist."""
        return os.path.exists('.git')
    
    def _check_git_updates(self):
        """Prüft auf Git-Updates."""
        try:
            # Git fetch um remote changes zu holen
            subprocess.run(['git', 'fetch'], capture_output=True, text=True)
            
            # Prüfe ob es neue Commits gibt
            result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0 and int(result.stdout.strip()) > 0:
                return True
                
        except Exception as e:
            print(f"Git Update-Check fehlgeschlagen: {e}")
            
        return False
    
    def _check_cloud_updates(self):
        """Prüft auf Cloud-Updates über Google Sheets."""
        try:
            # Hier könntest du ein spezielles "Updates" Sheet verwenden
            # Das würde die aktuelle Version und Download-Links enthalten
            return False  # Placeholder für Cloud-Updates
            
        except Exception as e:
            print(f"Cloud Update-Check fehlgeschlagen: {e}")
            return False
    
    def update_application(self):
        """Führt das Update der Anwendung durch."""
        try:
            if self._is_git_repo():
                return self._update_via_git()
            else:
                return self._update_via_cloud()
                
        except Exception as e:
            messagebox.showerror("Update Fehler", f"Update fehlgeschlagen: {e}")
            return False
    
    def _update_via_git(self):
        """Update über Git."""
        try:
            # Git pull um Updates zu holen
            result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                                 capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Update Erfolgreich", 
                                  "Die Anwendung wurde erfolgreich aktualisiert!\n"
                                  "Bitte starten Sie die Anwendung neu.")
                return True
            else:
                messagebox.showerror("Update Fehler", f"Git Update fehlgeschlagen: {result.stderr}")
                return False
                
        except Exception as e:
            messagebox.showerror("Update Fehler", f"Git Update fehlgeschlagen: {e}")
            return False
    
    def _update_via_cloud(self):
        """Update über Cloud-Download."""
        # Placeholder für Cloud-basierte Updates
        messagebox.showinfo("Update", "Cloud-basierte Updates sind noch nicht implementiert.")
        return False
    
    def show_update_dialog(self):
        """Zeigt einen Update-Dialog an."""
        if self.check_for_updates():
            result = messagebox.askyesno("Update Verfügbar", 
                                      "Ein Update ist verfügbar!\n"
                                      "Möchten Sie die Anwendung jetzt aktualisieren?")
            if result:
                return self.update_application()
        else:
            messagebox.showinfo("Kein Update", "Die Anwendung ist bereits auf dem neuesten Stand.")
            return False
    
    def get_version_info(self):
        """Gibt Versionsinformationen zurück."""
        try:
            if self._is_git_repo():
                # Git commit hash als Version
                result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    return f"{self.current_version} ({result.stdout.strip()})"
            
            return self.current_version
            
        except Exception:
            return self.current_version
