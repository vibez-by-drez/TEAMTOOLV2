# -*- coding: utf-8 -*-
"""
Backend-Logik für das Coworking Tool, einschließlich Datenmodell und Google Sheets Synchronisation.
"""

import os
import threading
import json
from uuid import uuid4
from tkinter import messagebox

# Abhängigkeiten von Drittanbietern
try:
    import gspread
except ImportError:
    gspread = None

# Lokale Importe
from utils import now_iso

def ensure_gspread():
    """Stellt sicher, dass gspread installiert ist."""
    if gspread is None:
        messagebox.showerror("Fehlende Abhängigkeit", "Bitte installiere gspread:\n\npip install gspread")
        raise RuntimeError("gspread not installed")

class SheetsBackend:
    """
    Verwaltet die Verbindung und die Operationen mit Google Sheets.
    """
    def __init__(self, config):
        self.config = config
        self.gc = None
        self.sh = None
        self.ws_projects = None
        self.ws_tasks = None
        self.lock = threading.Lock()

    def connect(self):
        """Stellt die Verbindung zum Google Sheet her."""
        ensure_gspread()
        path = self.config.get("service_account_json") or ""
        if not path or not os.path.exists(path):
            raise FileNotFoundError("Service-Account JSON nicht gefunden. Bitte in den Einstellungen setzen.")
        self.gc = gspread.service_account(filename=path)
        sheet_id = self.config.get("sheet_id") or ""
        if not sheet_id:
            raise ValueError("Sheet-ID fehlt. Bitte in den Einstellungen setzen.")
        self.sh = self.gc.open_by_key(sheet_id)
        # Sicherstellen, dass die Arbeitsblätter existieren
        self.ws_projects = self._ensure_ws("Projects", ["project_id", "name", "color", "deadline", "last_update"])
        self.ws_tasks    = self._ensure_ws("Tasks",    ["task_id", "project_id", "name", "goal", "description",
                                                        "attention", "assignee", "checklist_json", "last_update"])

    def _ensure_ws(self, title, headers):
        """Stellt sicher, dass ein Arbeitsblatt mit den korrekten Headern existiert."""
        try:
            ws = self.sh.worksheet(title)
        except gspread.exceptions.WorksheetNotFound:
            ws = self.sh.add_worksheet(title=title, rows=1000, cols=len(headers))
            ws.append_row(headers)
        # Header überprüfen
        first_row = ws.row_values(1)
        if first_row != headers:
            ws.clear()
            ws.append_row(headers)
        return ws

    def fetch_projects(self):
        """Holt alle Projekte aus dem Sheet."""
        with self.lock:
            rows = self.ws_projects.get_all_records()
        # Erforderliche Felder normalisieren
        for r in rows:
            r.setdefault("project_id", "")
            r.setdefault("name", "")
            r.setdefault("color", "")
            r.setdefault("deadline", "")
            r.setdefault("last_update", "")
        return rows

    def fetch_tasks(self):
        """Holt alle Tasks aus dem Sheet."""
        with self.lock:
            rows = self.ws_tasks.get_all_records()
        for r in rows:
            r.setdefault("task_id", "")
            r.setdefault("project_id", "")
            r.setdefault("name", "")
            r.setdefault("goal", "")
            r.setdefault("description", "")
            r.setdefault("attention", "")
            
            # Handle assignee field - convert comma-separated string to list
            assignee_data = r.get("assignee", "")
            if assignee_data:
                # Split by comma and strip whitespace
                assignee_list = [name.strip() for name in assignee_data.split(",") if name.strip()]
                r["assignee"] = assignee_list
            else:
                r["assignee"] = []
            
            r.setdefault("checklist_json", "[]")
            r.setdefault("last_update", "")
        return rows

    def upsert_project(self, project):
        """Fügt ein Projekt hinzu oder aktualisiert es."""
        with self.lock:
            all_rows = self.ws_projects.get_all_records()
            # Zeile finden
            row_idx = None
            for i, r in enumerate(all_rows, start=2):
                if r.get("project_id") == project["project_id"]:
                    row_idx = i
                    break
            vals = [
                project.get("project_id", ""),
                project.get("name", ""),
                project.get("color", ""),
                project.get("deadline", ""),
                project.get("last_update", now_iso())
            ]
            if row_idx:
                self.ws_projects.update(f"A{row_idx}:E{row_idx}", [vals])
            else:
                self.ws_projects.append_row(vals)

    def delete_project(self, project_id):
        """Löscht ein Projekt und die zugehörigen Tasks."""
        with self.lock:
            # Projektzeile löschen
            all_rows = self.ws_projects.get_all_records()
            for i, r in enumerate(all_rows, start=2):
                if r.get("project_id") == project_id:
                    self.ws_projects.delete_rows(i)
                    break
            # Zugehörige Tasks löschen
            tasks = self.ws_tasks.get_all_records()
            to_delete = []
            for i, r in enumerate(tasks, start=2):
                if r.get("project_id") == project_id:
                    to_delete.append(i)
            for idx in reversed(to_delete):
                self.ws_tasks.delete_rows(idx)

    def upsert_task(self, task):
        """Fügt einen Task hinzu oder aktualisiert ihn."""
        with self.lock:
            all_rows = self.ws_tasks.get_all_records()
            row_idx = None
            for i, r in enumerate(all_rows, start=2):
                if r.get("task_id") == task["task_id"]:
                    row_idx = i
                    break
            # Handle assignee as either string or list - save as comma-separated string
            assignee_data = task.get("assignee", "")
            if isinstance(assignee_data, list):
                # Join multiple assignees with comma and space
                assignee_str = ", ".join(assignee_data) if assignee_data else ""
            else:
                assignee_str = str(assignee_data) if assignee_data else ""
            
            vals = [
                task.get("task_id", ""),
                task.get("project_id", ""),
                task.get("name", ""),
                task.get("goal", ""),
                task.get("description", ""),
                task.get("attention", ""),
                assignee_str,
                task.get("checklist_json", "[]"),
                task.get("last_update", now_iso())
            ]
            if row_idx:
                self.ws_tasks.update(values=[vals], range_name=f"A{row_idx}:I{row_idx}")
            else:
                self.ws_tasks.append_row(vals)

    def delete_task(self, task_id):
        """Löscht einen Task."""
        with self.lock:
            all_rows = self.ws_tasks.get_all_records()
            for i, r in enumerate(all_rows, start=2):
                if r.get("task_id") == task_id:
                    self.ws_tasks.delete_rows(i)
                    break

