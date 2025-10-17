# -*- coding: utf-8 -*-
"""
Hilfsfunktionen und -klassen für das Coworking Tool.
"""

import os
import random
import time
import math
from datetime import datetime, timezone

try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

def now_iso():
    """Gibt die aktuelle Zeit als ISO 8601 String in UTC zurück."""
    return datetime.now(timezone.utc).isoformat()

def ease_in_out_sine(t):
    """Easing-Funktion für sanfte Animationen (0-1 Input, 0-1 Output)."""
    return -(math.cos(math.pi * t) - 1) / 2

def lerp(start, end, t):
    """Lineare Interpolation zwischen Start- und Endwerten."""
    return start + (end - start) * t

def create_assets_folder():
    """Erstellt den 'assets'-Ordner, falls er nicht existiert."""
    if not os.path.exists("assets"):
        os.makedirs("assets")
        print("Created assets folder")

def generate_fallback_assets():
    """Generiert Fallback-PNG-Assets, falls Pillow verfügbar ist."""
    if not PILLOW_AVAILABLE:
        return

    create_assets_folder()

    # Generiert eine Textur für Glas-Panels
    try:
        glass_img = Image.new('RGBA', (200, 100), (255, 255, 255, 50))
        draw = ImageDraw.Draw(glass_img)
        # Fügt ein subtiles Rauschmuster hinzu
        for _ in range(1000):
            x, y = random.randint(0, 199), random.randint(0, 99)
            alpha = random.randint(20, 80)
            draw.point((x, y), (255, 255, 255, alpha))
        glass_img.save("assets/glass_panel.png")
    except Exception:
        pass

    # Generiert eine Nebel-Textur
    try:
        nebula_img = Image.new('RGBA', (400, 300), (0, 0, 0, 0))
        draw = ImageDraw.Draw(nebula_img)
        # Erstellt weiche, kreisförmige Farbverläufe
        for i in range(5):
            x, y = random.randint(50, 350), random.randint(50, 250)
            size = random.randint(80, 150)
            color = (random.randint(50, 150), random.randint(50, 150), random.randint(100, 200), random.randint(30, 80))
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
        nebula_img.save("assets/nebula_soft.png")
    except Exception:
        pass

class AnimationManager:
    """Verwaltet Animationen für UI-Elemente."""
    def __init__(self, master, fps=30):
        self.master = master
        self.fps = fps
        self.interval = int(1000 / fps)
        self.animations = {}  # {id: AnimationData}
        self.running = False
        self.animation_id = None

    def start(self):
        if not self.running:
            self.running = True
            self._tick()

    def stop(self):
        self.running = False
        if self.animation_id:
            self.master.after_cancel(self.animation_id)
            self.animation_id = None

    def _tick(self):
        if not self.running:
            return

        current_time = time.time()

        # Alle Animationen aktualisieren
        to_remove = []
        for anim_id, anim_data in self.animations.items():
            if current_time >= anim_data['end_time']:
                # Animation beendet
                if anim_data['callback']:
                    anim_data['callback'](anim_data['end_value'])
                to_remove.append(anim_id)
            else:
                # Animation aktualisieren
                elapsed = current_time - anim_data['start_time']
                duration = anim_data['end_time'] - anim_data['start_time']
                progress = min(elapsed / duration, 1.0)

                # Easing anwenden
                eased_progress = ease_in_out_sine(progress)

                # Aktuellen Wert berechnen
                current_value = lerp(anim_data['start_value'], anim_data['end_value'], eased_progress)

                # Update-Callback aufrufen
                if anim_data['update_callback']:
                    anim_data['update_callback'](current_value)

        # Beendete Animationen entfernen
        for anim_id in to_remove:
            del self.animations[anim_id]

        # Nächsten Tick planen
        self.animation_id = self.master.after(self.interval, self._tick)

    def animate(self, anim_id, start_value, end_value, duration, update_callback=None, finished_callback=None):
        """Startet eine neue Animation."""
        self.animations[anim_id] = {
            'start_value': start_value,
            'end_value': end_value,
            'start_time': time.time(),
            'end_time': time.time() + duration,
            'update_callback': update_callback,
            'callback': finished_callback
        }

    def stop_animation(self, anim_id):
        """Stoppt eine bestimmte Animation."""
        if anim_id in self.animations:
            del self.animations[anim_id]