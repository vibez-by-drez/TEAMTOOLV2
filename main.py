# -*- coding: utf-8 -*-
"""
Haupt-Einstiegspunkt für das Coworking Projekte Tool.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

# Optionale UI-Bibliotheken
try:
    import ttkbootstrap as ttk_bs
    TTKBOOTSTRAP_AVAILABLE = True
except ImportError:
    TTKBOOTSTRAP_AVAILABLE = False

# Lokale Modul-Importe
import config
from utils import AnimationManager, generate_fallback_assets
from backend import SheetsBackend, Model
from ui import BubbleCanvas, LegendWidget, MiniRadar, NewProjectDialog, TaskEditor, SettingsDialog
from update_manager import UpdateManager

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Co-Worker V3")
        self.geometry("1296x900")

        # Konfiguration laden
        self.config_data = config.load_config()

        # Backend und Datenmodell initialisieren
        self.backend = SheetsBackend(self.config_data)
        self.model = Model(self.backend)

        # UI-Theme und -Stil anwenden
        self.configure(bg=config.get_color(self.config_data, "background", "#0f0f0f"))
        self._apply_theme()

        # Fallback-Assets generieren
        generate_fallback_assets()

        # UI-Elemente erstellen
        self._create_widgets()

        # Zustand der Anwendung
        self.mode = "projects"  # oder "tasks"
        self.current_project_id = None

        # Synchronisations-Thread
        self.sync_thread = None
        self.stop_sync = threading.Event()

        # Animations-Manager
        self.anim_manager = AnimationManager(self, self.config_data.get('ui', {}).get('animation_fps', 30))
        
        # Update-Manager
        self.update_manager = UpdateManager(self.config_data)

        # Tastatur-Shortcuts binden
        self.bind("<Escape>", self._toggle_focus_mode)
        self.bind("<KeyPress>", self._on_key_press)
        self.bind("<KeyRelease>", self._on_key_release)
        
        # Pan-Modus für Canvas
        self.pan_mode = False

        # Verbindung herstellen und Daten laden
        self._connect_and_load()

        # Animationen starten
        self.anim_manager.start()
        
        # Automatischen Update-Check starten
        self.update_manager.start_auto_update_check()
        
        # Sofortigen Update-Check beim Start
        self.after(2000, self._check_updates_on_start)  # 2 Sekunden nach Start

        # Schließen-Handler
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _apply_theme(self):
        """Wendet das UI-Theme an."""
        if TTKBOOTSTRAP_AVAILABLE and self.config_data.get('ui', {}).get('theme') != 'default':
            try:
                theme = self.config_data['ui']['theme']
                self.style = ttk_bs.Style(theme=theme)
            except Exception:
                self.style = ttk.Style(self)
        else:
            self.style = ttk.Style(self)

        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass # Fallback, wenn "clam" nicht verfügbar ist

    def _create_widgets(self):
        """Erstellt alle UI-Widgets der Hauptanwendung."""
        # Top-Bar
        top = tk.Frame(self, bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"), height=60)
        top.pack(side="top", fill="x")
        top.pack_propagate(False)

        title_frame = tk.Frame(top, bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"))
        title_frame.pack(side="left", padx=20, pady=15)
        self.title_label = tk.Label(title_frame, text="Co-Worker V3", font=("Helvetica", 16, "bold"), bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"), fg="#000000")
        self.title_label.pack(side="left")
        self.status_label = tk.Label(title_frame, text="● Offline", font=("Helvetica", 10), bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"), fg="#000000")
        self.status_label.pack(side="left", padx=(15, 0))

        # Zoom-Slider
        zoom_frame = tk.Frame(top, bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"))
        zoom_frame.pack(side="right", padx=10, pady=15)
        
        tk.Label(zoom_frame, text="🔍", font=("Helvetica", 12), bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"), fg="#000000").pack(side="left")
        
        self.zoom_var = tk.DoubleVar(value=1.0)
        self.zoom_scale = tk.Scale(zoom_frame, from_=0.3, to=3.0, resolution=0.1, orient="horizontal", 
                                 variable=self.zoom_var, command=self._on_zoom_change,
                                 bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"), 
                                 fg="#000000", highlightthickness=0, length=100)
        self.zoom_scale.pack(side="left", padx=(5, 0))
        
        
        btn_frame = tk.Frame(top, bg=config.get_color(self.config_data, "surface_light", "#2a2a2a"))
        btn_frame.pack(side="right", padx=20, pady=15)
        
        # Projekt-Einstellungen Button (wird dynamisch hinzugefügt/entfernt)
        self.project_settings_btn = None
        
        tk.Button(btn_frame, text="⚙️ Einstellungen", command=self.open_settings, bg="#333333", fg="#000000", font=("Helvetica", 10), relief="sunken", bd=2, padx=15, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="right", padx=(5, 0))
        tk.Button(btn_frame, text="← Zurück zu Projekten", command=self.show_projects, bg="#333333", fg="#000000", font=("Helvetica", 10, "bold"), relief="sunken", bd=2, padx=15, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="right")

        # Focus-Modus Banner
        self.focus_banner = tk.Label(self, text="Focus Mode aktiv - ESC zum Verlassen", bg="#ff6600", fg="#000000", font=("Helvetica", 10, "bold"))
        self.focus_banner.pack(side="top", fill="x", pady=(0, 5))
        self.focus_banner.pack_forget()

        # Haupt-Canvas
        self.canvas = BubbleCanvas(self, self.config_data)
        self.canvas.model = self.model  # Model für ToDo-Berechnungen
        self.canvas.pack(fill="both", expand=True)

        # Legende
        self.legend = LegendWidget(self, self.config_data)
        self.legend.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        self.legend.pack_forget()

        # Mini-Radar
        self.radar = MiniRadar(self, self.config_data)
        self.radar.place(relx=0.98, rely=0.02, anchor="ne")
        if not self.config_data.get('ui', {}).get('enable_radar', False):
            self.radar.place_forget()

        # "Hinzufügen"-Button
        self.add_btn = tk.Button(self, text="+", font=("Helvetica", 24, "bold"), bg="#333333", fg="#000000", bd=0, activebackground="#444444", command=self.on_add_clicked, relief="sunken", width=3, height=1, activeforeground="#000000")
        self.add_btn.place(relx=0.95, rely=0.96, anchor="center")  # Bissl runter
        self.add_btn.bind("<Enter>", lambda e: self.add_btn.config(bg="#555555"))
        self.add_btn.bind("<Leave>", lambda e: self.add_btn.config(bg="#333333"))

    def _connect_and_load(self):
        try:
            self.backend.connect()
            self.status_label.config(text="● Online", fg="green")
            self.model.load_all()
        except Exception as e:
            self.status_label.config(text="● Offline", fg="red")
            messagebox.showwarning("Setup benötigt", f"Bitte Einstellungen prüfen.\n\n{e}")
        self.show_projects()
        self._start_sync()

    def _start_sync(self):
        self.stop_sync.clear()
        if not self.sync_thread or not self.sync_thread.is_alive():
            self.sync_thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.sync_thread.start()

    def _sync_loop(self):
        while not self.stop_sync.is_set():
            try:
                self.model.merge_remote()
                self.after(0, self._refresh_view)
            except Exception as e:
                print(f"Sync failed: {e}") # Log error instead of popup
            time.sleep(int(self.config_data.get("poll_seconds", config.DEFAULT_POLL_SECONDS)))

    def _refresh_view(self):
        # Im Landkarten-Modus: Nur Daten aktualisieren, nicht neu zeichnen
        if hasattr(self, 'canvas') and self.canvas.zoom_mode == 'map':
            # Nur Radar aktualisieren, keine Neuzeichnung der Bubbles
            self._update_radar()
        else:
            # Normaler Modus: Vollständige Aktualisierung
            if self.mode == "projects":
                self._draw_projects()
            else:
                self._draw_tasks(self.current_project_id)
            self._update_radar()

    def show_projects(self):
        self.mode = "projects"
        self.current_project_id = None
        self.current_project_name = None
        
        # Titel zurücksetzen auf Standard
        self.title_label.config(text="Co-Worker V3")
        
        # Projekt-Einstellungen Button entfernen
        self._remove_project_settings_button()
        
        self.legend.pack_forget()
        if self.config_data.get('ui', {}).get('enable_radar', False):
            self.radar.place(relx=0.98, rely=0.02, anchor="ne")
        self._draw_projects()

    def _draw_projects(self):
        projects = self.model.get_projects_list()
        
        # Prioritäten berechnen
        projects_with_priority = self._calculate_project_priorities(projects)
        
        # Nach Priorität sortieren (höchste zuerst)
        projects_with_priority.sort(key=lambda p: p.get("priority", 0), reverse=True)
        
        self.canvas.draw_bubbles(projects_with_priority, "name", "project", self.on_project_clicked)
        self.add_btn.configure(command=self.on_add_project)

    def on_project_clicked(self, project):
        self.mode = "tasks"
        self.current_project_id = project["project_id"]
        self.current_project_name = project.get("name", "Unbekanntes Projekt")
        
        # Titel aktualisieren um aktuelles Projekt anzuzeigen
        self.title_label.config(text=f"Co-Worker V3 - {self.current_project_name}")
        
        # Projekt-Einstellungen Button hinzufügen
        self._add_project_settings_button()
        
        self.legend.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        if self.config_data.get('ui', {}).get('enable_radar', False):
            self.radar.place(relx=0.98, rely=0.02, anchor="ne")
        self._draw_tasks(self.current_project_id)

    def on_add_project(self):
        def on_dialog_result(result):
            if result:
                name, color, deadline = result
                self.model.new_project(name=name, color=color, deadline=deadline)
                self._draw_projects()
        NewProjectDialog(self, on_result=on_dialog_result).show()

    def _draw_tasks(self, project_id):
        tasks = sorted(self.model.get_tasks_for_project(project_id), key=lambda t: t.get("last_update", ""), reverse=True)
        self.canvas.draw_bubbles(tasks, "name", "task", self.on_task_clicked, assignee_getter=lambda t: t.get("assignee", []))
        self.add_btn.configure(command=self.on_add_task)

    def on_add_clicked(self):
        if self.mode == "projects":
            self.on_add_project()
        else:
            self.on_add_task()

    def on_add_task(self):
        if self.current_project_id:
            task = self.model.new_task(self.current_project_id, name="Neuer Task")
            self._draw_tasks(self.current_project_id)
            self.edit_task(task)

    def on_task_clicked(self, task):
        self.edit_task(task)
    
    def _edit_current_project(self):
        """Bearbeitet das aktuelle Projekt in der Task-Ansicht."""
        if not self.current_project_id:
            return
            
        # Aktuelles Projekt finden
        current_project = None
        for project in self.model.get_projects_list():
            if project.get("project_id") == self.current_project_id:
                current_project = project
                break
                
        if not current_project:
            return
            
        # Projekt-Dialog öffnen
        def on_dialog_result(result):
            if result:
                name, color, deadline = result
                current_project["name"] = name
                current_project["color"] = color
                current_project["deadline"] = deadline
                self.model.save_project(current_project)
                
                # Titel aktualisieren
                self.title_label.config(text=f"Co-Worker V3 - {name}")
                
                # Projekte neu zeichnen (falls wir zurück zu Projekten gehen)
                self._refresh_view()
        
        from ui import NewProjectDialog
        
        # Werte vor dem Dialog speichern
        project_name = current_project.get("name", "")
        project_color = current_project.get("color", "#222222")
        project_deadline = current_project.get("deadline", "")
        
        dialog = NewProjectDialog(self, on_result=on_dialog_result)
        
        # Nach der Initialisierung die Werte setzen
        def set_values():
            try:
                dialog.var_name.set(project_name)
                dialog.var_color.set(project_color)
                dialog.var_deadline.set(project_deadline)
                
                # Farbe im Preview aktualisieren
                if hasattr(dialog, 'color_preview'):
                    dialog.color_preview.create_rectangle(2, 2, 38, 28, fill=project_color, outline="")
            except:
                pass  # Falls noch nicht initialisiert, ignorieren
        
        dialog.show()
        
        # Nach kurzer Verzögerung die Werte setzen
        self.after(100, set_values)
    
    def _calculate_project_priorities(self, projects):
        """Berechnet Prioritäten basierend auf Deadlines (1-5, 5 = höchste)."""
        from datetime import datetime
        
        # Projekte mit Deadlines sammeln
        projects_with_deadlines = []
        for project in projects:
            deadline = project.get("deadline", "")
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                    days_until = (deadline_date - datetime.now()).days
                    projects_with_deadlines.append((project, days_until))
                except:
                    pass
        
        # Nach Tagen bis Deadline sortieren (nächste zuerst)
        projects_with_deadlines.sort(key=lambda x: x[1])
        
        # Prioritäten zuweisen (5 Stufen)
        priority_levels = [5, 4, 3, 2, 1]
        projects_with_priority = []
        
        for i, (project, days_until) in enumerate(projects_with_deadlines):
            # Priorität basierend auf Position in der sortierten Liste
            if i < len(priority_levels):
                priority = priority_levels[i]
            else:
                # Wenn mehr als 5 Projekte, wiederhole die niedrigeren Stufen
                priority = priority_levels[i % len(priority_levels)]
            
            project["priority"] = priority
            project["days_until_deadline"] = days_until
            projects_with_priority.append(project)
        
        # Projekte ohne Deadline bekommen Priorität 1
        for project in projects:
            if not project.get("deadline"):
                project["priority"] = 1
                project["days_until_deadline"] = None
                projects_with_priority.append(project)
        
        return projects_with_priority
    
    def _add_project_settings_button(self):
        """Fügt den Projekt-Einstellungen Button hinzu."""
        if self.project_settings_btn is None:
            # Finde den btn_frame (erste Frame in der oberen Leiste)
            for widget in self.winfo_children():
                if isinstance(widget, tk.Frame):
                    for child in widget.winfo_children():
                        if isinstance(child, tk.Frame) and child.winfo_children():
                            # Das ist der btn_frame
                            self.project_settings_btn = tk.Button(child, text="📝 Projekt-Einstellungen", 
                                                               command=self._edit_current_project,
                                                               bg="#4CAF50", fg="#000000", 
                                                               font=("Helvetica", 9, "bold"), 
                                                               relief="raised", bd=2)
                            self.project_settings_btn.pack(side="left", padx=(0, 10))
                            break
                    break
    
    def _remove_project_settings_button(self):
        """Entfernt den Projekt-Einstellungen Button."""
        if self.project_settings_btn is not None:
            self.project_settings_btn.destroy()
            self.project_settings_btn = None

    def edit_task(self, task):
        def save_cb(updated_task):
            self.model.save_task(updated_task)
            self._draw_tasks(self.current_project_id)
        def delete_cb(task_id):
            self.model.delete_task(task_id)
            self._draw_tasks(self.current_project_id)
        TaskEditor(self, self.model, task, save_cb, delete_cb, self.config_data.get("current_user", "")).show()

    def open_settings(self):
        dialog = SettingsDialog(self, self.config_data, self._on_settings_saved)
        dialog.show()
    
    def show_version_info(self):
        """Zeigt Versionsinformationen an."""
        version = self.update_manager.get_version_info()
        messagebox.showinfo("Versionsinformationen", 
                          f"Aktuelle Version: {version}\n\n"
                          f"F3: Nach Updates suchen\n"
                          f"F2: Fokus-Modus\n"
                          f"F1: Einstellungen")

    def _on_settings_saved(self, new_config):
        self.config_data = new_config
        try:
            # Update zoom mode in canvas
            if hasattr(self, 'canvas'):
                self.canvas.zoom_mode = self.config_data.get('ui', {}).get('zoom_mode', 'dynamic')
                # Reset fixed positions when switching modes
                if hasattr(self.canvas, 'fixed_positions'):
                    self.canvas.fixed_positions.clear()
            
            self.backend = SheetsBackend(self.config_data)
            self.model = Model(self.backend)
            self._connect_and_load()
            self._refresh_all_ui_elements()
        except Exception as e:
            messagebox.showerror("Fehler", f"Konnte nach Einstellungs-Update nicht verbinden:\n{e}")

    def _toggle_focus_mode(self, event=None):
        current = self.config_data.get('ui', {}).get('enable_focus_mode', False)
        self.config_data['ui']['enable_focus_mode'] = not current
        
        # Banner anzeigen/verstecken basierend auf dem neuen Status
        if not current:  # Wenn wir Fokus-Modus aktivieren
            self.focus_banner.pack(side="top", fill="x")
        else:  # Wenn wir Fokus-Modus deaktivieren
            self.focus_banner.pack_forget()
            
        self._refresh_view()

    def _on_key_press(self, event):
        if event.keysym.lower() == "f1": self.open_settings()
        elif event.keysym.lower() == "f2": self._toggle_focus_mode()
        elif event.keysym.lower() == "f3": self._check_for_updates()
        elif event.keysym == "space": self._toggle_pan_mode(True)
    
    def _on_key_release(self, event):
        if event.keysym == "space": self._toggle_pan_mode(False)
    
    def _toggle_pan_mode(self, enabled):
        """Aktiviert/deaktiviert Pan-Modus nur im Landkarten-Modus."""
        # Nur im Landkarten-Modus Pan-Modus aktivieren
        if hasattr(self, 'canvas') and self.canvas.zoom_mode == 'map':
            self.pan_mode = enabled
            self.canvas.set_pan_mode(enabled)
            
            # Visuelles Feedback nur im Landkarten-Modus
            if enabled:
                # Zeige Pan-Hinweis
                if not hasattr(self, 'pan_banner'):
                    self.pan_banner = tk.Label(self, text="🖱️ Pan-Modus aktiv - Leertaste gedrückt halten und ziehen", 
                                             bg="#4CAF50", fg="#000000", font=("Helvetica", 10, "bold"))
                self.pan_banner.pack(side="top", fill="x", pady=(0, 5))
            else:
                # Verstecke Pan-Hinweis
                if hasattr(self, 'pan_banner'):
                    self.pan_banner.pack_forget()
        else:
            # Im dynamischen Modus: Pan-Modus deaktiviert
            self.pan_mode = False
            if hasattr(self, 'canvas'):
                self.canvas.set_pan_mode(False)
    
    def _check_for_updates(self):
        """Prüft auf Updates und zeigt Dialog."""
        self.update_manager.show_update_dialog()
    
    def _check_updates_on_start(self):
        """Prüft sofort beim Start auf Updates."""
        try:
            if self.update_manager.check_for_updates():
                result = messagebox.askyesno("Update Verfügbar", 
                                          "Ein Update ist verfügbar!\n"
                                          "Möchten Sie die Anwendung jetzt aktualisieren?\n\n"
                                          "Das Tool wird nach dem Update neu gestartet.")
                if result:
                    if self.update_manager.update_application():
                        # Tool neu starten nach Update
                        import sys
                        import os
                        os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception as e:
            print(f"Update-Check beim Start fehlgeschlagen: {e}")
    
    def _on_zoom_change(self, value):
        """Wird aufgerufen wenn der Zoom-Slider geändert wird."""
        try:
            zoom_level = float(value)
            # Deaktiviere Auto-Zoom wenn Benutzer manuell zoomt
            self.canvas.auto_zoom_enabled = False
            self.canvas.set_zoom_level(zoom_level)
        except (ValueError, AttributeError):
            pass
    

    def _update_radar(self):
        if self.config_data.get('ui', {}).get('enable_radar', False):
            projects = self.model.get_projects_list()
            tasks = self.model.get_tasks_for_project(self.current_project_id) if self.current_project_id else []
            self.radar.update_data(projects, tasks)

    def _refresh_all_ui_elements(self):
        # Aktualisiert alle UI-Elemente, wenn sich z.B. das Theme ändert
        bg_color = config.get_color(self.config_data, "background", "#0f0f0f")
        self.configure(bg=bg_color)
        # ... weitere UI-Updates hier ...
        self._refresh_view()

    def on_close(self):
        self.anim_manager.stop()
        self.stop_sync.set()
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()