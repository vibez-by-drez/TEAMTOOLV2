# -*- coding: utf-8 -*-
"""
UI-Komponenten für das Coworking Tool.
Enthält alle Tkinter-Widgets, Dialoge und benutzerdefinierten Canvas-Elemente.
"""

import json
import math
import random
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser

# Optionale UI-Bibliotheken
try:
    from PIL import Image, ImageDraw
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False

try:
    import webview
    WEBVIEW_AVAILABLE = True
except ImportError:
    WEBVIEW_AVAILABLE = False

# Lokale Importe
import config
from utils import now_iso

# ---------- Mini Radar Widget ----------
class MiniRadar(tk.Canvas):
    """Mini-Radar-Widget, das den Projekt-/Task-Status anzeigt."""
    def __init__(self, master, app_config, **kwargs):
        super().__init__(master, width=200, height=200, bg="#000011", highlightthickness=0, **kwargs)
        self.app_config = app_config
        self.radius = 80
        self.center_x = 100
        self.center_y = 100
        self.sweep_angle = 0
        self.data_points = []

    def update_data(self, projects, tasks):
        """Aktualisiert das Radar mit aktuellen Daten."""
        if not self.app_config.get('ui', {}).get('enable_radar', False):
            return

        self.data_points = []

        # Projekte als äußere Ringpunkte hinzufügen
        for i, project in enumerate(projects[:8]):
            angle = (i / len(projects)) * 360 if projects else 0
            distance = 60

            deadline = project.get("deadline", "")
            urgency = 0.5
            if deadline:
                try:
                    deadline_date = datetime.strptime(deadline, "%Y-%m-%d")
                    days_until = (deadline_date - datetime.now()).days
                    urgency = max(0.1, min(1.0, 1.0 - (days_until / 30)))
                except:
                    pass

            self.data_points.append({
                'x': self.center_x + distance * math.cos(math.radians(angle)),
                'y': self.center_y + distance * math.sin(math.radians(angle)),
                'type': 'project', 'urgency': urgency, 'name': project.get("name", "")[:10]
            })

        # Tasks als innere Ringpunkte hinzufügen
        for i, task in enumerate(tasks[:6]):
            angle = (i / len(tasks)) * 360 if tasks else 0
            distance = 30
            progress = self._calculate_task_progress(task)

            self.data_points.append({
                'x': self.center_x + distance * math.cos(math.radians(angle)),
                'y': self.center_y + distance * math.sin(math.radians(angle)),
                'type': 'task', 'progress': progress / 100.0, 'name': task.get("name", "")[:8]
            })

        self._draw_radar()

    def _calculate_task_progress(self, task):
        try:
            checklist = json.loads(task.get("checklist_json", "[]"))
            if not checklist: return 0
            done = sum(1 for item in checklist if item.get("done", False))
            return int((done / len(checklist)) * 100) if checklist else 0
        except:
            return 0

    def _draw_radar(self):
        self.delete("all")
        for r in [20, 40, 60, 80]:
            self.create_oval(self.center_x - r, self.center_y - r, self.center_x + r, self.center_y + r, outline="#333333", width=1)

        sweep_x = self.center_x + self.radius * math.cos(math.radians(self.sweep_angle))
        sweep_y = self.center_y + self.radius * math.sin(math.radians(self.sweep_angle))
        self.create_line(self.center_x, self.center_y, sweep_x, sweep_y, fill="#00ff00", width=2)

        for point in self.data_points:
            if point['type'] == 'project':
                color = "#ff0000" if point['urgency'] > 0.7 else "#ffff00" if point['urgency'] > 0.4 else "#00ff00"
                self.create_oval(point['x'] - 4, point['y'] - 4, point['x'] + 4, point['y'] + 4, fill=color, outline="white", width=1)
            else:
                progress = point['progress']
                color = "#00ff88" if progress == 1.0 else "#0088ff"
                size = int(3 + progress * 3)
                self.create_oval(point['x'] - size, point['y'] - size, point['x'] + size, point['y'] + size, fill=color, outline="white", width=1)

        self.sweep_angle = (self.sweep_angle + 2) % 360
        self.after(50, self._draw_radar)

# ---------- Dialoge und UI-Elemente ----------
class ModalDialog:
    """Basisklasse für modale Dialoge, die als Overlay im Hauptfenster erscheinen."""
    def __init__(self, parent, title, width=500, height=400):
        self.parent = parent
        self.title = title
        self.width = width
        self.height = height
        self.result = None
        self.overlay = None
        self.dialog_frame = None
        self.on_result = None

    def show(self):
        app_config = getattr(self.parent, 'config_data', {})
        overlay_bg = config.get_color(app_config, "background", "#0f0f0f")
        dialog_bg = config.get_color(app_config, "surface", "#1b1b1b")
        title_bg = config.get_color(app_config, "surface_light", "#2a2a2a")

        self.overlay = tk.Frame(self.parent, bg=overlay_bg, highlightthickness=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.dialog_frame = tk.Frame(self.overlay, bg=dialog_bg, relief="raised", bd=2)
        self.dialog_frame.place(relx=0.5, rely=0.5, anchor="center", width=self.width, height=self.height)

        title_frame = tk.Frame(self.dialog_frame, bg=title_bg, height=40)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text=self.title, bg=title_bg, fg="#000000", font=("Helvetica", 12, "bold")).pack(side="left", padx=15, pady=10)
        tk.Button(title_frame, text="×", bg=title_bg, fg="#000000", font=("Helvetica", 16, "bold"), bd=0, command=self.hide).pack(side="right", padx=10, pady=5)

        self.content_frame = tk.Frame(self.dialog_frame, bg=dialog_bg)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.overlay.bind("<Escape>", lambda e: self.hide())
        self.overlay.focus_set()

        self.create_content()
        self.dialog_frame.grab_set()

    def hide(self):
        if self.overlay:
            self.dialog_frame.grab_release()
            self.overlay.destroy()
            if self.on_result and self.result is None:
                self.on_result(None)

    def create_content(self):
        pass

