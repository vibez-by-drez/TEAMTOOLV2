# 🚀 Coworking Tool - Installation für Nutzer

## 📋 Schnellstart

### **Schritt 1: Repository klonen**
```bash
# Repository klonen
git clone https://github.com/vibez-by-drez/TEAMTOOLV2.git
cd TEAMTOOLV2

# Installation starten
python install_for_users.py
```

### **Schritt 2: Tool starten**
- **Windows**: Doppelklick auf `Start_CoworkingTool.bat`
- **Mac/Linux**: Doppelklick auf `Start_CoworkingTool.sh`

## 🔄 Automatische Updates

Das Tool prüft **automatisch alle 5 Minuten** auf Updates und installiert sie selbständig!

### **Manuelle Update-Prüfung:**
- **F3-Taste** drücken im Tool
- Oder: `python update_script.py` im Terminal

## ⌨️ Tastatur-Shortcuts

| Taste | Funktion |
|-------|----------|
| **F1** | Einstellungen öffnen |
| **F2** | Fokus-Modus umschalten |
| **F3** | Nach Updates suchen |
| **ESC** | Fokus-Modus verlassen |

## 🆕 Neue Features

### **Multi-Assignee System:**
- ✅ Bis zu 4 Personen pro Task
- ✅ Proportional farbige Ringe um Tasks
- ✅ Asteroiden für To-Do-Items
- ✅ Flüssige Animationen

### **Automatische Updates:**
- ✅ Prüft alle 5 Minuten auf Updates
- ✅ Benachrichtigungen bei neuen Versionen
- ✅ Ein-Klick-Installation
- ✅ Automatische Backups

## 🛠️ Systemanforderungen

- **Python 3.7+**
- **Git** (wird automatisch geprüft)
- **Internetverbindung** (für Updates)

## 🚨 Troubleshooting

### **Git nicht installiert:**
- **Windows**: https://git-scm.com/download/win
- **Mac**: `brew install git`
- **Linux**: `sudo apt install git`

### **Update-Probleme:**
```bash
# Manueller Update
cd ~/CoworkingTool
git pull origin main
python main.py
```

### **Tool startet nicht:**
```bash
# Abhängigkeiten installieren
pip install -r requirements.txt
```

## 📞 Support

Bei Problemen:
1. **F3** drücken für Update-Check
2. **F1** drücken für Einstellungen
3. Terminal öffnen und `python update_script.py` ausführen
