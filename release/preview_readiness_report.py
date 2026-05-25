import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ENVIRONMENT_DIR = os.path.join(BASE_DIR, "environment")

if ENVIRONMENT_DIR not in sys.path:
    sys.path.insert(0, ENVIRONMENT_DIR)

from axon_doctor import AXONDoctor


class PreviewReadinessReport:
    def __init__(self):
        self.version = "Developer Preview 0.1"

    def build_report(self):
        doctor = AXONDoctor()
        doctor_result = doctor.run_doctor()

        health = doctor_result.get("health", {})
        runtime = doctor_result.get("runtime", {})
        acceleration = doctor_result.get(
            "acceleration_policy",
            {}
        ).get("acceleration", {})

        virtualization = doctor_result.get(
            "virtualization",
            {}
        )

        gpu = doctor_result.get(
            "gpu_capability",
            {}
        ).get("gpu", {})

        blocking_issues = self._find_blocking_issues(
            health=health,
            runtime=runtime
        )

        warnings = self._find_warnings(
            health=health,
            acceleration=acceleration,
            virtualization=virtualization
        )

        ready = len(blocking_issues) == 0

        return {
            "status": "completed",
            "report_type": "axon_preview_readiness",
            "generated_at": self._timestamp(),
            "version": self.version,
            "ready_for_developer_preview": ready,
            "release_channel": "developer_preview",
            "blocking_issues": blocking_issues,
            "warnings": warnings,
            "completed_capabilities": self._completed_capabilities(),
            "deferred_capabilities": self._deferred_capabilities(
                acceleration=acceleration,
                gpu=gpu
            ),
            "available_commands": [
                "axon start",
                "axon start --fast",
                "axon doctor",
                "axon version",
                "axon help"
            ],
            "runtime_summary": {
                "python_executable": runtime.get("python_executable"),
                "venv_active": runtime.get("venv_active"),
                "missing_required_packages": runtime.get("missing_required_packages"),
                "missing_optional_packages": runtime.get("missing_optional_packages")
            },
            "environment_summary": {
                "virtualization_detected": virtualization.get("virtualization_detected"),
                "virtualization_type": virtualization.get("virtualization_type"),
                "gpu_vendor": gpu.get("gpu_vendor"),
                "virtual_gpu_detected": gpu.get("virtual_gpu_detected"),
                "gpu_passthrough_status": gpu.get("gpu_passthrough_status"),
                "acceleration_mode": acceleration.get("mode"),
                "backend": acceleration.get("backend"),
                "gpu_acceleration_ready": acceleration.get("gpu_acceleration_ready")
            },
            "safety_summary": {
                "release_safe": health.get("release_safe"),
                "execution_is_guarded": True,
                "approval_system_available": True,
                "reports_available": True,
                "gpu_driver_auto_install_allowed": False,
                "rocm_auto_install_allowed": False,
                "bitsandbytes_auto_install_allowed": False,
                "system_python_modified": False,
                "break_system_packages_used": False
            },
            "launch_positioning": {
                "name": "AXON OS Developer Preview 0.1",
                "description": (
                    "AI-native operating layer foundation focused on safe runtime checks, "
                    "VM/GPU awareness, approval-based operations, and developer reports."
                ),
                "not_final_release": True,
                "recommended_label": "Developer Preview"
            }
        }

    def save_report(self, output_dir=None):
        output_dir = output_dir or os.path.join(
            BASE_DIR,
            "release"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        report = self.build_report()

        json_file = os.path.join(
            output_dir,
            "axon_preview_readiness_report.json"
        )

        markdown_file = os.path.join(
            output_dir,
            "AXON_PREVIEW_READINESS_REPORT.md"
        )

        with open(json_file, "w", encoding="utf-8") as file:
            json.dump(
                report,
                file,
                indent=2,
                ensure_ascii=False
            )

        with open(markdown_file, "w", encoding="utf-8") as file:
            file.write(
                self._to_markdown(report)
            )

        report["generated_files"] = {
            "json": json_file,
            "markdown": markdown_file
        }

        return report

    def _find_blocking_issues(self, health, runtime):
        issues = []

        if not runtime.get("venv_active"):
            issues.append(
                "AXON virtual environment is not active."
            )

        for package in runtime.get("missing_required_packages", []):
            issues.append(
                f"Required runtime package is missing: {package}"
            )

        if health.get("release_safe") is not True:
            issues.append(
                "AXON Doctor did not mark this runtime as release safe."
            )

        return issues

    def _find_warnings(self, health, acceleration, virtualization):
        warnings = list(
            health.get("warnings", [])
        )

        if acceleration.get("mode") == "vm_safe_cpu":
            warnings.append(
                "GPU acceleration is not enabled in this environment. AXON will run in VM-safe CPU mode."
            )

        if virtualization.get("virtualization_detected"):
            warnings.append(
                "Virtualized runtime detected. Hardware acceleration requires WSL2, bare metal, or GPU passthrough."
            )

        return list(dict.fromkeys(warnings))

    def _completed_capabilities(self):
        return [
            "AXON CLI command wrapper",
            "AXON boot screen",
            "AXON Doctor environment health check",
            "Runtime package verification",
            "Virtualization detection",
            "GPU capability detection",
            "Acceleration policy",
            "VM-safe CPU mode",
            "Safe installation planning",
            "Approval-based operation planning",
            "Execution reports",
            "Markdown final reports"
        ]

    def _deferred_capabilities(self, acceleration, gpu):
        deferred = [
            {
                "name": "Full GPU driver automation",
                "status": "deferred",
                "reason": "GPU driver installation requires confirmed supported hardware, environment checks, and explicit approval."
            },
            {
                "name": "bitsandbytes installation",
                "status": "deferred",
                "reason": "Allowed only after supported NVIDIA CUDA backend is confirmed."
            },
            {
                "name": "ROCm setup",
                "status": "deferred",
                "reason": "Requires supported AMD hardware and environment compatibility checks."
            },
            {
                "name": "Real dataset download workflow",
                "status": "planned",
                "reason": "Requires Kaggle credentials handling and download execution safeguards."
            },
            {
                "name": "Training workflow execution",
                "status": "planned",
                "reason": "Requires dataset flow, resource policy, and safe executor real execution mode."
            },
            {
                "name": "ISO image",
                "status": "not_for_preview",
                "reason": "Developer Preview will launch as a project package and CLI before ISO."
            }
        ]

        if acceleration.get("gpu_acceleration_ready"):
            deferred = [
                item for item in deferred
                if item.get("name") != "bitsandbytes installation"
            ]

        return deferred

    def _to_markdown(self, report):
        lines = []

        lines.append("# AXON OS Developer Preview Readiness Report")
        lines.append("")
        lines.append(f"- Version: `{report.get('version')}`")
        lines.append(f"- Status: `{report.get('status')}`")
        lines.append(f"- Ready For Developer Preview: `{report.get('ready_for_developer_preview')}`")
        lines.append(f"- Release Channel: `{report.get('release_channel')}`")
        lines.append(f"- Generated At: `{report.get('generated_at')}`")
        lines.append("")

        lines.append("## Launch Positioning")
        lines.append("")
        launch = report.get("launch_positioning", {})
        lines.append(f"- Name: `{launch.get('name')}`")
        lines.append(f"- Recommended Label: `{launch.get('recommended_label')}`")
        lines.append(f"- Not Final Release: `{launch.get('not_final_release')}`")
        lines.append("")
        lines.append(launch.get("description", ""))
        lines.append("")

        lines.append("## Blocking Issues")
        lines.append("")
        blocking = report.get("blocking_issues", [])
        if not blocking:
            lines.append("No blocking issues were found.")
        else:
            for item in blocking:
                lines.append(f"- {item}")
        lines.append("")

        lines.append("## Warnings")
        lines.append("")
        warnings = report.get("warnings", [])
        if not warnings:
            lines.append("No warnings were found.")
        else:
            for item in warnings:
                lines.append(f"- {item}")
        lines.append("")

        lines.append("## Completed Capabilities")
        lines.append("")
        for item in report.get("completed_capabilities", []):
            lines.append(f"- {item}")
        lines.append("")

        lines.append("## Deferred Capabilities")
        lines.append("")
        for item in report.get("deferred_capabilities", []):
            lines.append(f"- {item.get('name')}: `{item.get('status')}`")
            lines.append(f"  - Reason: {item.get('reason')}")
        lines.append("")

        lines.append("## Available Commands")
        lines.append("")
        for command in report.get("available_commands", []):
            lines.append(f"- `{command}`")
        lines.append("")

        lines.append("## Runtime Summary")
        lines.append("")
        runtime = report.get("runtime_summary", {})
        lines.append(f"- Python Executable: `{runtime.get('python_executable')}`")
        lines.append(f"- Venv Active: `{runtime.get('venv_active')}`")
        lines.append(f"- Missing Required Packages: `{runtime.get('missing_required_packages')}`")
        lines.append(f"- Missing Optional Packages: `{runtime.get('missing_optional_packages')}`")
        lines.append("")

        lines.append("## Environment Summary")
        lines.append("")
        env = report.get("environment_summary", {})
        lines.append(f"- Virtualization Detected: `{env.get('virtualization_detected')}`")
        lines.append(f"- Virtualization Type: `{env.get('virtualization_type')}`")
        lines.append(f"- GPU Vendor: `{env.get('gpu_vendor')}`")
        lines.append(f"- Virtual GPU Detected: `{env.get('virtual_gpu_detected')}`")
        lines.append(f"- GPU Passthrough Status: `{env.get('gpu_passthrough_status')}`")
        lines.append(f"- Acceleration Mode: `{env.get('acceleration_mode')}`")
        lines.append(f"- Backend: `{env.get('backend')}`")
        lines.append(f"- GPU Acceleration Ready: `{env.get('gpu_acceleration_ready')}`")
        lines.append("")

        lines.append("## Safety Summary")
        lines.append("")
        safety = report.get("safety_summary", {})
        for key, value in safety.items():
            lines.append(f"- {key}: `{value}`")
        lines.append("")

        return "\n".join(lines) + "\n"

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"


if __name__ == "__main__":
    report = PreviewReadinessReport().save_report()
    print("AXON Preview Readiness Report generated.")
    print("Ready:", report.get("ready_for_developer_preview"))
    print("JSON:", report.get("generated_files", {}).get("json"))
    print("Markdown:", report.get("generated_files", {}).get("markdown"))
