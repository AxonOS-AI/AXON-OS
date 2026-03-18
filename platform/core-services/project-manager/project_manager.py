# AxonOS/platform/core-services/project-manager/project_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Manages Axon OS development projects.
#          Stores metadata in SQLite (db_manager).
#          Creates and manages project folders on disk.
#
# OPERATIONS: create, list, get, update, delete, archive
# ─────────────────────────────────────────────────────────────────

import os
import sys
import json
import shutil
import logging
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import PROJECTS_DIR, LOG_DIR, MAX_RECENT_PROJECTS
from core_services_init import get_db   # shared helper (see below)

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "projects.log"),
    level=logging.INFO,
    format="%(asctime)s [ProjectMgr] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.project_manager")


class ProjectManager:
    """
    CRUD interface for Axon OS projects.

    Each project is:
      - A record in the SQLite `projects` table
      - A folder on disk at ~/AxonProjects/<name>/
      - A .axon_project.json file inside that folder
    """

    # ── Create ────────────────────────────────────────────────────
    def create(self, name: str, description: str = "",
               tags: str = "") -> dict:
        """
        Create a new project.
        Returns the project dict or raises ValueError if name taken.
        """
        name = name.strip()
        if not name:
            raise ValueError("Project name cannot be empty")

        project_path = os.path.join(PROJECTS_DIR, name)

        conn = get_db()
        existing = conn.execute(
            "SELECT id FROM projects WHERE name = ?", (name,)
        ).fetchone()

        if existing:
            conn.close()
            raise ValueError(f"Project '{name}' already exists")

        # Create folder + metadata file
        os.makedirs(project_path, exist_ok=True)
        meta = {
            "name": name,
            "description": description,
            "axon_version": "1.0.0",
            "tags": tags
        }
        with open(os.path.join(project_path, ".axon_project.json"), "w") as f:
            json.dump(meta, f, indent=2)

        # Insert DB record
        cursor = conn.execute(
            """INSERT INTO projects (name, description, path, tags)
               VALUES (?, ?, ?, ?)""",
            (name, description, project_path, tags)
        )
        conn.commit()
        project_id = cursor.lastrowid
        conn.close()

        log.info("Created project: %s (id=%s)", name, project_id)
        return self.get(project_id)

    # ── List ──────────────────────────────────────────────────────
    def list_all(self, status: str = "active") -> list[dict]:
        """Return all projects with given status as list of dicts."""
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM projects WHERE status = ? ORDER BY updated_at DESC",
            (status,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def list_recent(self) -> list[dict]:
        """Return the most recently updated projects."""
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM projects ORDER BY updated_at DESC LIMIT ?",
            (MAX_RECENT_PROJECTS,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ── Get ───────────────────────────────────────────────────────
    def get(self, project_id: int) -> Optional[dict]:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM projects WHERE id = ?", (project_id,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    def get_by_name(self, name: str) -> Optional[dict]:
        conn = get_db()
        row = conn.execute(
            "SELECT * FROM projects WHERE name = ?", (name,)
        ).fetchone()
        conn.close()
        return dict(row) if row else None

    # ── Update ────────────────────────────────────────────────────
    def update(self, project_id: int, **kwargs) -> Optional[dict]:
        """
        Update project fields. Allowed: description, tags, status.
        """
        allowed = {"description", "tags", "status"}
        fields  = {k: v for k, v in kwargs.items() if k in allowed}
        if not fields:
            return self.get(project_id)

        set_clause = ", ".join(f"{k} = ?" for k in fields)
        set_clause += ", updated_at = datetime('now')"
        values     = list(fields.values()) + [project_id]

        conn = get_db()
        conn.execute(
            f"UPDATE projects SET {set_clause} WHERE id = ?", values
        )
        conn.commit()
        conn.close()
        log.info("Updated project id=%s: %s", project_id, fields)
        return self.get(project_id)

    # ── Delete ────────────────────────────────────────────────────
    def delete(self, project_id: int, delete_files: bool = False) -> bool:
        """
        Remove project from DB. Optionally delete disk folder.
        """
        project = self.get(project_id)
        if not project:
            return False

        conn = get_db()
        conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()

        if delete_files and os.path.isdir(project["path"]):
            shutil.rmtree(project["path"])
            log.info("Deleted files for project: %s", project["name"])

        log.info("Deleted project record: %s", project["name"])
        return True

    # ── Archive ───────────────────────────────────────────────────
    def archive(self, project_id: int) -> Optional[dict]:
        """Mark project as archived (soft delete)."""
        return self.update(project_id, status="archived")

    # ── Tasks ─────────────────────────────────────────────────────
    def add_task(self, project_id: int, title: str,
                 priority: str = "normal") -> dict:
        conn = get_db()
        cursor = conn.execute(
            "INSERT INTO tasks (project_id, title, priority) VALUES (?, ?, ?)",
            (project_id, title, priority)
        )
        conn.commit()
        task_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        conn.close()
        return dict(row)

    def list_tasks(self, project_id: int) -> list[dict]:
        conn = get_db()
        rows = conn.execute(
            "SELECT * FROM tasks WHERE project_id = ? ORDER BY created_at",
            (project_id,)
        ).fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def complete_task(self, task_id: int) -> bool:
        conn = get_db()
        conn.execute(
            "UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?",
            (task_id,)
        )
        conn.commit()
        conn.close()
        return True


# ── CLI Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from db_manager import initialize_schema
    initialize_schema()

    pm = ProjectManager()

    # Create a test project
    try:
        p = pm.create("TestProject", description="A test Axon project", tags="test,demo")
        print(f"✓ Created: {p['name']} (id={p['id']})")
    except ValueError as e:
        print(f"  Already exists: {e}")
        p = pm.get_by_name("TestProject")

    # List
    projects = pm.list_all()
    print(f"✓ Total projects: {len(projects)}")

    # Add task
    task = pm.add_task(p["id"], "Build the desktop GUI", priority="high")
    print(f"✓ Task added: {task['title']}")
