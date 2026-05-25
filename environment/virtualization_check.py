import os
import json
import subprocess


class VirtualizationCheck:

    def save_check_report(self, project_path):
        result = self.run_check()

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
            "virtualization_check.json"
        )

        with open(report_file, "w", encoding="utf-8") as file:
            json.dump(
                result,
                file,
                indent=2,
                ensure_ascii=False
            )

        result["generated_files"] = {
            "virtualization_check": report_file
        }

        return result

    def run_check(self):
        systemd_result = self._run_command(
            ["systemd-detect-virt"]
        )

        cpuinfo_text = self._read_file(
            "/proc/cpuinfo"
        )

        product_name = self._read_file(
            "/sys/class/dmi/id/product_name"
        ).strip()

        sys_vendor = self._read_file(
            "/sys/class/dmi/id/sys_vendor"
        ).strip()

        board_vendor = self._read_file(
            "/sys/class/dmi/id/board_vendor"
        ).strip()

        combined_text = " ".join(
            [
                systemd_result.get("stdout", ""),
                product_name,
                sys_vendor,
                board_vendor,
                cpuinfo_text[:5000]
            ]
        ).lower()

        virtualization_type = self._detect_type(
            systemd_result=systemd_result,
            combined_text=combined_text
        )

        virtualization_detected = virtualization_type not in [
            "none",
            "unknown"
        ]

        recommended_mode = self._recommended_mode(
            virtualization_detected=virtualization_detected,
            virtualization_type=virtualization_type
        )

        return {
            "status": "completed",
            "report_type": "virtualization_check",
            "virtualization_detected": virtualization_detected,
            "virtualization_type": virtualization_type,
            "recommended_mode": recommended_mode,
            "safe_mode": "vm_safe" if virtualization_detected else "bare_metal",
            "systemd_detect_virt": {
                "available": systemd_result.get("available"),
                "return_code": systemd_result.get("return_code"),
                "stdout": systemd_result.get("stdout"),
                "stderr": systemd_result.get("stderr")
            },
            "dmi": {
                "product_name": product_name,
                "sys_vendor": sys_vendor,
                "board_vendor": board_vendor
            },
            "policy": {
                "auto_install_gpu_drivers": False,
                "auto_install_rocm": False,
                "auto_install_nvidia_drivers": False,
                "auto_install_bitsandbytes": False,
                "reason": self._policy_reason(
                    virtualization_detected=virtualization_detected,
                    virtualization_type=virtualization_type
                )
            }
        }

    def _detect_type(self, systemd_result, combined_text):
        detected = str(systemd_result.get("stdout", "")).strip().lower()

        if detected and detected not in ["none"]:
            return detected

        checks = [
            ("vmware", ["vmware", "vmw"]),
            ("virtualbox", ["virtualbox", "vbox"]),
            ("wsl", ["microsoft", "wsl"]),
            ("kvm", ["kvm", "qemu"]),
            ("proxmox", ["proxmox"]),
            ("hyperv", ["hyper-v", "hyperv"]),
            ("xen", ["xen"])
        ]

        for vm_type, markers in checks:
            for marker in markers:
                if marker in combined_text:
                    return vm_type

        if detected == "none":
            return "none"

        return "unknown"

    def _recommended_mode(self, virtualization_detected, virtualization_type):
        if virtualization_detected:
            return "cpu_vm_safe"

        if virtualization_type == "none":
            return "hardware_detection_allowed"

        return "cpu_safe_unknown_environment"

    def _policy_reason(self, virtualization_detected, virtualization_type):
        if virtualization_detected:
            return (
                "Virtualized environment detected. GPU drivers and GPU packages "
                "must not be installed automatically unless GPU passthrough or "
                "hardware acceleration is explicitly confirmed."
            )

        if virtualization_type == "none":
            return (
                "Bare metal environment appears possible. Hardware acceleration "
                "may be checked, but driver installation still requires explicit "
                "user approval."
            )

        return (
            "Virtualization status is unknown. AXON must use safe CPU mode until "
            "hardware acceleration is confirmed."
        )

    def _read_file(self, path):
        try:
            if not os.path.exists(path):
                return ""

            with open(path, "r", encoding="utf-8", errors="ignore") as file:
                return file.read()

        except Exception:
            return ""

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
