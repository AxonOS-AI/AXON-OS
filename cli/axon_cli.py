import os
import sys
import argparse

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

CLI_DIR = os.path.join(BASE_DIR, "cli")
ENVIRONMENT_DIR = os.path.join(BASE_DIR, "environment")

for path in [CLI_DIR, ENVIRONMENT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

from boot_screen import BootScreen
from axon_doctor import AXONDoctor


AXON_VERSION = "Developer Preview 0.1"


class AXONCLI:
    def run(self):
        parser = argparse.ArgumentParser(
            prog="axon",
            description="AXON OS Developer Preview CLI"
        )

        parser.add_argument(
            "command",
            nargs="?",
            default="help",
            choices=[
                "start",
                "doctor",
                "version",
                "help"
            ],
            help="AXON command to run"
        )

        parser.add_argument(
            "--fast",
            action="store_true",
            help="Skip slow boot animation delay"
        )

        args = parser.parse_args()

        if args.command == "start":
            return self.start(fast=args.fast)

        if args.command == "doctor":
            return self.doctor()

        if args.command == "version":
            return self.version()

        return self.help()

    def start(self, fast=False):
        BootScreen().render(fast=fast)

        doctor = AXONDoctor()
        result = doctor.run_doctor()

        health = result.get("health", {})
        acceleration = result.get(
            "acceleration_policy",
            {}
        ).get("acceleration", {})

        virtualization = result.get(
            "virtualization",
            {}
        )

        print("AXON Status")
        print("-----------")
        print(f"Version: {AXON_VERSION}")
        print(f"Health: {health.get('overall_status')}")
        print(f"Release Safe: {health.get('release_safe')}")
        print(f"Virtualization: {virtualization.get('virtualization_type')}")
        print(f"Acceleration Mode: {acceleration.get('mode')}")
        print(f"Backend: {acceleration.get('backend')}")
        print("")
        print('Type "axon doctor" to view full environment health.')
        print('Type "axon help" to view available commands.')
        return 0

    def doctor(self):
        doctor = AXONDoctor()
        result = doctor.run_doctor()

        health = result.get("health", {})
        runtime = result.get("runtime", {})
        acceleration = result.get(
            "acceleration_policy",
            {}
        ).get("acceleration", {})

        virtualization = result.get(
            "virtualization",
            {}
        )

        gpu = result.get(
            "gpu_capability",
            {}
        ).get("gpu", {})

        print("AXON Doctor")
        print("===========")
        print(f"Status: {health.get('overall_status')}")
        print(f"Release Safe: {health.get('release_safe')}")
        print("")
        print("Runtime")
        print("-------")
        print(f"Python: {runtime.get('python_executable')}")
        print(f"Venv Active: {runtime.get('venv_active')}")
        print(f"Missing Required Packages: {runtime.get('missing_required_packages')}")
        print(f"Missing Optional Packages: {runtime.get('missing_optional_packages')}")
        print("")
        print("Virtualization")
        print("--------------")
        print(f"Detected: {virtualization.get('virtualization_detected')}")
        print(f"Type: {virtualization.get('virtualization_type')}")
        print("")
        print("GPU")
        print("---")
        print(f"Guest GPU Visible: {gpu.get('guest_gpu_visible')}")
        print(f"GPU Vendor: {gpu.get('gpu_vendor')}")
        print(f"Virtual GPU Detected: {gpu.get('virtual_gpu_detected')}")
        print(f"GPU Passthrough Status: {gpu.get('gpu_passthrough_status')}")
        print("")
        print("Acceleration")
        print("------------")
        print(f"Mode: {acceleration.get('mode')}")
        print(f"Backend: {acceleration.get('backend')}")
        print(f"GPU Ready: {acceleration.get('gpu_acceleration_ready')}")
        print(f"Allow GPU Packages: {acceleration.get('allow_gpu_packages')}")
        print("")
        print("Warnings")
        print("--------")
        warnings = health.get("warnings", [])
        if not warnings:
            print("No warnings.")
        else:
            for warning in warnings:
                print(f"- {warning}")

        print("")
        print("Next Steps")
        print("----------")
        next_steps = health.get("next_steps", [])
        if not next_steps:
            print("No next steps.")
        else:
            for step in next_steps:
                print(f"- {step}")

        return 0

    def version(self):
        print(f"AXON OS {AXON_VERSION}")
        print("Developed by Abdullah Ali")
        return 0

    def help(self):
        print("AXON OS Developer Preview CLI")
        print("")
        print("Commands:")
        print("  axon start      Start AXON preview runtime")
        print("  axon doctor     Check AXON environment health")
        print("  axon version    Show AXON version")
        print("  axon help       Show this help")
        print("")
        print("Development usage:")
        print("  python3 cli/axon_cli.py start --fast")
        print("  python3 cli/axon_cli.py doctor")
        return 0


if __name__ == "__main__":
    raise SystemExit(
        AXONCLI().run()
    )
