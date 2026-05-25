import sys
import os
import json
import platform
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ENVIRONMENT_DIR = os.path.join(BASE_DIR, "environment")

if ENVIRONMENT_DIR not in sys.path:
    sys.path.append(ENVIRONMENT_DIR)

from tool_check import ToolCheck
from dependency_audit import DependencyAudit


class EnvironmentDiscovery:
    def __init__(self):
        self.tool_check = ToolCheck()
        self.dependency_audit = DependencyAudit()

    def run_discovery(self):
        tools = self.tool_check.check_tools()
        dependencies = self.dependency_audit.audit_packages()
        gpu = self.check_gpu_capability()

        return {
            "status": "completed",
            "report_type": "environment_discovery",
            "generated_at": self._timestamp(),
            "system": self._system_info(),
            "tools": tools,
            "dependencies": dependencies,
            "gpu": gpu,
            "recommendation": self._build_recommendation(
                tools=tools,
                dependencies=dependencies,
                gpu=gpu
            ),
            "privacy": {
                "personal_information_included": False,
                "secret_values_included": False,
                "safe_for_reports": True
            }
        }

    def save_discovery_report(self, project_path):
        report = self.run_discovery()

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
            "environment_discovery.json"
        )

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False
            )

        return {
            "status": "created",
            "report_file": report_file,
            "report": report
        }

    def check_gpu_capability(self):
        result = {
            "status": "completed",
            "gpu_support_mode": "adaptive",
            "current_machine_gpu_detected": False,
            "torch_available": False,
            "torch_version": None,
            "torch_cuda_version": None,
            "cuda_available": False,
            "gpu_count": 0,
            "gpu_names": [],
            "recommended_execution_mode": "cpu",
            "note": (
                "This result describes the current machine only. "
                "AXON must adapt to each user's hardware at runtime."
            )
        }

        try:
            import torch

            result["torch_available"] = True
            result["torch_version"] = getattr(torch, "__version__", None)
            result["torch_cuda_version"] = getattr(torch.version, "cuda", None)
            result["cuda_available"] = bool(torch.cuda.is_available())
            result["gpu_count"] = int(torch.cuda.device_count())

            if result["cuda_available"] and result["gpu_count"] > 0:
                result["current_machine_gpu_detected"] = True
                result["recommended_execution_mode"] = "cuda"

                gpu_names = []

                for index in range(result["gpu_count"]):
                    try:
                        gpu_names.append(
                            torch.cuda.get_device_name(index)
                        )
                    except Exception:
                        gpu_names.append("unknown")

                result["gpu_names"] = gpu_names

            else:
                result["recommended_execution_mode"] = "cpu"

        except Exception as error:
            result["status"] = "partial"
            result["error"] = str(error)
            result["recommended_execution_mode"] = "cpu"

        return result

    def _system_info(self):
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_version": platform.version(),
            "machine": platform.machine(),
            "python_version": platform.python_version()
        }

    def _build_recommendation(self, tools, dependencies, gpu):
        missing_tools = tools.get("missing_tools", [])
        missing_packages = dependencies.get("missing_packages", [])

        execution_mode = gpu.get(
            "recommended_execution_mode",
            "cpu"
        )

        return {
            "execution_mode": execution_mode,
            "can_run_cpu_workflows": True,
            "can_run_gpu_workflows": gpu.get("cuda_available", False),
            "missing_tools": missing_tools,
            "missing_packages": missing_packages,
            "requires_installation_before_full_ai_workflows": (
                len(missing_tools) > 0 or len(missing_packages) > 0
            ),
            "message": (
                "Environment discovery completed. "
                "AXON should use adaptive execution based on available tools, packages, and GPU capability."
            )
        }

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
