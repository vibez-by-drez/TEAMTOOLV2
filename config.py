# -*- coding: utf-8 -*-
"""
Konfigurations- und Konstanten-Modul für das Coworking Tool.
"""

import json
import os

# --- Optional Visual Enhancement Libraries ---
try:
    import ttkbootstrap as ttk_bs
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False

CONFIG_FILE = "cowork_config.json"
DEFAULT_POLL_SECONDS = 5

USERS = ["Ricky", "Zimba", "Drez", "Moe", "Unzugewiesen"]
ASSIGNEE_COLORS = {
    "Ricky": "#1e90ff",   # blau
    "Zimba": "#ff8c00",   # orange
    "Drez":  "#32cd32",   # grün
    "Moe":   "#ff1493",   # pink
    "Unzugewiesen": "#888888",   # grau (unassigned)
    "":      "#888888",   # grau (unassigned)
    None:    "#888888",
}

def load_config():
    """Lädt die Konfiguration aus der JSON-Datei oder erstellt eine Standardkonfiguration."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            try:
                config = json.load(f)
            except json.JSONDecodeError:
                config = {}
    else:
        config = {}

    # Standardwerte für alle Konfigurationsoptionen
    defaults = {
        "sheet_id": "",
        "service_account_json": "",
        "current_user": "",
        "poll_seconds": DEFAULT_POLL_SECONDS,
        # UI Enhancement Flags
        "ui": {
            "enable_galaxy_bg": False,
            "enable_deadline_halo": True,
            "enable_progress_ring": True,
            "enable_radar": False,
            "enable_focus_mode": False,
            "enable_floating_animation": True,
            "animation_fps": 30,
            "floating_speed": 0.07,
            "neon_intensity": 0.7,
            "blur_level": 0.5,
            "theme": "dark" if TTKBOOTSTRAP_AVAILABLE else "default",
            # Simple theme mode
            "theme_mode": "bright"  # "bright" or "dark"
        }
    }

    # Konfiguration mit Standardwerten zusammenführen
    for key, value in defaults.items():
        if key not in config:
            config[key] = value
        elif key == "ui" and isinstance(value, dict):
            if key not in config or not isinstance(config[key], dict):
                config[key] = {}
            for ui_key, ui_value in value.items():
                if ui_key not in config[key]:
                    config[key][ui_key] = ui_value

    return config

def save_config(cfg):
    """Speichert die Konfiguration in der JSON-Datei."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)

def get_theme_colors(config):
    """Gibt die Farbpalette für das aktuelle Theme zurück."""
    # Derzeit wird immer der "bright" Modus verwendet.
    return {
        'background': '#ffffff',
        'surface': '#f5f5f5',
        'surface_light': '#f0f0f0',
        'text_primary': '#000000',
        'text_secondary': '#333333',
        'text_muted': '#666666',
        'primary': '#007acc',
        'secondary': '#666666',
        'border': '#cccccc',
        'border_light': '#dddddd',
        'hover': '#eeeeee',
        'bubble_bg': '#ffffff',
        'bubble_outline': '#cccccc',
        'success': '#00aa44',
        'warning': '#ff8800',
        'error': '#cc0000'
    }

def get_color(config, color_key, default_color):
    """Holt eine Farbe aus dem Theme mit einem Fallback-Wert."""
    theme_colors = get_theme_colors(config)
    return theme_colors.get(color_key, default_color)