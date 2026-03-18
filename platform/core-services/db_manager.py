# AxonOS/platform/core-services/db_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Central SQLite database manager for all Core Services.
#          Handles: projects, tasks, system events, update history.
#          All services share one DB file at ~/.axonos/axonos.db
# ─────────────────────────────────────────────────────────────────

import sqlite3
import logging
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DB_PATH, LOG_DIR

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "db.log"),
    level=logging.INFO,
    format="%(asctime)s [DB] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.db")


def get_connection() -> sqlite3.Connection:
    """Return a thread-safe SQLite connection with row factory."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def initialize_schema() -> None:
    """
    Create all tables if they do not exist.
    Safe to call on every startup — idempotent.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # ── Projects ──────────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL UNIQUE,
            description TEXT    DEFAULT '',
            path        TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now')),
            updated_at  TEXT    DEFAULT (datetime('now')),
            status      TEXT    DEFAULT 'active',
            tags        TEXT    DEFAULT ''
        )
    """)

    # ── Tasks (belong to a project) ───────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id  INTEGER NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
            title       TEXT    NOT NULL,
            status      TEXT    DEFAULT 'pending',
            priority    TEXT    DEFAULT 'normal',
            created_at  TEXT    DEFAULT (datetime('now')),
            updated_at  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── System Events (audit log) ─────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_events (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            level      TEXT    DEFAULT 'info',
            timestamp  TEXT    DEFAULT (datetime('now'))
        )
    """)

    # ── Update History ────────────────────────────────────────────
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS update_history (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            version      TEXT    NOT NULL,
            applied_at   TEXT    DEFAULT (datetime('now')),
            status       TEXT    DEFAULT 'success',
            notes        TEXT    DEFAULT ''
        )
    """)

    conn.commit()
    conn.close()
    log.info("Schema initialized at %s", DB_PATH)


def log_event(event_type: str, message: str, level: str = "info") -> None:
    """Write a system event to the audit log table."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO system_events (event_type, message, level) VALUES (?, ?, ?)",
        (event_type, message, level)
    )
    conn.commit()
    conn.close()


if __name__ == "__main__":
    initialize_schema()
    log_event("startup", "Database initialized", "info")
    print(f"✓ Database ready at: {DB_PATH}")
