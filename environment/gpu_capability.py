import os
import sys
import shutil
import subprocess
import warnings


class GPUCapability:
    def run_check(self, virtualization_result=None):
        virtualization_result = virtualization_result or {}

        lspci_result = self._run_command(
            ["lspci"]
        )

        lspci_text = (
            lspci_result.get("stdout", "")
            + "\n"
            + lspci_result.get("stderr", "")
        )

        gpu_devices = self._extract_gpu_devices(
            lspci_text
        )

        vendor = self._detect_vendor(
            gpu_devices=gpu_devices,
            lspci_text=lspci_text
        )

        virtual_gpu_detected = self._detect_virtual_gpu(
            gpu_devices=gpu_devices,
            lspci_text=lspci_text
        )

        nvidia_smi_path = shutil.which("nvidia-smi")
        rocm_smi_path = shutil.which("rocm-smi")

        torch_status = self._check_torch_cuda()

        virtualization_detected = virtualization_result.get(
            "virtualization_detected",
            False
        )

        virtualization_type = virtualization_result.get(
            "virtualization_type",
            "unknown"
        )

        passthrough_status = self._infer_passthrough_status(
            virtualization_detected=virtualization_detected,
            vendor=vendor,
            virtual_gpu_detected=virtual_gpu_detected,
            gpu_devices=gpu_devices
        )

        recommended_backend = self._recommend_backend(
            virtualization_detected=virtualization_detected,
            virtualization_type=virtualization_type,
            vendor=vendor,
            virtual_gpu_detected=virtual_gpu_detected,
            passthrough_status=passthrough_status,
            torch_status=torch_status,
            nvidia_smi_path=nvidia_smi_path,
            rocm_smi_path=rocm_smi_path
        )

        return {
            "status": "completed",
            "report_type": "gpu_capability",
            "virtualization": {
                "virtualization_detected": virtualization_detected,
                "virtualization_type": virtualization_type
            },
            "gpu": {
                "guest_gpu_visible": len(gpu_devices) > 0,
                "gpu_vendor": vendor,
                "gpu_devices": gpu_devices,
                "virtual_gpu_detected": virtual_gpu_detected,
                "gpu_passthrough_status": passthrough_status
            },
            "tools": {
                "nvidia_smi_available": nvidia_smi_path is not None,
                "nvidia_smi_path": nvidia_smi_path,
                "rocm_smi_available": rocm_smi_path is not None,
                "rocm_smi_path": rocm_smi_path
            },
            "torch": torch_status,
            "recommendation": recommended_backend,
            "policy": {
                "auto_install_gpu_drivers": False,
                "auto_install_nvidia_drivers": False,
                "auto_install_rocm": False,
                "auto_install_bitsandbytes": False,
                "allow_optional_gpu_packages": recommended_backend.get(
                    "allow_optional_gpu_packages",
                    False
                ),
                "reason": recommended_backend.get("reason")
            }
        }

    def save_check_report(self, project_path, virtualization_result=None):
        result = self.run_check(
            virtualization_result=virtualization_result
        )

        reports_dir = os.path.join(
            project_path,
            "reports"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        report_file = os.path.join(
            reports_dir,
            "gpu_capability.json"
        )

        import json

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        result["generated_files"] = {
            "gpu_capability": report_file
        }

        return result

    def _extract_gpu_devices(self, lspci_text):
        devices = []

        for line in lspci_text.splitlines():
            lower = line.lower()

            if (
                "vga compatible controller" in lower
                or "3d controller" in lower
                or "display controller" in lower
            ):
                devices.append(line.strip())

        return devices

    def _detect_vendor(self, gpu_devices, lspci_text):
        text = "\n".join(gpu_devices).lower() or lspci_text.lower()

        virtual_markers = [
            "vmware",
            "virtualbox",
            "vbox",
            "qxl",
            "virtio",
            "hyper-v",
            "microsoft basic render"
        ]

        if any(marker in text for marker in virtual_markers):
            return "virtual"

        if "nvidia" in text:
            return "nvidia"

        amd_markers = [
            "advanced micro devices",
            "amd/ati",
            "amd ati",
            "radeon",
            "[amd/ati]"
        ]

        if any(marker in text for marker in amd_markers):
            return "amd"

        if "intel corporation" in text or "intel" in text:
            return "intel"

        if gpu_devices:
            return "unknown"

        return "none"

    def _detect_virtual_gpu(self, gpu_devices, lspci_text):
        text = "\n".join(gpu_devices).lower() or lspci_text.lower()

        markers = [
            "vmware",
            "virtualbox",
            "vbox",
            "qxl",
            "virtio",
            "microsoft basic render",
            "hyper-v"
        ]

        return any(marker in text for marker in markers)

    def _infer_passthrough_status(
        self,
        virtualization_detected,
        vendor,
        virtual_gpu_detected,
        gpu_devices
    ):
        if not virtualization_detected:
            return "not_applicable_bare_metal_or_unknown"

        if not gpu_devices:
            return "not_detected"

        if virtual_gpu_detected:
            return "not_detected_virtual_gpu_only"

        if vendor in ["nvidia", "amd", "intel"]:
            return "possible_real_gpu_visible_to_guest"

        return "unknown"

    def _recommend_backend(
        self,
        virtualization_detected,
        virtualization_type,
        vendor,
        virtual_gpu_detected,
        passthrough_status,
        torch_status,
        nvidia_smi_path,
        rocm_smi_path
    ):
        if virtualization_detected and passthrough_status not in [
            "possible_real_gpu_visible_to_guest"
        ]:
            return {
                "recommended_backend": "cpu",
                "execution_mode": "vm_safe_cpu",
                "allow_optional_gpu_packages": False,
                "gpu_acceleration_ready": False,
                "reason": (
                    "AXON is running inside a virtualized environment "
                    f"({virtualization_type}) without confirmed real GPU passthrough. "
                    "GPU drivers, ROCm, NVIDIA drivers, and bitsandbytes must not "
                    "be installed automatically."
                )
            }

        if vendor == "nvidia":
            cuda_available = torch_status.get("cuda_available")

            if cuda_available and nvidia_smi_path:
                return {
                    "recommended_backend": "cuda",
                    "execution_mode": "gpu_cuda",
                    "allow_optional_gpu_packages": True,
                    "gpu_acceleration_ready": True,
                    "reason": (
                        "NVIDIA GPU appears available with CUDA. Optional CUDA "
                        "packages may be planned after explicit user approval."
                    )
                }

            return {
                "recommended_backend": "cpu",
                "execution_mode": "gpu_not_ready",
                "allow_optional_gpu_packages": False,
                "gpu_acceleration_ready": False,
                "reason": (
                    "NVIDIA GPU was detected, but CUDA readiness was not confirmed. "
                    "AXON should not install GPU packages automatically."
                )
            }

        if vendor == "amd":
            return {
                "recommended_backend": "cpu_or_amd_check_required",
                "execution_mode": "amd_check_required",
                "allow_optional_gpu_packages": False,
                "gpu_acceleration_ready": False,
                "reason": (
                    "AMD GPU was detected. ROCm/Vulkan compatibility must be checked "
                    "against supported hardware and environment before enabling GPU acceleration."
                )
            }

        if vendor == "intel":
            return {
                "recommended_backend": "cpu_or_intel_check_required",
                "execution_mode": "intel_check_required",
                "allow_optional_gpu_packages": False,
                "gpu_acceleration_ready": False,
                "reason": (
                    "Intel GPU was detected. Intel acceleration support requires a separate "
                    "backend policy. CPU mode remains the safe default."
                )
            }

        return {
            "recommended_backend": "cpu",
            "execution_mode": "cpu",
            "allow_optional_gpu_packages": False,
            "gpu_acceleration_ready": False,
            "reason": "No supported GPU acceleration backend was confirmed."
        }

    def _check_torch_cuda(self):
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", FutureWarning)
                import torch

            gpu_names = []

            if torch.cuda.is_available():
                for index in range(torch.cuda.device_count()):
                    gpu_names.append(
                        torch.cuda.get_device_name(index)
                    )

            return {
                "torch_available": True,
                "torch_version": getattr(torch, "__version__", None),
                "cuda_available": torch.cuda.is_available(),
                "torch_cuda_version": getattr(torch.version, "cuda", None),
                "gpu_count": torch.cuda.device_count(),
                "gpu_names": gpu_names
            }

        except Exception as error:
            return {
                "torch_available": False,
                "torch_version": None,
                "cuda_available": False,
                "torch_cuda_version": None,
                "gpu_count": 0,
                "gpu_names": [],
                "error": str(error)
            }

    def _run_command(self, command):
        try:
            completed = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )

            return {
                "available": True,
                "return_code": completed.returncode,
                "stdout": completed.stdout.strip(),
                "stderr": completed.stderr.strip()
            }

        except FileNotFoundError:
            return {
                "available": False,
                "return_code": None,
                "stdout": "",
                "stderr": "Command not found."
            }

        except Exception as error:
            return {
                "available": True,
                "return_code": None,
                "stdout": "",
                "stderr": str(error)
            }
