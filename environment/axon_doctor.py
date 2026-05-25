import os
import sys
import importlib.util
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ENVIRONMENT_DIR = os.path.join(BASE_DIR, "environment")

if ENVIRONMENT_DIR not in sys.path:
    sys.path.append(ENVIRONMENT_DIR)

from virtualization_check import VirtualizationCheck
from gpu_capability import GPUCapability
from acceleration_policy import AccelerationPolicy


class AXONDoctor:
    def __init__(self):
        self.runtime_packages = {
            "kaggle": "kaggle",
            "sentencepiece": "sentencepiece",
            "peft": "peft",
            "trl": "trl",
            "jupyterlab": "jupyterlab",
            "opencv_cv2": "cv2",
            "torch": "torch",
            "transformers": "transformers",
            "datasets": "datasets",
            "accelerate": "accelerate",
            "numpy": "numpy",
            "pandas": "pandas",
            "safetensors": "safetensors",
            "tokenizers": "tokenizers",
            "bitsandbytes": "bitsandbytes"
        }

    def run_doctor(self):
        virtualization = VirtualizationCheck().run_check()

        gpu = GPUCapability().run_check(
            virtualization_result=virtualization
        )

        acceleration = AccelerationPolicy().build_policy(
            virtualization_result=virtualization,
            gpu_result=gpu
        )

        runtime = self._check_runtime()

        health = self._build_health_summary(
            runtime=runtime,
            virtualization=virtualization,
            gpu=gpu,
            acceleration=acceleration
        )

        return {
            "status": "completed",
            "report_type": "axon_doctor",
            "generated_at": self._timestamp(),
            "runtime": runtime,
            "virtualization": virtualization,
            "gpu_capability": gpu,
            "acceleration_policy": acceleration,
            "health": health
        }

    def save_doctor_report(self, project_path):
        import json

        result = self.run_doctor()

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
            "axon_doctor.json"
        )

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        result["generated_files"] = {
            "axon_doctor": report_file
        }

        return result

    def _check_runtime(self):
        packages = []

        missing_required = []
        missing_optional = []

        for package_name, import_name in self.runtime_packages.items():
            spec = importlib.util.find_spec(import_name)

            available = spec is not None
            path = spec.origin if spec else None

            category = self._package_category(package_name)
            required = self._package_required(package_name)

            packages.append(
                {
                    "package": package_name,
                    "import_name": import_name,
                    "available": available,
                    "path": path,
                    "category": category,
                    "required": required
                }
            )

            if not available and required:
                missing_required.append(package_name)

            if not available and not required:
                missing_optional.append(package_name)

        return {
            "python_executable": sys.executable,
            "python_version": sys.version,
            "prefix": sys.prefix,
            "base_prefix": sys.base_prefix,
            "venv_active": sys.prefix != sys.base_prefix,
            "packages": packages,
            "missing_required_packages": missing_required,
            "missing_optional_packages": missing_optional
        }

    def _build_health_summary(
        self,
        runtime,
        virtualization,
        gpu,
        acceleration
    ):
        warnings = []
        errors = []
        next_steps = []

        if not runtime.get("venv_active"):
            warnings.append(
                "AXON is not running inside a virtual environment."
            )
            next_steps.append(
                "Activate AXON .venv before running development workflows."
            )

        for package in runtime.get("missing_required_packages", []):
            errors.append(
                f"Required runtime package is missing: {package}"
            )

        acceleration_data = acceleration.get("acceleration", {})
        package_policy = acceleration.get("package_policy", {})

        if virtualization.get("virtualization_detected"):
            warnings.append(
                f"Virtualized environment detected: {virtualization.get('virtualization_type')}."
            )

        if acceleration_data.get("mode") == "vm_safe_cpu":
            warnings.append(
                "GPU acceleration is disabled because AXON is running in VM-safe CPU mode."
            )

        if package_policy.get("bitsandbytes", {}).get("allowed_now") is False:
            next_steps.append(
                "Do not install bitsandbytes until a supported CUDA backend is confirmed."
            )

        for step in acceleration.get("user_guidance", {}).get(
            "recommended_next_steps",
            []
        ):
            if step not in next_steps:
                next_steps.append(step)

        if errors:
            overall_status = "error"
        elif warnings:
            overall_status = "warning"
        else:
            overall_status = "healthy"

        return {
            "overall_status": overall_status,
            "release_safe": len(errors) == 0,
            "warnings": warnings,
            "errors": errors,
            "next_steps": next_steps,
            "summary": self._health_message(
                overall_status=overall_status,
                errors=errors,
                warnings=warnings
            )
        }

    def _health_message(self, overall_status, errors, warnings):
        if overall_status == "error":
            return (
                "AXON doctor found blocking runtime issues that must be fixed."
            )

        if overall_status == "warning":
            return (
                "AXON doctor completed with warnings. The system can continue "
                "in safe mode, but some acceleration features are disabled."
            )

        return "AXON doctor found no blocking issues."

    def _package_category(self, package_name):
        if package_name in ["bitsandbytes"]:
            return "optional_gpu_package"

        if package_name in [
            "torch",
            "transformers",
            "datasets",
            "accelerate",
            "peft",
            "trl"
        ]:
            return "ai_runtime"

        if package_name in [
            "kaggle",
            "sentencepiece",
            "jupyterlab",
            "opencv_cv2"
        ]:
            return "workflow_runtime"

        return "support_library"

    def _package_required(self, package_name):
        # Developer Preview must boot and run AXON Doctor without requiring
        # heavy AI/GPU packages. AI workflow packages are optional until the
        # real training/download workflow is enabled.
        required_packages = []

        return package_name in required_packages

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
