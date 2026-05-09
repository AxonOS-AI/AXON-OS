# AxonOS/platform/core-services/resource-manager/gpu_detector.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Purpose: Automatic GPU detection — works on ANY device.
#          Detects: NVIDIA (CUDA), AMD (ROCm), Intel (oneAPI),
#                   Apple (MPS), or CPU-only.
#          No GPU = NOT an error — it's a supported mode.
# Layer:   Platform / Core Services / Resource Manager
# Depends: None (pure stdlib — optional gpu libs detected at runtime)
# ─────────────────────────────────────────────────────────────────

import os
import sys
import subprocess
import logging
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger("axon.gpu_detector")


# ── GPU Backend Constants ──────────────────────────────────────────

class GPUBackend:
    NVIDIA   = "nvidia"
    AMD      = "amd"
    INTEL    = "intel"
    APPLE    = "apple"
    CPU_ONLY = "cpu_only"


# ── GPU Info Dataclass ────────────────────────────────────────────

@dataclass
class GPUInfo:
    """Complete information about detected GPU(s)."""
    backend:         str   = GPUBackend.CPU_ONLY
    name:            str   = "CPU only"
    vendor:          str   = "none"
    vram_total_gb:   float = 0.0
    vram_used_gb:    float = 0.0
    vram_free_gb:    float = 0.0
    utilization_pct: float = 0.0
    temperature_c:   Optional[float] = None
    cuda_available:  bool  = False
    rocm_available:  bool  = False
    driver_version:  str   = ""
    compute_cap:     str   = ""
    training_device: str   = "cpu"
    count:           int   = 0
    error:           Optional[str] = None

    @property
    def supported(self) -> bool:
        return self.backend != GPUBackend.CPU_ONLY

    @property
    def status_label(self) -> str:
        if self.backend == GPUBackend.NVIDIA:
            return "CUDA"
        elif self.backend == GPUBackend.AMD:
            return "ROCm"
        elif self.backend == GPUBackend.INTEL:
            return "XPU"
        elif self.backend == GPUBackend.APPLE:
            return "MPS"
        return "CPU"

    @property
    def status_color(self) -> str:
        if self.backend == GPUBackend.NVIDIA:
            return "#1D9E75"
        elif self.backend == GPUBackend.AMD:
            return "#EF9F27"
        elif self.backend == GPUBackend.INTEL:
            return "#378ADD"
        elif self.backend == GPUBackend.APPLE:
            return "#8B6FE8"
        return "#E24B4A"


# ── Detector ─────────────────────────────────────────────────────

