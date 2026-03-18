# AxonOS/platform/core-services/core_services_init.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Bootstrap helper imported by ALL core services.
#          Ensures DB is initialized before any service runs.
#          Provides get_db() shortcut used across all services.
# ─────────────────────────────────────────────────────────────────

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db_manager import initialize_schema, get_connection, log_event

_initialized = False


def bootstrap() -> None:
    """Call once at platform startup to prepare all core services."""
    global _initialized
    if _initialized:
        return
    initialize_schema()
    log_event("bootstrap", "Core services initialized", "info")
    _initialized = True


def get_db():
    """Shortcut used by all core services to get a DB connection."""
    return get_connection()
