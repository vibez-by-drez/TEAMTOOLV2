# 🔧 GitHub Update-System - Vollständige Erklärung

## 📋 Wie funktioniert Ihr GitHub Update-System?

### 🎯 **Repository-Informationen**
- **GitHub Repository**: `https://github.com/vibez-by-drez/TEAMTOOLV2.git`
- **Branch**: `main`
- **Letzter Commit**: `40f153b Update: Verbesserte UI und Update-System - v6.6dev`

## 🔄 **Automatisches Update-System**

### 1. **Update-Prüfung (alle 5 Minuten)**
```python
# In update_manager.py
self.update_check_interval = 300  # 5 Minuten in Sekunden
```

**Was passiert:**
1. **Git Fetch**: `git fetch` - Holt neue Commits vom GitHub
2. **Commit-Vergleich**: `git rev-list HEAD..origin/main --count`
3. **Update-Benachrichtigung**: Wenn neue Commits gefunden werden

### 2. **Update-Installation**
```python
# Git Pull für Updates
subprocess.run(['git', 'pull', 'origin', 'main'])
```

**Sicherheitsfeatures:**
- ✅ **Automatisches Backup** vor jedem Update
- ✅ **Rollback-Möglichkeit** bei Problemen
- ✅ **Neustart** der Anwendung nach Update

## 🚀 **Für Entwickler (Sie)**

### **Updates veröffentlichen:**
```bash
# 1. Änderungen hinzufügen
git add .

# 2. Commit erstellen
git commit -m "Beschreibung der Änderungen"

# 3. Auf GitHub pushen
git push origin main
```

### **Was passiert dann:**
1. **Alle Team-Mitglieder** erhalten automatisch Benachrichtigungen
2. **Update-Check** läuft alle 5 Minuten
3. **Ein-Klick-Installation** über F3-Taste

## 👥 **Für Team-Mitglieder**

### **Automatische Updates:**
- Das Tool prüft **alle 5 Minuten** auf Updates
- **Benachrichtigung** erscheint bei verfügbaren Updates
- **F3-Taste** für sofortige Installation

### **Manuelle Updates:**
```bash
# Option 1: In der Anwendung
# F3-Taste drücken

# Option 2: Terminal
python update_script.py

# Option 3: Git direkt
git pull origin main
```

## 🔧 **Technische Details**

### **Update-Prüfung:**
```python
def _check_git_updates(self):
    # Git fetch um remote changes zu holen
    subprocess.run(['git', 'fetch'], capture_output=True, text=True)
    
    # Prüfe ob es neue Commits gibt
    result = subprocess.run(['git', 'rev-list', 'HEAD..origin/main', '--count'], 
                          capture_output=True, text=True)
    
    if result.returncode == 0 and int(result.stdout.strip()) > 0:
        return True  # Updates verfügbar!
```

### **Update-Installation:**
```python
def _update_via_git(self):
    # Git pull um Updates zu holen
    result = subprocess.run(['git', 'pull', 'origin', 'main'], 
                         capture_output=True, text=True)
    
    if result.returncode == 0:
        # Update erfolgreich!
        return True
```

## 📊 **Update-Status prüfen**

### **Aktueller Status:**
```bash
# Zeige letzte Commits
git log --oneline -5

# Prüfe auf neue Updates
git fetch
git rev-list HEAD..origin/main --count
```

### **Update-Historie:**
```
40f153b Update: Verbesserte UI und Update-System - v6.6dev
0a94e25 Update: Füge :D wieder hinzu - Update-System Test #3
6f9c60c Update: Entferne :D vom Titel - Update-System Test #2
9c4900c Fix: Sofortiger Update-Check beim Start + verbesserte Benachrichtigungen
40c7545 Test Update: Füge :D zum Titel hinzu - Update-System Test
```

## 🛠️ **Konfiguration anpassen**

### **Update-Intervall ändern:**
```python
# In update_manager.py, Zeile 19
self.update_check_interval = 300  # 5 Minuten
# Ändern zu:
self.update_check_interval = 600  # 10 Minuten
```

### **Auto-Update deaktivieren:**
```python
# In main.py, Zeile 73
# Kommentiere aus:
# self.update_manager.start_auto_update_check()
```

## 🚨 **Troubleshooting**

### **Git-Verbindung prüfen:**
```bash
git remote -v
# Sollte zeigen: origin https://github.com/vibez-by-drez/TEAMTOOLV2.git
```

### **Update-Probleme:**
```bash
# Git-Status prüfen
git status

# Manueller Update
git pull origin main

# Bei Konflikten
git stash
git pull origin main
git stash pop
```

### **Backup wiederherstellen:**
```bash
# Backup-Verzeichnisse finden
ls -la ../backup_*

# Backup wiederherstellen
cp -r ../backup_YYYYMMDD_HHMMSS/* .
```

## 🎯 **Zusammenfassung**

### **Ihr Update-System funktioniert so:**

1. **Sie pushen Updates** → `git push origin main`
2. **GitHub speichert** → Repository wird aktualisiert
3. **Team-Mitglieder** → Tool prüft alle 5 Minuten automatisch
4. **Update-Benachrichtigung** → F3 für Installation
5. **Sichere Installation** → Backup + Git Pull + Neustart

### **Vorteile:**
- ✅ **Automatisch** - Keine manuellen Downloads
- ✅ **Sicher** - Backups vor jedem Update
- ✅ **Schnell** - Ein-Klick-Installation
- ✅ **Zuverlässig** - Git-basierte Versionskontrolle

**Ihr System ist perfekt eingerichtet! 🚀**
