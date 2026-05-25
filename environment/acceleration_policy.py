class AccelerationPolicy:
    def build_policy(self, virtualization_result=None, gpu_result=None):
        virtualization_result = virtualization_result or {}
        gpu_result = gpu_result or {}

        virtualization = {
            "detected": virtualization_result.get(
                "virtualization_detected",
                gpu_result.get("virtualization", {}).get(
                    "virtualization_detected",
                    False
                )
            ),
            "type": virtualization_result.get(
                "virtualization_type",
                gpu_result.get("virtualization", {}).get(
                    "virtualization_type",
                    "unknown"
                )
            ),
            "safe_mode": virtualization_result.get(
                "safe_mode",
                "unknown"
            )
        }

        gpu = gpu_result.get("gpu", {})
        recommendation = gpu_result.get("recommendation", {})
        policy = gpu_result.get("policy", {})
        tools = gpu_result.get("tools", {})
        torch_info = gpu_result.get("torch", {})

        acceleration_mode = self._decide_acceleration_mode(
            virtualization=virtualization,
            gpu=gpu,
            recommendation=recommendation,
            torch_info=torch_info
        )

        package_policy = self._build_package_policy(
            acceleration_mode=acceleration_mode,
            gpu=gpu,
            tools=tools,
            torch_info=torch_info,
            recommendation=recommendation
        )

        user_guidance = self._build_user_guidance(
            acceleration_mode=acceleration_mode,
            virtualization=virtualization,
            gpu=gpu
        )

        return {
            "status": "completed",
            "report_type": "acceleration_policy",
            "virtualization": virtualization,
            "gpu_summary": {
                "guest_gpu_visible": gpu.get("guest_gpu_visible"),
                "gpu_vendor": gpu.get("gpu_vendor"),
                "virtual_gpu_detected": gpu.get("virtual_gpu_detected"),
                "gpu_passthrough_status": gpu.get("gpu_passthrough_status"),
                "gpu_devices": gpu.get("gpu_devices", [])
            },
            "torch_summary": {
                "torch_available": torch_info.get("torch_available"),
                "torch_version": torch_info.get("torch_version"),
                "cuda_available": torch_info.get("cuda_available"),
                "torch_cuda_version": torch_info.get("torch_cuda_version"),
                "gpu_count": torch_info.get("gpu_count"),
                "gpu_names": torch_info.get("gpu_names", [])
            },
            "acceleration": acceleration_mode,
            "package_policy": package_policy,
            "user_guidance": user_guidance,
            "safety": {
                "gpu_driver_auto_install_allowed": False,
                "nvidia_driver_auto_install_allowed": False,
                "rocm_auto_install_allowed": False,
                "bitsandbytes_auto_install_allowed": False,
                "requires_explicit_user_approval": True,
                "reason": acceleration_mode.get("reason")
            }
        }

    def save_policy_report(
        self,
        project_path,
        virtualization_result=None,
        gpu_result=None
    ):
        import os
        import json

        result = self.build_policy(
            virtualization_result=virtualization_result,
            gpu_result=gpu_result
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
            "acceleration_policy.json"
        )

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        result["generated_files"] = {
            "acceleration_policy": report_file
        }

        return result

    def _decide_acceleration_mode(
        self,
        virtualization,
        gpu,
        recommendation,
        torch_info
    ):
        virtualization_detected = virtualization.get("detected")
        virtualization_type = virtualization.get("type")
        gpu_vendor = gpu.get("gpu_vendor")
        passthrough_status = gpu.get("gpu_passthrough_status")
        virtual_gpu_detected = gpu.get("virtual_gpu_detected")
        cuda_available = torch_info.get("cuda_available")

        if virtualization_detected and passthrough_status != "possible_real_gpu_visible_to_guest":
            return {
                "mode": "vm_safe_cpu",
                "backend": "cpu",
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False,
                "allow_gpu_driver_plan": False,
                "recommended_for_release": True,
                "reason": (
                    "Virtualized environment detected without confirmed real GPU passthrough. "
                    "AXON must use VM-safe CPU mode and must not install GPU drivers or GPU packages automatically."
                )
            }

        if gpu_vendor == "nvidia" and cuda_available:
            return {
                "mode": "cuda_ready",
                "backend": "cuda",
                "gpu_acceleration_ready": True,
                "allow_gpu_packages": True,
                "allow_gpu_driver_plan": False,
                "recommended_for_release": True,
                "reason": (
                    "NVIDIA CUDA appears ready. Optional CUDA packages may be planned only after explicit user approval."
                )
            }

        if gpu_vendor == "nvidia":
            return {
                "mode": "nvidia_not_ready",
                "backend": "cpu",
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False,
                "allow_gpu_driver_plan": True,
                "recommended_for_release": False,
                "reason": (
                    "NVIDIA GPU was detected, but CUDA readiness was not confirmed. AXON should stay on CPU mode and provide setup guidance."
                )
            }

        if gpu_vendor == "amd":
            return {
                "mode": "amd_check_required",
                "backend": "cpu_or_rocm_later",
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False,
                "allow_gpu_driver_plan": True,
                "recommended_for_release": False,
                "reason": (
                    "AMD GPU was detected. ROCm or alternative acceleration support requires hardware and environment compatibility checks."
                )
            }

        if gpu_vendor == "intel":
            return {
                "mode": "intel_check_required",
                "backend": "cpu_or_intel_later",
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False,
                "allow_gpu_driver_plan": True,
                "recommended_for_release": False,
                "reason": (
                    "Intel GPU was detected. Intel acceleration requires a separate backend policy. CPU mode remains safe."
                )
            }

        if gpu_vendor == "virtual" or virtual_gpu_detected:
            return {
                "mode": "virtual_gpu_cpu",
                "backend": "cpu",
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False,
                "allow_gpu_driver_plan": False,
                "recommended_for_release": True,
                "reason": (
                    "Only a virtual GPU is visible. AXON must use CPU mode unless real GPU passthrough is configured."
                )
            }

        return {
            "mode": recommendation.get("execution_mode", "cpu"),
            "backend": recommendation.get("recommended_backend", "cpu"),
            "gpu_acceleration_ready": False,
            "allow_gpu_packages": False,
            "allow_gpu_driver_plan": False,
            "recommended_for_release": True,
            "reason": recommendation.get(
                "reason",
                "No supported GPU acceleration backend was confirmed."
            )
        }

    def _build_package_policy(
        self,
        acceleration_mode,
        gpu,
        tools,
        torch_info,
        recommendation
    ):
        allow_gpu_packages = acceleration_mode.get(
            "allow_gpu_packages",
            False
        )

        return {
            "bitsandbytes": {
                "required": False,
                "category": "optional_gpu_package",
                "allowed_now": bool(
                    allow_gpu_packages
                    and acceleration_mode.get("backend") == "cuda"
                ),
                "install_condition": "NVIDIA CUDA backend confirmed.",
                "current_status": "allowed" if (
                    allow_gpu_packages
                    and acceleration_mode.get("backend") == "cuda"
                ) else "blocked_or_deferred",
                "reason": (
                    "bitsandbytes is only allowed when a supported CUDA backend is confirmed."
                )
            },
            "nvidia_smi": {
                "required": False,
                "category": "driver_tool",
                "available": tools.get("nvidia_smi_available"),
                "auto_install_allowed": False,
                "reason": "nvidia-smi belongs to the NVIDIA driver stack and must not be auto-installed by AXON."
            },
            "rocm": {
                "required": False,
                "category": "optional_amd_backend",
                "available": tools.get("rocm_smi_available"),
                "auto_install_allowed": False,
                "reason": "ROCm setup requires supported AMD hardware and environment checks before planning."
            },
            "gpu_drivers": {
                "required": False,
                "category": "driver_stack",
                "auto_install_allowed": False,
                "reason": "GPU driver installation is never automatic and requires a confirmed supported environment and explicit user approval."
            }
        }

    def _build_user_guidance(self, acceleration_mode, virtualization, gpu):
        mode = acceleration_mode.get("mode")
        virtualization_type = virtualization.get("type")

        if mode == "vm_safe_cpu":
            return {
                "summary": "AXON is running in VM-safe CPU mode.",
                "message": (
                    f"AXON detected {virtualization_type}. The guest system does not show confirmed real GPU passthrough. "
                    "GPU acceleration is disabled safely. For Windows users who need GPU acceleration, AXON should recommend WSL2 mode when supported. "
                    "Advanced users may use bare metal Linux or a hypervisor with real GPU passthrough."
                ),
                "recommended_next_steps": [
                    "Continue using AXON in CPU mode.",
                    "Use AXON WSL2 Mode for Windows GPU acceleration when supported.",
                    "Use bare metal Linux or Proxmox/ESXi/KVM GPU passthrough for advanced GPU setups.",
                    "Do not install GPU drivers inside this VM unless real passthrough is confirmed."
                ]
            }

        if mode == "cuda_ready":
            return {
                "summary": "CUDA GPU acceleration appears ready.",
                "message": (
                    "AXON detected a CUDA-ready NVIDIA environment. Optional CUDA packages can be planned after explicit approval."
                ),
                "recommended_next_steps": [
                    "Run a CUDA validation test.",
                    "Plan optional packages such as bitsandbytes after approval.",
                    "Record GPU readiness in the final report."
                ]
            }

        if mode in ["amd_check_required", "nvidia_not_ready", "intel_check_required"]:
            return {
                "summary": "GPU was detected, but acceleration is not ready yet.",
                "message": acceleration_mode.get("reason"),
                "recommended_next_steps": [
                    "Keep CPU mode enabled.",
                    "Generate a GPU setup guidance report.",
                    "Do not auto-install GPU drivers.",
                    "Ask for explicit approval before any hardware-specific setup."
                ]
            }

        return {
            "summary": "AXON will use CPU mode.",
            "message": acceleration_mode.get("reason"),
            "recommended_next_steps": [
                "Continue in CPU mode.",
                "Run hardware detection again if the environment changes."
            ]
        }
