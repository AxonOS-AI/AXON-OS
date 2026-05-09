# AxonOS/platform/core-services/resource-manager/resource_manager.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# PURPOSE: Continuously monitors CPU, RAM, GPU, Disk.
#          All public methods traced — call stack captured on error.
# ─────────────────────────────────────────────────────────────────

import threading
import time
import os
import sys
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tracer import trace, TraceContext, PlatformError, log_error, _logger as log
from config import RESOURCE_POLL_SEC, RESOURCE_HISTORY, LOG_DIR


@dataclass
class ResourceSnapshot:
    timestamp:       float = 0.0
    cpu_percent:     float = 0.0
    ram_percent:     float = 0.0
    ram_used_gb:     float = 0.0
    ram_total_gb:    float = 0.0
    disk_percent:    float = 0.0
    disk_used_gb:    float = 0.0
    disk_total_gb:   float = 0.0
    gpu_percent:     Optional[float] = None
    gpu_mem_percent: Optional[float] = None
    gpu_name:        Optional[str]   = None


@dataclass
class ResourceHistory:
    snapshots: list = field(default_factory=list)
    max_size:  int  = RESOURCE_HISTORY

    def add(self, s: ResourceSnapshot) -> None:
        self.snapshots.append(s)
        if len(self.snapshots) > self.max_size:
            self.snapshots.pop(0)

    def avg_cpu(self) -> float:
        return sum(s.cpu_percent for s in self.snapshots) / max(1, len(self.snapshots))

    def avg_ram(self) -> float:
        return sum(s.ram_percent for s in self.snapshots) / max(1, len(self.snapshots))


class ResourceManager:
    """Background thread resource monitor. All methods stack-traced."""

    def __init__(self):
        self._snapshot  = ResourceSnapshot()
        self._history   = ResourceHistory()
        self._lock      = threading.Lock()
        self._running   = False
        self._thread    = None
        self._psutil    = None
        self._gpu_lib   = None
        self._gpu_handle = None
        self._gpu_name  = None
        self._init_libs()

    @trace(layer="platform")
    def _init_libs(self) -> None:
        try:
            import psutil
            self._psutil = psutil
        except ImportError:
            log.warning("psutil not installed — using /proc fallback")

        # Auto-detect GPU — NVIDIA / AMD / Intel / Apple / CPU-only
        try:
            from gpu_detector import GPUDetector
            self._gpu_info    = GPUDetector.detect()
            self._gpu_backend = GPUDetector
            self._gpu_lib     = self._gpu_info.supported
            self._gpu_name    = self._gpu_info.name
            log.info("GPU: %s (%s) device: %s",
                     self._gpu_info.name,
                     self._gpu_info.status_label,
                     self._gpu_info.training_device)
        except Exception as e:
            log.warning("GPU detection: %s — CPU-only mode", e)
            self._gpu_info    = None
            self._gpu_backend = None
            self._gpu_lib     = False

    def _read(self) -> ResourceSnapshot:
        """Read current system stats. Exceptions logged but not raised."""
        snap = ResourceSnapshot(timestamp=time.time())
        try:
            if self._psutil:
                p = self._psutil
                snap.cpu_percent  = p.cpu_percent(interval=None)
                vm = p.virtual_memory()
                snap.ram_percent  = vm.percent
                snap.ram_used_gb  = round(vm.used  / (1024**3), 2)
                snap.ram_total_gb = round(vm.total / (1024**3), 2)
                disk = p.disk_usage("/")
                snap.disk_percent  = disk.percent
                snap.disk_used_gb  = round(disk.used  / (1024**3), 2)
                snap.disk_total_gb = round(disk.total / (1024**3), 2)
            else:
                with open("/proc/meminfo") as f:
                    lines = {l.split(":")[0]: int(l.split()[1])
                             for l in f.readlines() if ":" in l}
                total = lines.get("MemTotal", 1)
                avail = lines.get("MemAvailable", total)
                snap.ram_total_gb = round(total / (1024**2), 2)
                snap.ram_used_gb  = round((total - avail) / (1024**2), 2)
                snap.ram_percent  = round((1 - avail / total) * 100, 1)
        except Exception as e:
            log_error(e, "resource_manager._read", context={"phase": "cpu/ram"})

        if self._gpu_lib and self._gpu_backend:
            try:
                info = self._gpu_backend.update_live()
                if info and info.supported:
                    snap.gpu_percent     = info.utilization_pct
                    snap.gpu_mem_percent = round(
                        info.vram_used_gb / max(0.1, info.vram_total_gb) * 100, 1)
                    snap.gpu_name        = info.name
            except Exception as e:
                log_error(e, "resource_manager._read", context={"phase": "gpu"})
        return snap

    def _loop(self) -> None:
        while self._running:
            try:
                snap = self._read()
                with self._lock:
                    self._snapshot = snap
                    self._history.add(snap)
            except Exception as e:
                log_error(e, "resource_manager._loop")
            time.sleep(RESOURCE_POLL_SEC)

    @trace(layer="platform")
    def start(self) -> None:
        if self._running:
            return
        with TraceContext("resource_manager.start", layer="platform"):
            self._running = True
            self._thread  = threading.Thread(target=self._loop, daemon=True,
                                             name="AxonResourceMonitor")
            self._thread.start()
            log.info("Resource monitor started")

    @trace(layer="platform")
    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        log.info("Resource monitor stopped")

    def get_snapshot(self) -> ResourceSnapshot:
        with self._lock:
            return self._snapshot

    def get_history(self) -> ResourceHistory:
        with self._lock:
            return self._history

    def get_gpu_info(self):
        """Return full GPUInfo object for UI display."""
        return self._gpu_info

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


if __name__ == "__main__":
    rm = ResourceManager()
    rm.start()
    time.sleep(3)
    print(rm.summary())
    rm.stop()