class Model:
    """
    Verwaltet den In-Memory-Datenzustand und die Synchronisation mit dem Backend.
    """
    def __init__(self, backend):
        self.backend = backend
        self.projects = {}  # project_id -> dict
        self.tasks = {}     # task_id -> dict
        self.tasks_by_project = {}  # project_id -> set(task_ids)

    def load_all(self):
        """Lädt alle Daten aus dem Backend."""
        self.projects.clear()
        self.tasks.clear()
        self.tasks_by_project.clear()
        for p in self.backend.fetch_projects():
            pid = p.get("project_id") or str(uuid4())
            p["project_id"] = pid
            p.setdefault("deadline", "")
            self.projects[pid] = p
            self.tasks_by_project.setdefault(pid, set())
        for t in self.backend.fetch_tasks():
            tid = t.get("task_id") or str(uuid4())
            t["task_id"] = tid
            self.tasks[tid] = t
            self.tasks_by_project.setdefault(t["project_id"], set()).add(tid)

    def get_projects_list(self):
        """Gibt eine Liste aller Projekte zurück."""
        return list(self.projects.values())

    def get_tasks_for_project(self, project_id):
        """Gibt eine Liste aller Tasks für ein bestimmtes Projekt zurück."""
        ids = self.tasks_by_project.get(project_id, set())
        return [self.tasks[i] for i in ids]

    def new_project(self, name, color="#222222", deadline=""):
        """Erstellt ein neues Projekt."""
        pid = str(uuid4())
        p = {
            "project_id": pid,
            "name": name,
            "color": color or "#222222",
            "deadline": deadline or "",
            "last_update": now_iso()
        }
        self.projects[pid] = p
        self.tasks_by_project[pid] = set()
        self.backend.upsert_project(p)
        return p

    def delete_project(self, project_id):
        """Löscht ein Projekt und seine Tasks."""
        if project_id in self.projects:
            # Im Speicher entfernen
            for tid in list(self.tasks_by_project.get(project_id, set())):
                self.tasks.pop(tid, None)
            self.tasks_by_project.pop(project_id, None)
            self.projects.pop(project_id, None)
            # Im Backend löschen
            self.backend.delete_project(project_id)

    def new_task(self, project_id, name="Neuer Task"):
        """Erstellt einen neuen Task."""
        tid = str(uuid4())
        t = {
            "task_id": tid,
            "project_id": project_id,
            "name": name,
            "goal": "",
            "description": "",
            "attention": "",
            "assignee": [],
            "checklist_json": "[]",
            "last_update": now_iso()
        }
        self.tasks[tid] = t
        self.tasks_by_project.setdefault(project_id, set()).add(tid)
        self.backend.upsert_task(t)
        return t

    def save_task(self, task):
        """Speichert einen Task."""
        task["last_update"] = now_iso()
        self.backend.upsert_task(task)

    def delete_task(self, task_id):
        """Löscht einen Task."""
        task = self.tasks.get(task_id)
        if not task:
            return
        pid = task["project_id"]
        self.tasks.pop(task_id, None)
        if pid in self.tasks_by_project:
            self.tasks_by_project[pid].discard(task_id)
        self.backend.delete_task(task_id)

    def merge_remote(self):
        """Holt Remote-Änderungen und führt sie nach dem 'Last-Write-Wins'-Prinzip zusammen."""
        remote_projects = {p["project_id"]: p for p in self.backend.fetch_projects()}
        remote_tasks = {t["task_id"]: t for t in self.backend.fetch_tasks()}

        # Projekte zusammenführen
        for pid, r in remote_projects.items():
            l = self.projects.get(pid)
            if not l or (r.get("last_update", "") or "") > (l.get("last_update", "") or ""):
                self.projects[pid] = r
                self.tasks_by_project.setdefault(pid, set())

        # Tasks zusammenführen
        for tid, r in remote_tasks.items():
            l = self.tasks.get(tid)
            if not l or (r.get("last_update", "") or "") > (l.get("last_update", "") or ""):
                self.tasks[tid] = r
                self.tasks_by_project.setdefault(r["project_id"], set()).add(tid)

        # tasks_by_project neu aufbauen, um Konsistenz zu gewährleisten
        tbp = {}
        for t in self.tasks.values():
            tbp.setdefault(t["project_id"], set()).add(t["task_id"])
        self.tasks_by_project = tbp