class NewProjectDialog(ModalDialog):
    def __init__(self, parent, on_result=None):
        super().__init__(parent, "Neues Projekt anlegen", 500, 350)
        self.on_result = on_result

    def create_content(self):
        app_config = getattr(self.parent, 'config_data', {})
        self.bg_color = config.get_color(app_config, "surface", "#1b1b1b")

        self.var_name = tk.StringVar()
        self.var_color = tk.StringVar(value="#222222")
        self.var_deadline = tk.StringVar()

        tk.Label(self.content_frame, text="Projektname:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.name_entry = tk.Entry(self.content_frame, textvariable=self.var_name, font=("Helvetica", 11), bg=self.bg_color, fg="#000000", insertbackground="#000000", relief="flat", bd=5)
        self.name_entry.pack(fill="x", pady=(0, 15))

        tk.Label(self.content_frame, text="Farbe:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        color_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        color_frame.pack(fill="x", pady=(0, 15))

        self.color_preview = tk.Canvas(color_frame, width=40, height=30, highlightthickness=2, highlightbackground="#555", bg=self.bg_color)
        self.color_preview.pack(side="left", padx=(0, 10))
        self.color_preview.create_rectangle(2, 2, 38, 28, fill=self.var_color.get(), outline="")

        tk.Button(color_frame, text="Farbe wählen", command=self._pick_color, bg=self.bg_color, fg="#000000", font=("Helvetica", 9), relief="sunken", bd=2).pack(side="left")

        tk.Label(self.content_frame, text="Deadline (YYYY-MM-DD):", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.deadline_entry = tk.Entry(self.content_frame, textvariable=self.var_deadline, font=("Helvetica", 11), bg=self.bg_color, fg="#000000", insertbackground="#000000", relief="flat", bd=5)
        self.deadline_entry.pack(fill="x", pady=(0, 20))

        btn_frame = tk.Frame(self.content_frame, bg=self.bg_color)
        btn_frame.pack(fill="x", side="bottom")
        tk.Button(btn_frame, text="Abbrechen", command=self.hide, bg="#333333", fg="#000000", font=("Helvetica", 10), relief="sunken", bd=2, padx=20, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="right", padx=(10, 0))
        tk.Button(btn_frame, text="Projekt anlegen", command=self._ok, bg="#333333", fg="#000000", font=("Helvetica", 10, "bold"), relief="sunken", bd=2, padx=20, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="right")

        self.name_entry.focus()
        self.content_frame.bind("<Return>", lambda e: self._ok())

    def _pick_color(self):
        color_code = colorchooser.askcolor(color=self.var_color.get())[1]
        if color_code:
            self.var_color.set(color_code)
            self.color_preview.create_rectangle(2, 2, 38, 28, fill=color_code, outline="")

    def _ok(self):
        name = self.var_name.get().strip()
        if not name:
            messagebox.showwarning("Fehlend", "Bitte einen Projektnamen eingeben.")
            return
        deadline = self.var_deadline.get().strip()
        if deadline and len(deadline) != 10:
            messagebox.showwarning("Format", "Bitte Deadline als YYYY-MM-DD eingeben.")
            return
        self.result = (name, self.var_color.get(), deadline)
        if self.on_result:
            self.on_result(self.result)
        self.hide()

class TaskEditor(ModalDialog):
    def __init__(self, parent, model, task, on_save, on_delete, current_user):
        super().__init__(parent, "Task bearbeiten", 644, 860)
        self.model = model
        self.task = task
        self.on_save = on_save
        self.on_delete = on_delete
        self.current_user = current_user

    def create_content(self):
        app_config = getattr(self.parent, 'config_data', {})
        self.bg_color = config.get_color(app_config, "surface", "#1b1b1b")

        self.var_name = tk.StringVar(value=self.task.get("name", ""))
        self.var_goal = tk.StringVar(value=self.task.get("goal", ""))
        
        # Handle both old single assignee and new multi-assignee format
        assignee_data = self.task.get("assignee", "")
        if isinstance(assignee_data, list):
            self.selected_assignees = assignee_data.copy()
        elif assignee_data:
            self.selected_assignees = [assignee_data]
        else:
            self.selected_assignees = []

        # Create a main container for the scrollable area
        scroll_container = tk.Frame(self.content_frame, bg=self.bg_color)
        scroll_container.pack(fill="both", expand=True, padx=10, pady=(10, 0))
        
        canvas = tk.Canvas(scroll_container, bg=self.bg_color, highlightthickness=0)
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.bg_color)
        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        tk.Label(scrollable_frame, text="Task Name:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        tk.Entry(scrollable_frame, textvariable=self.var_name, font=("Helvetica", 11), bg="#f8f8f8", fg="#000000", insertbackground="#000000", relief="sunken", bd=3).pack(fill="x", pady=(0, 15))

        tk.Label(scrollable_frame, text="Task Ziel:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        tk.Entry(scrollable_frame, textvariable=self.var_goal, font=("Helvetica", 11), bg="#f8f8f8", fg="#000000", insertbackground="#000000", relief="sunken", bd=3).pack(fill="x", pady=(0, 15))

        tk.Label(scrollable_frame, text="Beschreibung:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.txt_desc = tk.Text(scrollable_frame, height=4, wrap="word", font=("Helvetica", 10), bg="#f8f8f8", fg="#000000", insertbackground="#000000", relief="sunken", bd=3)
        self.txt_desc.pack(fill="x", pady=(0, 15))
        self.txt_desc.insert("1.0", self.task.get("description", ""))

        tk.Label(scrollable_frame, text="Beachtung:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.txt_attention = tk.Text(scrollable_frame, height=3, wrap="word", font=("Helvetica", 10), bg="#f8f8f8", fg="#000000", insertbackground="#000000", relief="sunken", bd=3)
        self.txt_attention.pack(fill="x", pady=(0, 15))
        self.txt_attention.insert("1.0", self.task.get("attention", ""))

        tk.Label(scrollable_frame, text="Bearbeitet von:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 5))
        
        # Create multi-select interface for assignees
        self.assignee_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        self.assignee_frame.pack(fill="x", pady=(0, 15))
        
        # Create checkboxes for each user
        self.assignee_vars = {}
        for i, user in enumerate(config.USERS):
            var = tk.BooleanVar(value=user in self.selected_assignees)
            self.assignee_vars[user] = var
            
            cb_frame = tk.Frame(self.assignee_frame, bg=self.bg_color)
            cb_frame.pack(fill="x", pady=2)
            
            cb = tk.Checkbutton(cb_frame, variable=var, text=user, 
                              bg=self.bg_color, fg="#000000", 
                              selectcolor="#4CAF50", activebackground=self.bg_color,
                              font=("Helvetica", 10), anchor="w")
            cb.pack(side="left")
            
            # Add color indicator
            if user in config.ASSIGNEE_COLORS:
                color = config.ASSIGNEE_COLORS[user]
                color_canvas = tk.Canvas(cb_frame, width=20, height=20, bg=self.bg_color, highlightthickness=0)
                color_canvas.pack(side="right", padx=(10, 0))
                color_canvas.create_oval(3, 3, 17, 17, fill=color, outline="#555555", width=2)

        self.lbl_update = tk.Label(scrollable_frame, text=f"Letztes Update: {self.task.get('last_update', '')}", bg=self.bg_color, fg="#000000", font=("Helvetica", 9))
        self.lbl_update.pack(anchor="e", pady=(0, 20))

        tk.Label(scrollable_frame, text="To-Do Liste:", bg=self.bg_color, fg="#000000", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(0, 10))
        self.checklist_frame = tk.Frame(scrollable_frame, bg=self.bg_color)
        self.checklist_frame.pack(fill="x", pady=(0, 10))
        self.check_items = []
        try:
            checklist = json.loads(self.task.get("checklist_json", "[]"))
        except:
            checklist = []
        for item in checklist:
            self._add_check_item(item.get("text", ""), bool(item.get("done", False)))
        tk.Button(scrollable_frame, text="+ To-Do hinzufügen", command=self._on_add_item, bg="#cccccc", fg="#000000", font=("Helvetica", 9), relief="sunken", bd=2, activebackground="#dddddd", activeforeground="#000000").pack(anchor="w", pady=(0, 20))

        # Pack canvas and scrollbar in the scroll container
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Buttons in a separate frame at the bottom with fixed height
        btn_frame = tk.Frame(self.content_frame, bg=self.bg_color, height=60)
        btn_frame.pack(fill="x", side="bottom", pady=(5, 10))
        btn_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        tk.Button(btn_frame, text="Löschen", command=self._on_delete, bg="#333333", fg="#000000", font=("Helvetica", 10), relief="sunken", bd=2, padx=20, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="left", padx=(0, 10))
        tk.Button(btn_frame, text="Speichern", command=self._on_save, bg="#333333", fg="#000000", font=("Helvetica", 10, "bold"), relief="sunken", bd=2, padx=20, pady=8, activebackground="#444444", activeforeground="#000000").pack(side="right")

        # Auto-assign current user if no assignees are selected and current_user is set
        if not self.selected_assignees and self.current_user and self.current_user in config.USERS:
            if hasattr(self, 'assignee_vars') and self.current_user in self.assignee_vars:
                self.assignee_vars[self.current_user].set(True)
                self.selected_assignees = [self.current_user]

    def _on_add_item(self):
        self._add_check_item("", False)

    def _add_check_item(self, text, done):
        var_b = tk.BooleanVar(value=done)
        var_t = tk.StringVar(value=text)
        item_frame = tk.Frame(self.checklist_frame, bg=self.bg_color)
        item_frame.pack(fill="x", pady=2)
        tk.Checkbutton(item_frame, variable=var_b, bg=self.bg_color, fg="#000000", selectcolor="#4CAF50", activebackground=self.bg_color, relief="sunken", bd=2).pack(side="left", padx=(0, 8))
        tk.Entry(item_frame, textvariable=var_t, font=("Helvetica", 10), bg="#f8f8f8", fg="#000000", insertbackground="#000000", relief="sunken", bd=3).pack(side="left", fill="x", expand=True)
        self.check_items.append((var_b, var_t))

    def _collect_checklist(self):
        return [{"text": var_t.get().strip(), "done": bool(var_b.get())} for var_b, var_t in self.check_items if var_t.get().strip()]

    def _on_delete(self):
        if messagebox.askyesno("Bestätigen", "Diesen Task wirklich löschen?"):
            self.on_delete(self.task["task_id"])
            self.hide()

    def _on_save(self):
        self.task["name"] = self.var_name.get().strip()
        self.task["goal"] = self.var_goal.get().strip()
        self.task["description"] = self.txt_desc.get("1.0", "end").strip()
        self.task["attention"] = self.txt_attention.get("1.0", "end").strip()
        
        # Collect selected assignees
        selected_assignees = [user for user, var in self.assignee_vars.items() if var.get()]
        self.task["assignee"] = selected_assignees
        
        self.task["checklist_json"] = json.dumps(self._collect_checklist(), ensure_ascii=False)
        self.task["last_update"] = now_iso()
        self.lbl_update.configure(text=f"Letztes Update: {self.task['last_update']}")
        self.on_save(self.task)
        self.hide()

class SettingsDialog(ModalDialog):
    def __init__(self, parent, app_config, on_save):
        super().__init__(parent, "⚙️ Einstellungen", 800, 600)
        self.config_data = app_config
        self.on_save = on_save
        self.on_result = lambda r: self._save() # Save on close if not cancelled

    def show(self):
        # Override the parent show method to use light colors for settings dialog
        self.overlay = tk.Frame(self.parent, bg="#808080", highlightthickness=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.dialog_frame = tk.Frame(self.overlay, bg="white", relief="raised", bd=2)
        self.dialog_frame.place(relx=0.5, rely=0.5, anchor="center", width=self.width, height=self.height)

        title_frame = tk.Frame(self.dialog_frame, bg="#f0f0f0", height=40)
        title_frame.pack(fill="x", padx=0, pady=0)
        title_frame.pack_propagate(False)

        tk.Label(title_frame, text=self.title, bg="#f0f0f0", fg="black", font=("Helvetica", 12, "bold")).pack(side="left", padx=15, pady=10)
        tk.Button(title_frame, text="×", bg="#f0f0f0", fg="black", font=("Helvetica", 16, "bold"), bd=0, command=self.hide).pack(side="right", padx=10, pady=5)

        self.content_frame = tk.Frame(self.dialog_frame, bg="white")
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.overlay.bind("<Escape>", lambda e: self.hide())
        self.overlay.focus_set()

        self.create_content()
        self.dialog_frame.grab_set()

    def create_content(self):
        # Set a white background for the content
        self.content_frame.configure(bg="white")
        self.dialog_frame.configure(bg="white")

        # Create a simple notebook-like interface with buttons
        tab_frame = tk.Frame(self.content_frame, bg="white")
        tab_frame.pack(fill="x", padx=10, pady=(10, 0))
        
        # Tab buttons
        self.general_btn = tk.Button(tab_frame, text="Allgemein", 
                                   command=self._show_general,
                                   bg="#007acc", fg="white", relief="sunken", bd=2, padx=20, pady=8)
        self.general_btn.pack(side="left", padx=(0, 5))
        
        self.visual_btn = tk.Button(tab_frame, text="Darstellung", 
                                  command=self._show_visual,
                                  bg="#f0f0f0", fg="black", relief="raised", bd=2, padx=20, pady=8)
        self.visual_btn.pack(side="left")

        # Content area
        self.content_area = tk.Frame(self.content_frame, bg="white")
        self.content_area.pack(fill="both", expand=True, padx=10, pady=10)

        # Create both tabs but only show one
        self._create_general_tab(self.content_area)
        self._create_visual_tab(self.content_area)
        
        # Show general tab by default
        self._show_general()
        
        # Force immediate rendering to fix initial visibility bug
        self.dialog_frame.update_idletasks()
        self.content_frame.update_idletasks()
        self.content_area.update_idletasks()
        self.general_frame.update_idletasks()
        self.visual_frame.update_idletasks()

        # Buttons
        btn_frame = tk.Frame(self.content_frame, bg="white")
        btn_frame.pack(fill="x", side="bottom", pady=10, padx=10)
        tk.Button(btn_frame, text="Abbrechen", command=self.hide, bg="#e0e0e0", fg="black", relief="sunken", bd=3, padx=20, pady=8, font=("Helvetica", 10, "bold")).pack(side="right", padx=(10, 0))
        tk.Button(btn_frame, text="Speichern", command=self._ok, bg="#007acc", fg="white", relief="sunken", bd=3, padx=20, pady=8, font=("Helvetica", 10, "bold")).pack(side="right")

    def _show_general(self):
        # Hide visual frame
        self.visual_frame.pack_forget()
        # Show general frame
        self.general_frame.pack(fill="both", expand=True)
        # Update button styles
        self.general_btn.configure(bg="#007acc", fg="white", relief="sunken")
        self.visual_btn.configure(bg="#f0f0f0", fg="black", relief="raised")
        # Force immediate rendering
        self.general_frame.update_idletasks()

    def _show_visual(self):
        # Hide general frame
        self.general_frame.pack_forget()
        # Show visual frame
        self.visual_frame.pack(fill="both", expand=True)
        # Update button styles
        self.general_btn.configure(bg="#f0f0f0", fg="black", relief="raised")
        self.visual_btn.configure(bg="#007acc", fg="white", relief="sunken")
        # Force immediate rendering
        self.visual_frame.update_idletasks()

    def _create_general_tab(self, parent):
        self.general_frame = tk.Frame(parent, bg="white")
        self.var_sheet = tk.StringVar(value=self.config_data.get("sheet_id",""))
        self.var_json = tk.StringVar(value=self.config_data.get("service_account_json",""))
        self.var_user = tk.StringVar(value=self.config_data.get("current_user",""))
        self.var_poll = tk.StringVar(value=str(self.config_data.get("poll_seconds", config.DEFAULT_POLL_SECONDS)))

        tk.Label(self.general_frame, text="Google Sheet ID:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        sheet_entry = tk.Entry(self.general_frame, textvariable=self.var_sheet, width=52, bg="#f8f8f8", fg="black", font=("Helvetica", 10), relief="sunken", bd=3, insertbackground="black")
        sheet_entry.grid(row=0, column=1, sticky="we", pady=5)
        
        tk.Label(self.general_frame, text="Service-Account JSON Pfad:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        json_entry = tk.Entry(self.general_frame, textvariable=self.var_json, width=52, bg="#f8f8f8", fg="black", font=("Helvetica", 10), relief="sunken", bd=3, insertbackground="black")
        json_entry.grid(row=1, column=1, sticky="we", pady=5)
        tk.Button(self.general_frame, text="Datei wählen", command=self._pick_json, bg="#d0d0d0", fg="black", relief="sunken", bd=3, font=("Helvetica", 9)).grid(row=1, column=2, padx=(6,0), pady=5)
        
        tk.Label(self.general_frame, text="Aktiver Nutzer:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=2, column=0, sticky="w", pady=5)
        user_combo = tk.OptionMenu(self.general_frame, self.var_user, *config.USERS)
        user_combo.config(bg="#f8f8f8", fg="black", relief="sunken", bd=3, font=("Helvetica", 10))
        user_combo.grid(row=2, column=1, sticky="w", pady=5)
        
        tk.Label(self.general_frame, text="Sync-Intervall (Sek.):", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=3, column=0, sticky="w", pady=5)
        poll_entry = tk.Entry(self.general_frame, textvariable=self.var_poll, width=8, bg="#f8f8f8", fg="black", font=("Helvetica", 10), relief="sunken", bd=3, insertbackground="black")
        poll_entry.grid(row=3, column=1, sticky="w", pady=5)
        self.general_frame.columnconfigure(1, weight=1)
        
        # Force immediate rendering of all widgets
        self.general_frame.update_idletasks()

    def _create_visual_tab(self, parent):
        self.visual_frame = tk.Frame(parent, bg="white")
        ui_cfg = self.config_data.get('ui', {})
        self.vars = {
            'galaxy_bg': tk.BooleanVar(value=ui_cfg.get('enable_galaxy_bg', False)),
            'deadline_halo': tk.BooleanVar(value=ui_cfg.get('enable_deadline_halo', True)),
            'progress_ring': tk.BooleanVar(value=ui_cfg.get('enable_progress_ring', True)),
            'radar': tk.BooleanVar(value=ui_cfg.get('enable_radar', False)),
            'focus_mode': tk.BooleanVar(value=ui_cfg.get('enable_focus_mode', False)),
            'tooltips': tk.BooleanVar(value=ui_cfg.get('enable_tooltips', True)),
            'floating_animation': tk.BooleanVar(value=ui_cfg.get('enable_floating_animation', True)),
            'floating_speed': tk.DoubleVar(value=ui_cfg.get('floating_speed', 0.07)),
        }
        r = 0
        tk.Label(self.visual_frame, text="Visuelle Effekte:", bg="white", fg="black", font=("Helvetica", 12, "bold")).grid(row=r, column=0, columnspan=2, sticky="w", pady=(10,5)); r+=1
        for key, text in [('galaxy_bg', 'Galaxy Hintergrund'), ('deadline_halo', 'Deadline Halos'), ('progress_ring', 'Progress Ringe'), ('radar', 'Mini Radar'), ('focus_mode', 'Focus Mode'), ('tooltips', 'Hover Tooltips')]:
            cb = tk.Checkbutton(self.visual_frame, text=text, variable=self.vars[key], bg="white", fg="black", selectcolor="#4CAF50", activebackground="white", relief="sunken", bd=3, font=("Helvetica", 10))
            cb.grid(row=r, column=0, columnspan=2, sticky="w", pady=3); r+=1
        
        # Schwebebewegung Checkbox
        floating_cb = tk.Checkbutton(self.visual_frame, text="Schwebebewegung aktivieren", 
                                   variable=self.vars['floating_animation'], bg="white", fg="black", 
                                   selectcolor="#4CAF50", activebackground="white", relief="sunken", bd=3, 
                                   font=("Helvetica", 10, "bold"))
        floating_cb.grid(row=r, column=0, columnspan=2, sticky="w", pady=(10,5)); r+=1
        
        # Schwebegeschwindigkeit Slider
        tk.Label(self.visual_frame, text="Schwebegeschwindigkeit:", bg="white", fg="black", font=("Helvetica", 10, "bold")).grid(row=r, column=0, sticky="w", pady=(5,5)); r+=1
        speed_slider = tk.Scale(self.visual_frame, from_=0.01, to=0.2, resolution=0.01, orient="horizontal", 
                               variable=self.vars['floating_speed'], bg="white", fg="black", 
                               font=("Helvetica", 9), length=200)
        speed_slider.grid(row=r, column=0, columnspan=2, sticky="w", pady=5); r+=1
        
        # Force immediate rendering of all widgets
        self.visual_frame.update_idletasks()

    def _pick_json(self):
        path = filedialog.askopenfilename(title="Service-Account JSON auswählen", filetypes=[("JSON","*.json"),("Alle Dateien","*.*")])
        if path: self.var_json.set(path)

    def _ok(self):
        self._save()
        self.hide()

    def _save(self):
        self.config_data["sheet_id"] = self.var_sheet.get().strip()
        self.config_data["service_account_json"] = self.var_json.get().strip()
        self.config_data["current_user"] = self.var_user.get().strip()
        try: self.config_data["poll_seconds"] = max(2, int(self.var_poll.get()))
        except: self.config_data["poll_seconds"] = config.DEFAULT_POLL_SECONDS

        if 'ui' not in self.config_data: self.config_data['ui'] = {}
        for key, var in self.vars.items():
            if key == 'floating_speed':
                self.config_data['ui']['floating_speed'] = var.get()
            elif key == 'floating_animation':
                self.config_data['ui']['enable_floating_animation'] = var.get()
            else:
                self.config_data['ui'][f'enable_{key}'] = var.get()

        config.save_config(self.config_data)
        self.on_save(self.config_data)

class LegendWidget(tk.Frame):
    def __init__(self, master, app_config, **kwargs):
        super().__init__(master, **kwargs)
        self.app_config = app_config
        surface_light = config.get_color(self.app_config, "surface_light", "#2a2a2a")
        border_light = config.get_color(self.app_config, "border_light", "#666666")
        self.configure(bg=surface_light, relief="raised", bd=2, height=50)
        self.pack_propagate(False)

        tk.Label(self, text="👥 Bearbeiter:", font=("Helvetica", 11, "bold"), fg="#000000", bg=surface_light).pack(side="left", padx=(15, 10), pady=12)

        for user in config.USERS:
            if user in config.ASSIGNEE_COLORS:
                color = config.ASSIGNEE_COLORS[user]
                user_frame = tk.Frame(self, bg=surface_light)
                user_frame.pack(side="left", padx=5, pady=8)
                color_canvas = tk.Canvas(user_frame, width=20, height=20, bg=surface_light, highlightthickness=0)
                color_canvas.pack(side="left", padx=(0, 6))
                color_canvas.create_oval(3, 3, 17, 17, fill=color, outline=border_light, width=2)
                tk.Label(user_frame, text=user, font=("Helvetica", 10, "bold"), fg="#000000", bg=surface_light).pack(side="left")

class BubbleCanvas(tk.Canvas):
    def __init__(self, master, app_config, **kwargs):
        bg_color = config.get_color(app_config, "background", "#111111")
        super().__init__(master, bg=bg_color, highlightthickness=0, **kwargs)
        self.app_config = app_config
        self.items_map = []
        self.tooltip = None
        self.tooltip_data = None
        self.galaxy_animation_id = None
        self.stars = []
        self.galaxy_animation_offset = 0
        
        # Schwebebewegung für Bubbles
        self.floating_animation_id = None
        self.floating_offset = 0
        self.bubble_groups = []  # Speichert Gruppen von zusammengehörigen Bubble-Elementen
        self.asteroid_animation_id = None  # Animation für Asteroiden

        self.bind("<Configure>", lambda e: self.redraw())
        self.bind("<Motion>", self._on_mouse_move)
        self.bind("<Leave>", self._on_mouse_leave)

    def clear(self):
        self.delete("all")
        self.items_map.clear()
        self.bubble_groups.clear()
        self._hide_tooltip()
        # Stoppe Schwebebewegung
        if self.floating_animation_id:
            self.after_cancel(self.floating_animation_id)
            self.floating_animation_id = None
        # Stoppe Asteroid-Animation
        if self.asteroid_animation_id:
            self.after_cancel(self.asteroid_animation_id)
            self.asteroid_animation_id = None

    def draw_bubbles(self, data_list, label_key, bubble_type, on_click, assignee_getter=None):
        # Store current animation state before clearing
        was_floating_active = self.floating_animation_id is not None
        current_floating_offset = self.floating_offset
        
        self.clear()
        if self.app_config.get('ui', {}).get('enable_galaxy_bg', False):
            self._generate_galaxy_stars()
            self._animate_galaxy()

        w = self.winfo_width()
        h = self.winfo_height()
        if w < 50 or h < 50:
            self.after(50, lambda: self.draw_bubbles(data_list, label_key, bubble_type, on_click, assignee_getter))
            return

        radius = 80 if bubble_type == "project" else 70
        
        # Filtere gültige Objekte (Fokus-Modus berücksichtigen)
        valid_objects = []
        for obj in data_list:
            if (bubble_type == "task" and self.app_config.get('ui', {}).get('enable_focus_mode', False) and
                assignee_getter):
                # Für Multi-Assignee: Prüfe ob aktueller Benutzer in der Assignee-Liste ist
                assignees = assignee_getter(obj) or []
                if isinstance(assignees, str):
                    assignees = [assignees] if assignees else []
                elif not isinstance(assignees, list):
                    assignees = []
                
                current_user = self.app_config.get('current_user', '')
                if current_user and current_user not in assignees:
                    continue
            valid_objects.append(obj)
        
        if not valid_objects:
            return
        
        # Berechne Canvas-Mitte
        center_x = w // 2
        center_y = h // 2
        
        # Berechne kreisförmige Anordnung
        num_bubbles = len(valid_objects)
        if num_bubbles == 1:
            # Einzelne Bubble in der Mitte
            positions = [(center_x, center_y)]
        else:
            # Kreisförmige Anordnung
            positions = self._calculate_circular_positions(num_bubbles, center_x, center_y, w, h, radius)

        for i, obj in enumerate(valid_objects):
            x, y = positions[i]
            
            label = obj.get(label_key, "")[:18]
            color = obj.get("color") or "#222222"

            # Bubble-Gruppe für diese Bubble erstellen
            bubble_group = {
                'base_x': x,
                'base_y': y,
                'current_x': x,  # Aktuelle Position für kontinuierliche Animation
                'current_y': y,  # Aktuelle Position für kontinuierliche Animation
                'radius': radius,
                'items': [],
                'phase': random.uniform(0, 6.28),  # Zufällige Phase für individuelle Bewegung
                'rotation_offset': 0,  # Rotations-Offset für Ringe
                'ring_items': []  # Separate Liste für rotierende Ringe
            }

            if bubble_type == "project":
                halo_items = self._draw_deadline_halo(x, y, radius, obj.get("deadline", ""), obj.get("project_id"))
                if halo_items:
                    bubble_group['ring_items'].extend(halo_items)

            if bubble_type == "project":
                oval = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill="#1a1a1a", outline=color or "#444444", width=4)
                inner_ring = self.create_oval(x-radius+8, y-radius+8, x+radius-8, y-radius-8, fill="", outline="#ffffff", width=1)
                bubble_group['items'].extend([oval, inner_ring])
            else:
                oval = self.create_oval(x-radius, y-radius, x+radius, y+radius, fill=color, outline="#555555", width=3)
                inner_ring = self.create_oval(x-radius+6, y-radius+6, x+radius-6, y+radius-6, fill="", outline="#ffffff", width=1)
                bubble_group['items'].extend([oval, inner_ring])

            text_shadow = self.create_text(x+1, y+1, text=label, fill="#000000", font=("Helvetica", 12, "bold"), width=radius*1.6)
            text = self.create_text(x, y, text=label, fill="#ffffff", font=("Helvetica", 12, "bold"), width=radius*1.6)
            bubble_group['items'].extend([text_shadow, text])

            if bubble_type == "task":
                if assignee_getter:
                    assignees = assignee_getter(obj) or []
                    # Handle both old single assignee format and new list format
                    if isinstance(assignees, str):
                        assignees = [assignees] if assignees else []
                    elif not isinstance(assignees, list):
                        assignees = []
                    
                    # Limit to 4 assignees maximum
                    assignees = assignees[:4]
                    
                    if assignees:
                        self._draw_multi_assignee_ring(x, y, radius, assignees, bubble_group)
                progress_items = self._draw_progress_ring(x, y, radius, obj)
                if progress_items:
                    bubble_group['ring_items'].extend(progress_items)

            def make_cb(payload): return lambda e: on_click(payload)
            for item in bubble_group['items']:
                self.tag_bind(item, "<Button-1>", make_cb(obj))
                self.items_map.append((item, bubble_type, obj))
            
            # Auch Ring-Items für Klicks binden
            for item in bubble_group['ring_items']:
                self.tag_bind(item, "<Button-1>", make_cb(obj))
                self.items_map.append((item, bubble_type, obj))

            # Asteroiden für To-Do-Items hinzufügen (nur für Tasks)
            if bubble_type == "task":
                self._add_asteroids_to_bubble(bubble_group, obj, x, y, radius)
            
            # Bubble-Gruppe zur Liste hinzufügen
            self.bubble_groups.append(bubble_group)
        
        # Schwebebewegung starten
        self._start_floating_animation()
        # Asteroid-Animation starten
        self._start_asteroid_animation()
        
        # Restore animation state if it was previously active
        if was_floating_active:
            self.floating_offset = current_floating_offset

    def _draw_multi_assignee_ring(self, x, y, radius, assignees, bubble_group):
        """Draws a ring around the bubble with proportional color segments for multiple assignees."""
        import math
        
        num_assignees = len(assignees)
        if num_assignees == 0:
            return
        
        # Special case for single assignee - draw full circle
        if num_assignees == 1:
            color = config.ASSIGNEE_COLORS.get(assignees[0], "#777777")
            ring_item = self.create_oval(x - radius, y - radius, x + radius, y + radius, 
                                       outline=color, width=5)
            bubble_group['items'].append(ring_item)
            return
        
        # Multiple assignees - draw proportional segments
        segment_angle = 360.0 / num_assignees
        
        for i, assignee in enumerate(assignees):
            # Get color for this assignee
            color = config.ASSIGNEE_COLORS.get(assignee, "#777777")
            
            # Calculate start and end angles for this segment
            start_angle = i * segment_angle
            end_angle = (i + 1) * segment_angle
            
            # Calculate arc coordinates
            # We need to create an arc from start_angle to end_angle
            # Tkinter's create_arc works with start and extent angles
            extent_angle = end_angle - start_angle
            
            # Create the arc segment
            arc_item = self.create_arc(
                x - radius, y - radius, x + radius, y + radius,
                start=start_angle, extent=extent_angle,
                outline=color, width=5, style="arc"
            )
            bubble_group['items'].append(arc_item)

    def _add_asteroids_to_bubble(self, bubble_group, task, x, y, radius):
        """Fügt Asteroiden für To-Do-Items zu einer Bubble hinzu."""
        import json
        import math
        import random
        
        try:
            checklist = json.loads(task.get("checklist_json", "[]"))
            if not checklist:
                return
        except:
            return
        
        # Asteroiden-Liste für diese Bubble initialisieren
        bubble_group['asteroids'] = []
        
        # Für jedes To-Do-Item einen Asteroiden erstellen
        for i, item in enumerate(checklist):
            # Asteroid-Position berechnen (orbital um die Bubble)
            asteroid_angle = (i / len(checklist)) * 2 * math.pi
            asteroid_distance = radius + 30 + (i * 5)  # Verschiedene Entfernungen
            asteroid_x = x + asteroid_distance * math.cos(asteroid_angle)
            asteroid_y = y + asteroid_distance * math.sin(asteroid_angle)
            
            # Asteroid-Größe basierend auf To-Do-Status
            asteroid_size = 5 if item.get("done", False) else 7
            asteroid_color = "#000000" if item.get("done", False) else "#ff8800"  # Erledigte sind schwarz
            
            # Asteroid zeichnen (größer und sichtbarer)
            outline_color = "#ffffff" if not item.get("done", False) else "#333333"
            asteroid = self.create_oval(
                asteroid_x - asteroid_size, asteroid_y - asteroid_size,
                asteroid_x + asteroid_size, asteroid_y + asteroid_size,
                fill=asteroid_color, outline=outline_color, width=2
            )
            
            # Asteroid-Daten speichern
            asteroid_data = {
                'item': asteroid,
                'center_x': x,
                'center_y': y,
                'distance': asteroid_distance,
                'angle': asteroid_angle,
                'speed': 0.02 + (i * 0.005),  # Verschiedene Geschwindigkeiten
                'phase': random.uniform(0, 2 * math.pi),  # Zufällige Startphase
                'done': item.get("done", False)  # To-Do-Status speichern
            }
            
            bubble_group['asteroids'].append(asteroid_data)
            # Asteroiden nicht zu den Bubble-Items hinzufügen, um Flackern zu vermeiden

    def _start_asteroid_animation(self):
        """Startet die Asteroid-Animation."""
        if self.asteroid_animation_id:
            self.after_cancel(self.asteroid_animation_id)
        # Nur starten wenn Schwebebewegung aktiviert ist
        if self.app_config.get('ui', {}).get('enable_floating_animation', True):
            self._animate_asteroids()

    def _animate_asteroids(self):
        """Animiert alle Asteroiden um ihre Bubbles."""
        import math
        
        # Prüfe ob Schwebebewegung aktiviert ist (gleiche Einstellung wie für Bubbles)
        if not self.app_config.get('ui', {}).get('enable_floating_animation', True):
            return
        
        # Verwende die gleiche Geschwindigkeit wie die Schwebebewegung
        floating_speed = self.app_config.get('ui', {}).get('floating_speed', 0.07)
        
        for bubble_group in self.bubble_groups:
            if 'asteroids' not in bubble_group:
                continue
                
            for asteroid_data in bubble_group['asteroids']:
                # Asteroid um die Bubble rotieren lassen (Geschwindigkeit basierend auf Schwebeeinstellung)
                asteroid_data['angle'] += asteroid_data['speed'] * floating_speed * 2
                
                # Neue Position berechnen
                new_x = asteroid_data['center_x'] + asteroid_data['distance'] * math.cos(asteroid_data['angle'])
                new_y = asteroid_data['center_y'] + asteroid_data['distance'] * math.sin(asteroid_data['angle'])
                
                # Asteroid bewegen (nur die Asteroiden, nicht die Bubbles)
                asteroid_size = 5 if asteroid_data.get('done', False) else 7
                self.coords(asteroid_data['item'], 
                           new_x - asteroid_size, new_y - asteroid_size, 
                           new_x + asteroid_size, new_y + asteroid_size)
        
        # Animation fortsetzen (gleiche Framerate wie Schwebebewegung für maximale Flüssigkeit)
        self.asteroid_animation_id = self.after(6, self._animate_asteroids)  # Gleiche Framerate wie floating

    def _calculate_circular_positions(self, num_bubbles, center_x, center_y, canvas_width, canvas_height, bubble_radius):
        """Berechnet kreisförmige Positionen für Bubbles."""
        positions = []
        
        # Berechne optimalen Radius für den Kreis basierend auf Canvas-Größe
        max_radius = min(canvas_width, canvas_height) // 3
        min_radius = bubble_radius * 2
        
        # Dynamischer Radius basierend auf Anzahl der Bubbles
        if num_bubbles <= 3:
            circle_radius = min_radius + 50
        elif num_bubbles <= 6:
            circle_radius = min_radius + 80
        else:
            circle_radius = min_radius + 120
        
        # Begrenze auf Canvas-Größe
        circle_radius = min(circle_radius, max_radius)
        
        # Berechne Winkel zwischen den Bubbles
        angle_step = (2 * math.pi) / num_bubbles
        
        for i in range(num_bubbles):
            # Berechne Winkel für diese Bubble
            angle = i * angle_step + random.uniform(-0.2, 0.2)  # Kleine Zufälligkeit für natürlicheren Look
            
            # Berechne Position
            x = center_x + circle_radius * math.cos(angle)
            y = center_y + circle_radius * math.sin(angle)
            
            # Stelle sicher, dass die Bubble im Canvas bleibt
            x = max(bubble_radius, min(canvas_width - bubble_radius, x))
            y = max(bubble_radius, min(canvas_height - bubble_radius, y))
            
            positions.append((int(x), int(y)))
        
        return positions

    def _calculate_project_workload(self, project_id):
        """Berechnet die Arbeitslast eines Projekts basierend auf Tasks und ToDos."""
        try:
            # Alle Tasks für dieses Projekt holen
            tasks = self.model.get_tasks_for_project(project_id) if hasattr(self, 'model') else []
            if not tasks:
                return 0, 0  # Keine Tasks = keine Arbeitslast
            
            total_todos = 0
            completed_todos = 0
            total_tasks = len(tasks)
            
            for task in tasks:
                try:
                    checklist = json.loads(task.get("checklist_json", "[]"))
                    if checklist:
                        total_todos += len(checklist)
                        completed_todos += sum(1 for item in checklist if item.get("done", False))
                except:
                    continue
            
            # Arbeitslast = Anzahl Tasks + Anzahl ToDos
            workload = total_tasks + total_todos
            completion_rate = int((completed_todos / total_todos) * 100) if total_todos > 0 else 100
            
            return workload, completion_rate
        except:
            return 0, 0

    def _draw_deadline_halo(self, x, y, radius, deadline, project_id=None):
        if not self.app_config.get('ui', {}).get('enable_deadline_halo', True) or not deadline:
            return []
        try:
            days_until = (datetime.strptime(deadline, "%Y-%m-%d") - datetime.now()).days
            
            # Arbeitslast berechnen (nur Anzahl Tasks)
            workload, _ = self._calculate_project_workload(project_id) if project_id else (0, 100)
            
            # 1. Keine Ringe = Keine Tasks
            if workload == 0:
                return []
            
            # 2. FARBE: Nur basierend auf verbleibender Zeit (unabhängig von Tasks)
            if days_until >= 20: 
                color = "green"  # Grün - viel Zeit (20+ Tage)
            elif days_until >= 10: 
                color = "orange"  # Orange - mittlere Zeit (10-19 Tage)
            else: 
                color = "red"  # Rot - wenig Zeit (< 10 Tage)
            
            # 3. ANZAHL RINGE: Nur basierend auf Task-Anzahl (unabhängig von Zeit)
            if workload >= 8:  # 8+ Tasks = 3 Ringe
                num_rings = 3
            elif workload >= 4:  # 4-7 Tasks = 2 Ringe
                num_rings = 2
            else:  # 1-3 Tasks = 1 Ring
                num_rings = 1

            # 4. Ringe zeichnen
            halo_items = []
            halo_radius = radius + 15
            for i in range(num_rings):
                arc_radius = halo_radius + i * 5
                for start_angle in range(0, 360, 45):
                    item = self.create_arc(x-arc_radius, y-arc_radius, x+arc_radius, y+arc_radius, start=start_angle, extent=30, outline=color, width=2, style="arc")
                    halo_items.append(item)
            return halo_items
        except: 
            return []

    def _draw_progress_ring(self, x, y, radius, task):
        if not self.app_config.get('ui', {}).get('enable_progress_ring', True):
            return []
        progress = self._calculate_task_progress(task)
        if progress == 0: return []

        ring_items = []
        ring_radius = radius + 8
        progress_angle = int(360 * progress / 100)
        ring_items.append(self.create_arc(x - ring_radius, y - ring_radius, x + ring_radius, y + ring_radius, start=0, extent=360, outline="#333333", width=3, style="arc"))
        progress_color = "#00ff88" if progress == 100 else "#0088ff"
        ring_items.append(self.create_arc(x - ring_radius, y - ring_radius, x + ring_radius, y + ring_radius, start=90, extent=progress_angle, outline=progress_color, width=3, style="arc"))
        ring_items.append(self.create_text(x, y + ring_radius + 15, text=f"{progress}%", fill="white", font=("Helvetica", 8, "bold")))
        return ring_items

    def _calculate_task_progress(self, task):
        try:
            checklist = json.loads(task.get("checklist_json", "[]"))
            if not checklist: return 0
            done = sum(1 for item in checklist if item.get("done", False))
            return int((done / len(checklist)) * 100) if checklist else 0
        except:
            return 0

    def redraw(self): pass # Redraws are handled externally

    def _on_mouse_move(self, event):
        if not self.app_config.get('ui', {}).get('enable_tooltips', True): return
        item = self.find_closest(event.x, event.y)
        if not item: self._hide_tooltip(); return

        for item_id, item_type, payload in self.items_map:
            if item_id == item[0]:
                self._show_tooltip(event.x_root, event.y_root, payload, item_type)
                return
        self._hide_tooltip()

    def _on_mouse_leave(self, event): self._hide_tooltip()

    def _hide_tooltip(self):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
            self.tooltip_data = None

    def _show_tooltip(self, x, y, payload, item_type):
        if self.tooltip_data == payload: return
        self._hide_tooltip()

        if item_type == "project":
            content = f"Projekt: {payload.get('name', '')}\nDeadline: {payload.get('deadline', 'N/A')}"
        else:
            content = f"Task: {payload.get('name', '')}\nBearbeiter: {payload.get('assignee', 'N/A')}\nFortschritt: {self._calculate_task_progress(payload)}%"

        self.tooltip = tk.Toplevel(self)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x+15}+{y+10}")
        tk.Label(self.tooltip, text=content, bg="#1a1a1a", fg="#ffffff", font=("Helvetica", 9), relief="solid", bd=1, padx=8, pady=4).pack()
        self.tooltip_data = payload

    def _generate_galaxy_stars(self):
        self.stars.clear()
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or h < 50: return
        for _ in range(100):
            self.stars.append({'x': random.randint(0, w), 'y': random.randint(0, h), 'size': random.choice([1, 2, 3]), 'brightness': random.randint(50, 150), 'speed': random.uniform(0.5, 2.0), 'phase': random.uniform(0, 6.28)})

    def _animate_galaxy(self):
        if not self.app_config.get('ui', {}).get('enable_galaxy_bg', False):
            if self.galaxy_animation_id: self.after_cancel(self.galaxy_animation_id)
            self.galaxy_animation_id = None
            return

        self.delete("galaxy")
        self.galaxy_animation_offset += 0.01
        w, h = self.winfo_width(), self.winfo_height()
        if w < 50 or h < 50: return

        for star in self.stars:
            x = (star['x'] + self.galaxy_animation_offset * star['speed'] * 5) % w
            y = (star['y'] + self.galaxy_animation_offset * star['speed'] * 3) % h
            twinkle = 0.5 + 0.5 * math.sin(star['phase'] + self.galaxy_animation_offset * star['speed'])
            brightness = int(star['brightness'] * twinkle)
            if brightness > 80:
                color = f"#{min(brightness//3, 80):02x}{min(brightness//3, 80):02x}{min(brightness//3, 80):02x}"
                self.create_oval(x-star['size'], y-star['size'], x+star['size'], y+star['size'], fill=color, outline="", tags="galaxy")

        self.galaxy_animation_id = self.after(50, self._animate_galaxy)

    def _start_floating_animation(self):
        """Startet die Schwebebewegung für alle Bubbles."""
        if not self.bubble_groups:
            return
        
        # Stoppe vorherige Animation falls vorhanden
        if self.floating_animation_id:
            self.after_cancel(self.floating_animation_id)
        
        self._animate_floating()

    def _animate_floating(self):
        """Animiert die Schwebebewegung aller Bubbles."""
        if not self.bubble_groups:
            return
        
        # Prüfe ob Schwebebewegung aktiviert ist
        if not self.app_config.get('ui', {}).get('enable_floating_animation', True):
            return
        
        # Geschwindigkeit aus Konfiguration lesen
        floating_speed = self.app_config.get('ui', {}).get('floating_speed', 0.07)
        self.floating_offset += floating_speed
        
        for bubble_group in self.bubble_groups:
            # Kontinuierliche Drift-Animation ohne Sprünge
            phase = self.floating_offset + bubble_group['phase']
            
            # Sanfte Drift-Bewegung (kleine, kontinuierliche Änderungen)
            drift_x = math.sin(phase * 0.3) * 0.8  # Sehr kleine X-Drift
            drift_y = math.sin(phase * 0.5) * 1.2  # Sehr kleine Y-Drift
            
            # Aktualisiere aktuelle Position kontinuierlich (nur Drift, keine Basis-Rückkehr)
            bubble_group['current_x'] += drift_x * 0.05
            bubble_group['current_y'] += drift_y * 0.05
            
            # Ring-Rotation aktualisieren
            bubble_group['rotation_offset'] += 0.02  # Rotationsgeschwindigkeit
            
            # Aktualisiere alle Items in der Bubble-Gruppe
            self._update_bubble_items(bubble_group)
            
            # Ring-Items rotieren
            self._rotate_ring_items(bubble_group, bubble_group['current_x'], bubble_group['current_y'])
        
        # Nächste Animation planen (6ms = ~166 FPS für Mikro-Schritte)
        self.floating_animation_id = self.after(6, self._animate_floating)

    def _update_bubble_items(self, bubble_group):
        """Aktualisiert alle Items einer Bubble-Gruppe mit der aktuellen Position."""
        current_x = bubble_group['current_x']
        current_y = bubble_group['current_y']
        radius = bubble_group['radius']
        
        for item in bubble_group['items']:
            try:
                # Hole aktuelle Koordinaten
                coords = self.coords(item)
                if not coords:
                    continue
                
                # Berechne neue Position basierend auf Item-Typ
                if len(coords) >= 4:  # Oval oder Arc
                    # Für Ovale und Arcs: [x1, y1, x2, y2]
                    self.coords(item, current_x - radius, current_y - radius, 
                              current_x + radius, current_y + radius)
                elif len(coords) >= 2:  # Text
                    # Für Text: [x, y]
                    self.coords(item, current_x, current_y)
            except:
                # Falls ein Item nicht mehr existiert, ignorieren
                continue

    def _rotate_ring_items(self, bubble_group, current_x, current_y):
        """Rotiert die Ring-Items um die Bubble."""
        if not bubble_group['ring_items']:
            return
        
        center_x = current_x
        center_y = current_y
        radius = bubble_group['radius']
        rotation = bubble_group['rotation_offset']
        
        for i, item in enumerate(bubble_group['ring_items']):
            try:
                # Berechne rotierte Position für jeden Ring
                angle_offset = (i * 0.5) + rotation  # Verschiedene Winkel für verschiedene Ringe
                
                # Für Deadline-Halos: Rotiere um die Bubble
                if 'arc' in str(self.type(item)):
                    # Arc-Items rotieren
                    arc_radius = radius + 15 + (i % 3) * 5  # Verschiedene Radien
                    start_angle = (angle_offset * 57.3) % 360  # Konvertiere zu Grad
                    extent = 30
                    
                    # Berechne neue Arc-Position
                    x1 = center_x - arc_radius
                    y1 = center_y - arc_radius
                    x2 = center_x + arc_radius
                    y2 = center_y + arc_radius
                    
                    self.coords(item, x1, y1, x2, y2)
                    # Arc-Parameter aktualisieren (start und extent)
                    self.itemconfig(item, start=start_angle, extent=extent)
                
                # Für Progress-Ringe: Rotiere um die Bubble
                elif 'arc' in str(self.type(item)) and 'progress' in str(item):
                    ring_radius = radius + 8
                    start_angle = (angle_offset * 57.3) % 360
                    
                    x1 = center_x - ring_radius
                    y1 = center_y - ring_radius
                    x2 = center_x + ring_radius
                    y2 = center_y + ring_radius
                    
                    self.coords(item, x1, y1, x2, y2)
                    self.itemconfig(item, start=start_angle)
                
            except:
                # Falls ein Item nicht mehr existiert, ignorieren
                continue