# 🚀 Automatisches Update-System

## Übersicht
Das Coworking Tool verfügt über ein integriertes Update-System, das automatische Updates für alle Team-Mitglieder ermöglicht.

## 🔧 Funktionsweise

### 1. **Git-basierte Updates (Empfohlen)**
- Das Tool prüft automatisch auf neue Git-Commits
- Updates werden über `git pull` installiert
- Automatische Backup-Erstellung vor Updates

### 2. **Tastatur-Shortcuts**
- **F1**: Einstellungen öffnen
- **F2**: Fokus-Modus umschalten  
- **F3**: Nach Updates suchen
- **ESC**: Fokus-Modus verlassen

### 3. **Automatische Updates**
- Das Tool prüft alle 5 Minuten auf Updates
- Benachrichtigungen bei verfügbaren Updates
- Ein-Klick-Installation

## 📋 Setup für Team-Mitglieder

### Schritt 1: Repository klonen
```bash
git clone https://github.com/vibez-by-drez/TEAMTOOLV2.git
cd TEAMTOOLV2
```

### Schritt 2: Update-Script ausführbar machen
```bash
chmod +x update_script.py
```

### Schritt 3: Anwendung starten
```bash
python main.py
```

## 🔄 Update-Prozess

### Automatisch (Empfohlen)
1. Das Tool prüft automatisch auf Updates
2. Bei verfügbaren Updates erscheint eine Benachrichtigung
3. Ein-Klick-Installation über F3

### Manuell
```bash
python update_script.py
```

## 🛠️ Für Entwickler

### Updates veröffentlichen
1. Änderungen committen:
   ```bash
   git add .
   git commit -m "Neue Features hinzugefügt"
   ```

2. Auf GitHub pushen:
   ```bash
   git push origin main
   ```

3. Alle Team-Mitglieder erhalten automatisch Benachrichtigungen

### Update-Einstellungen
- **Update-Intervall**: 5 Minuten (konfigurierbar)
- **Auto-Update**: Aktiviert (konfigurierbar)
- **Backup**: Automatisch vor Updates

## 🔧 Konfiguration

### Update-Intervall ändern
In `update_manager.py`:
```python
self.update_check_interval = 300  # 5 Minuten in Sekunden
```

### Auto-Update deaktivieren
In `main.py`:
```python
# Kommentiere diese Zeile aus:
# self.update_manager.start_auto_update_check()
```

## 🚨 Troubleshooting

### Git nicht verfügbar
```bash
# Git installieren (Ubuntu/Debian)
sudo apt install git

# Git installieren (macOS)
brew install git
```

### Update-Fehler
1. Prüfe Git-Verbindung:
   ```bash
   git remote -v
   ```

2. Manueller Update:
   ```bash
   git pull origin main
   ```

### Backup wiederherstellen
```bash
# Backup-Verzeichnis finden
ls -la ../backup_*

# Backup wiederherstellen
cp -r ../backup_YYYYMMDD_HHMMSS/* .
```

## 📊 Vorteile

✅ **Automatische Updates** für alle Team-Mitglieder  
✅ **Sichere Installation** mit automatischen Backups  
✅ **Keine manuellen Downloads** erforderlich  
✅ **Versionskontrolle** über Git  
✅ **Ein-Klick-Updates** über F3-Taste  
✅ **Benachrichtigungen** bei verfügbaren Updates  

## 🔮 Zukünftige Features

- [ ] Cloud-basierte Updates (ohne Git)
- [ ] Rollback-Funktionalität
- [ ] Update-Historie
- [ ] Beta/Stable-Kanäle
- [ ] Automatische Neustarts
