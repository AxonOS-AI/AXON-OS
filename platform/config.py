# AxonOS/platform/config.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Shared configuration constants for the entire Platform Layer.
#          All visual settings deferred to last phase — these are
#          functional/structural values only.
# ─────────────────────────────────────────────────────────────────

import os

# ── Identity ──────────────────────────────────────────────────────
AXON_NAME        = "Axon OS"
AXON_VERSION     = "1.0.0"
AXON_CODENAME    = "Spark"
AXON_AUTHOR      = "Abdullah"

# ── Paths (relative to project root) ──────────────────────────────
ROOT_DIR         = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLATFORM_DIR     = os.path.join(ROOT_DIR, "platform")
AI_CONTAINER_DIR = os.path.join(ROOT_DIR, "ai-container")
SCRIPTS_DIR      = os.path.join(ROOT_DIR, "scripts")
DATA_DIR         = os.path.expanduser("~/.axonos")
DB_PATH          = os.path.join(DATA_DIR, "axonos.db")
LOG_DIR          = os.path.join(DATA_DIR, "logs")
PROJECTS_DIR     = os.path.expanduser("~/AxonProjects")

# ── Taskbar ───────────────────────────────────────────────────────
TASKBAR_HEIGHT   = 40        # px — visual deferred, structure needed now
TASKBAR_POSITION = "top"     # "top" | "bottom"

# ── Update ────────────────────────────────────────────────────────
UPDATE_CHECK_URL  = "https://api.github.com/repos/[your-username]/axon-os/releases/latest"
UPDATE_INTERVAL_H = 24       # hours between auto-checks

# ── Resource Monitor ──────────────────────────────────────────────
RESOURCE_POLL_SEC = 2        # seconds between resource readings
RESOURCE_HISTORY  = 60       # how many readings to keep in history

# ── Project Manager ───────────────────────────────────────────────
MAX_RECENT_PROJECTS = 10

# ── Desktop ───────────────────────────────────────────────────────
DEFAULT_WORKSPACE_COUNT = 4

# ── Ensure data dirs exist at import time ─────────────────────────
os.makedirs(DATA_DIR,     exist_ok=True)
os.makedirs(LOG_DIR,      exist_ok=True)
os.makedirs(PROJECTS_DIR, exist_ok=True)
