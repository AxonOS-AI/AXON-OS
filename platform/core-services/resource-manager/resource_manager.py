# AxonOS/platform/core-services/resource-manager/resource_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project
# Licensed under AGPL-3.0 (see LICENSE)
#
# PURPOSE: Continuously monitors system resources (CPU, RAM, GPU,
#          disk). Runs as a background thread. Other services
#          call get_snapshot() to read latest values.
#
# DEPENDENCIES: psutil (pip install psutil)
# ─────────────────────────────────────────────────────────────────

import threading
import time
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from config import RESOURCE_POLL_SEC, RESOURCE_HISTORY, LOG_DIR

logging.basicConfig(
    filename=os.path.join(LOG_DIR, "resource.log"),
    level=logging.WARNING,
    format="%(asctime)s [Resource] %(levelname)s %(message)s"
)
log = logging.getLogger("axon.resource")


# ── Data Structures ───────────────────────────────────────────────

@dataclass
class ResourceSnapshot:
    """A single point-in-time reading of all system resources."""
    timestamp:    float = 0.0
    cpu_percent:  float = 0.0       # 0–100
    ram_percent:  float = 0.0       # 0–100
    ram_used_gb:  float = 0.0
    ram_total_gb: float = 0.0
    disk_percent: float = 0.0
    disk_used_gb: float = 0.0
    disk_total_gb: float = 0.0
    gpu_percent:  Optional[float] = None   # None if no GPU detected
    gpu_mem_percent: Optional[float] = None
    gpu_name:     Optional[str] = None


@dataclass
class ResourceHistory:
    """Rolling window of recent snapshots."""
    snapshots: list = field(default_factory=list)
    max_size:  int  = RESOURCE_HISTORY

    def add(self, snapshot: ResourceSnapshot) -> None:
        self.snapshots.append(snapshot)
        if len(self.snapshots) > self.max_size:
            self.snapshots.pop(0)

    def avg_cpu(self) -> float:
        if not self.snapshots:
            return 0.0
        return sum(s.cpu_percent for s in self.snapshots) / len(self.snapshots)

    def avg_ram(self) -> float:
        if not self.snapshots:
            return 0.0
        return sum(s.ram_percent for s in self.snapshots) / len(self.snapshots)


# ── Resource Monitor ──────────────────────────────────────────────

class ResourceManager:
    """
    Background thread that polls system resources.

    Usage:
        rm = ResourceManager()
        rm.start()
        snap = rm.get_snapshot()
        rm.stop()
    """

    def __init__(self):
        self._snapshot = ResourceSnapshot()
        self._history  = ResourceHistory()
        self._lock     = threading.Lock()
        self._running  = False
        self._thread   = None
        self._psutil   = None
        self._gpu_lib  = None
        self._init_libs()

    def _init_libs(self) -> None:
        """Import optional dependencies safely."""
        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            log.warning("psutil not installed — using fallback values. Run: pip install psutil")

        try:
            import pynvml
            pynvml.nvmlInit()
            self._gpu_lib = pynvml
            self._gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            self._gpu_name = pynvml.nvmlDeviceGetName(self._gpu_handle)
            if isinstance(self._gpu_name, bytes):
                self._gpu_name = self._gpu_name.decode()
        except Exception:
            self._gpu_lib = None
            self._gpu_name = None

    def _read(self) -> ResourceSnapshot:
        """Read current system stats and return a snapshot."""
        snap = ResourceSnapshot(timestamp=time.time())

        if self._psutil:
            p = self._psutil
            snap.cpu_percent  = p.cpu_percent(interval=None)
            vm = p.virtual_memory()
            snap.ram_percent  = vm.percent
            snap.ram_used_gb  = round(vm.used  / (1024 ** 3), 2)
            snap.ram_total_gb = round(vm.total / (1024 ** 3), 2)
            disk = p.disk_usage("/")
            snap.disk_percent  = disk.percent
            snap.disk_used_gb  = round(disk.used  / (1024 ** 3), 2)
            snap.disk_total_gb = round(disk.total / (1024 ** 3), 2)
        else:
            # Fallback: read from /proc directly (Linux only)
            try:
                with open("/proc/loadavg") as f:
                    snap.cpu_percent = float(f.read().split()[0]) * 10
                with open("/proc/meminfo") as f:
                    lines = {l.split(":")[0]: int(l.split()[1])
                             for l in f.readlines() if ":" in l}
                total = lines.get("MemTotal", 1)
                avail = lines.get("MemAvailable", total)
                snap.ram_total_gb = round(total / (1024 ** 2), 2)
                snap.ram_used_gb  = round((total - avail) / (1024 ** 2), 2)
                snap.ram_percent  = round((1 - avail / total) * 100, 1)
            except Exception:
                pass

        if self._gpu_lib:
            try:
                util  = self._gpu_lib.nvmlDeviceGetUtilizationRates(self._gpu_handle)
                mem   = self._gpu_lib.nvmlDeviceGetMemoryInfo(self._gpu_handle)
                snap.gpu_percent     = float(util.gpu)
                snap.gpu_mem_percent = round(mem.used / mem.total * 100, 1)
                snap.gpu_name        = self._gpu_name
            except Exception:
                pass

        return snap

    def _loop(self) -> None:
        while self._running:
            snap = self._read()
            with self._lock:
                self._snapshot = snap
                self._history.add(snap)
            time.sleep(RESOURCE_POLL_SEC)

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread  = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        log.info("Resource monitor started")

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        log.info("Resource monitor stopped")

    def get_snapshot(self) -> ResourceSnapshot:
        """Thread-safe — returns the latest resource snapshot."""
        with self._lock:
            return self._snapshot

    def get_history(self) -> ResourceHistory:
        """Thread-safe — returns the rolling history."""
        with self._lock:
            return self._history

    def summary(self) -> str:
        s = self.get_snapshot()
        lines = [
            f"CPU:  {s.cpu_percent:.1f}%",
            f"RAM:  {s.ram_percent:.1f}%  ({s.ram_used_gb}/{s.ram_total_gb} GB)",
            f"Disk: {s.disk_percent:.1f}%  ({s.disk_used_gb}/{s.disk_total_gb} GB)",
        ]
        if s.gpu_percent is not None:
            lines.append(f"GPU:  {s.gpu_percent:.1f}%  ({s.gpu_name})")
        return "\n".join(lines)


# ── CLI Test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    rm = ResourceManager()
    rm.start()
    time.sleep(3)
    print(rm.summary())
    rm.stop()