class GPUDetector:
    """
    Detects available GPU hardware and returns a GPUInfo object.

    Detection order:
      1. NVIDIA  — via pynvml or nvidia-smi
      2. AMD     — via ROCm (rocm-smi or torch.cuda with ROCm)
      3. Intel   — via intel_extension_for_pytorch or xpu-smi
      4. Apple   — via torch.backends.mps (Apple Silicon)
      5. CPU     — fallback, always works
    """

    _cached: Optional[GPUInfo] = None

    @classmethod
    def detect(cls, force: bool = False) -> GPUInfo:
        if cls._cached and not force:
            return cls._cached

        for detector in [
            cls._detect_nvidia,
            cls._detect_amd,
            cls._detect_intel,
            cls._detect_apple,
        ]:
            result = detector()
            if result:
                cls._cached = result
                log.info("GPU detected: %s — %s (backend=%s)",
                         result.name, result.status_label, result.backend)
                return result

        info = GPUInfo(
            backend="cpu_only",
            name="CPU only",
            vendor="none",
            training_device="cpu",
            count=0
        )
        cls._cached = info
        log.info("No GPU detected — running in CPU-only mode (fully supported)")
        return info

    # ── NVIDIA ────────────────────────────────────────────────────

    @classmethod
    def _detect_nvidia(cls) -> Optional[GPUInfo]:
        """Detect NVIDIA GPU via pynvml library or nvidia-smi fallback."""

        # Method 1: pynvml (most detailed)
        try:
            try:
                import pynvml
            except ImportError:
                pynvml = None

            if pynvml is None:
                raise ImportError("pynvml not available")

            pynvml.nvmlInit()
            count = pynvml.nvmlDeviceGetCount()
            if count == 0:
                return None

            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            name   = pynvml.nvmlDeviceGetName(handle)
            name   = name.decode() if isinstance(name, bytes) else name
            mem    = pynvml.nvmlDeviceGetMemoryInfo(handle)
            util   = pynvml.nvmlDeviceGetUtilizationRates(handle)
            driver = pynvml.nvmlSystemGetDriverVersion()
            driver = driver.decode() if isinstance(driver, bytes) else driver

            temp = None
            try:
                temp = float(pynvml.nvmlDeviceGetTemperature(
                    handle, pynvml.NVML_TEMPERATURE_GPU))
            except Exception:
                pass

            compute_cap = ""
            try:
                major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
                compute_cap = f"{major}.{minor}"
            except Exception:
                pass

            return GPUInfo(
                backend         = GPUBackend.NVIDIA,
                name            = name,
                vendor          = "NVIDIA",
                vram_total_gb   = round(mem.total / (1024**3), 2),
                vram_used_gb    = round(mem.used  / (1024**3), 2),
                vram_free_gb    = round(mem.free  / (1024**3), 2),
                utilization_pct = float(util.gpu),
                temperature_c   = temp,
                cuda_available  = True,
                driver_version  = driver,
                compute_cap     = compute_cap,
                training_device = "cuda",
                count           = count,
            )
        except Exception:
            pass

        # Method 2: nvidia-smi fallback
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split(",")
                name   = parts[0].strip() if len(parts) > 0 else "NVIDIA GPU"
                vram   = float(parts[1].strip()) / 1024 if len(parts) > 1 else 0
                driver = parts[2].strip() if len(parts) > 2 else ""
                return GPUInfo(
                    backend         = GPUBackend.NVIDIA,
                    name            = name,
                    vendor          = "NVIDIA",
                    vram_total_gb   = round(vram, 2),
                    cuda_available  = True,
                    driver_version  = driver,
                    training_device = "cuda",
                    count           = 1,
                )
        except Exception:
            pass

        return None

    # ── AMD ───────────────────────────────────────────────────────

    @classmethod
    def _detect_amd(cls) -> Optional[GPUInfo]:
        try:
            result = subprocess.run(
                ["rocm-smi", "--showproductname", "--showmeminfo", "vram",
                 "--showuse", "--csv"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().splitlines()
                name  = "AMD GPU"
                for line in lines:
                    if "Card" in line or "GPU" in line:
                        name = line.split(",")[-1].strip()
                        break
                return GPUInfo(
                    backend         = GPUBackend.AMD,
                    name            = name,
                    vendor          = "AMD",
                    rocm_available  = True,
                    training_device = "cuda",
                    count           = 1,
                )
        except Exception:
            pass

        try:
            import torch
            if torch.cuda.is_available() and "AMD" in torch.cuda.get_device_name(0):
                name = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory
                return GPUInfo(
                    backend         = GPUBackend.AMD,
                    name            = name,
                    vendor          = "AMD",
                    vram_total_gb   = round(vram / (1024**3), 2),
                    rocm_available  = True,
                    training_device = "cuda",
                    count           = torch.cuda.device_count(),
                )
        except Exception:
            pass

        return None

    # ── Intel ─────────────────────────────────────────────────────

    @classmethod
    def _detect_intel(cls) -> Optional[GPUInfo]:
        try:
            import intel_extension_for_pytorch as ipex
            import torch
            if hasattr(torch, 'xpu') and torch.xpu.is_available():
                name = torch.xpu.get_device_name(0)
                return GPUInfo(
                    backend         = GPUBackend.INTEL,
                    name            = name,
                    vendor          = "Intel",
                    training_device = "xpu",
                    count           = torch.xpu.device_count(),
                )
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["xpu-smi", "discovery"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and "Intel" in result.stdout:
                return GPUInfo(
                    backend         = GPUBackend.INTEL,
                    name            = "Intel GPU",
                    vendor          = "Intel",
                    training_device = "xpu",
                    count           = 1,
                )
        except Exception:
            pass

        return None

    # ── Apple Silicon ─────────────────────────────────────────────

    @classmethod
    def _detect_apple(cls) -> Optional[GPUInfo]:
        try:
            import torch
            if torch.backends.mps.is_available():
                import platform
                chip = platform.processor() or "Apple Silicon"
                return GPUInfo(
                    backend         = GPUBackend.APPLE,
                    name            = chip,
                    vendor          = "Apple",
                    training_device = "mps",
                    count           = 1,
                )
        except Exception:
            pass
        return None

    # ── Live update ───────────────────────────────────────────────

    @classmethod
    def update_live(cls) -> Optional[GPUInfo]:
        """Update only live metrics (utilization, VRAM, temp). Safe to call every 2s."""
        if not cls._cached or not cls._cached.supported:
            return cls._cached

        if cls._cached.backend == GPUBackend.NVIDIA:
            try:
                try:
                    import pynvml
                except ImportError:
                    pynvml = None

                if pynvml is None:
                    return cls._cached

                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                util   = pynvml.nvmlDeviceGetUtilizationRates(handle)
                mem    = pynvml.nvmlDeviceGetMemoryInfo(handle)
                cls._cached.utilization_pct = float(util.gpu)
                cls._cached.vram_used_gb    = round(mem.used  / (1024**3), 2)
                cls._cached.vram_free_gb    = round(mem.free  / (1024**3), 2)
                try:
                    cls._cached.temperature_c = float(
                        pynvml.nvmlDeviceGetTemperature(handle, 0))
                except Exception:
                    pass
            except Exception:
                pass

        return cls._cached


# ── Convenience functions ─────────────────────────────────────────

def get_gpu_info(force: bool = False) -> GPUInfo:
    """Shortcut: detect and return GPU info."""
    return GPUDetector.detect(force=force)


def get_training_device() -> str:
    """Returns the best available training device string for PyTorch."""
    return GPUDetector.detect().training_device


# ── CLI test ──────────────────────────────────────────────────────
if __name__ == "__main__":
    print("=== Axon OS GPU Detector ===")
    info = get_gpu_info()
    print(f"Backend:   {info.backend}")
    print(f"Name:      {info.name}")
    print(f"Vendor:    {info.vendor}")
    print(f"Status:    {info.status_label}")
    print(f"Supported: {info.supported}")
    print(f"Device:    {info.training_device}")
    if info.supported:
        print(f"VRAM:      {info.vram_total_gb} GB total / {info.vram_free_gb} GB free")
        print(f"Usage:     {info.utilization_pct:.1f}%")
        if info.temperature_c:
            print(f"Temp:      {info.temperature_c:.0f}°C")
    else:
        print("Mode:      CPU-only training (fully supported)")
