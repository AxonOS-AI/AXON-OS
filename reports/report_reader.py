import os
import sys
import json
import glob

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ACTION_CONTROL_DIR = os.path.join(BASE_DIR, "action_control")

if ACTION_CONTROL_DIR not in sys.path:
    sys.path.append(ACTION_CONTROL_DIR)

try:
    from pending_actions import PendingActions
except Exception:
    PendingActions = None


class ReportReader:
    def __init__(self, project_path):
        self.project_path = project_path

    def read_project_files(self):
        return {
            "project_path": self.project_path,
            "workflow_result": self.read_json_file(
                "workflow_result.json"
            ),
            "progress": self.read_json_file(
                "progress.json"
            ),
            "intent": self.read_json_file(
                "intent.json"
            ),
            "task": self.read_json_file(
                "task.json"
            ),
            "execution_trace": self.read_jsonl_file(
                "execution_trace.jsonl"
            ),
            "decisions": self.read_jsonl_file(
                "decision_log.jsonl"
            ),
            "approvals": self.read_jsonl_file(
                "approval_log.jsonl"
            ),
            "errors": self.read_jsonl_file(
                os.path.join("logs", "errors.jsonl")
            ),
            "operation_progress": self.read_operation_progress_files(),
            "pending_actions": self.read_pending_actions(),
            "environment_discovery": self.read_json_file(
                os.path.join("reports", "environment_discovery.json")
            ),
            "installation_plan": self.read_json_file(
                os.path.join("reports", "installation_plan.json")
            ),
            "installation_approval_plan": self.read_json_file(
                os.path.join("reports", "installation_approval_plan.json")
            ),
            "virtualization_check": self.read_json_file(
                os.path.join("reports", "virtualization_check.json")
            ),
            "gpu_capability": self.read_json_file(
                os.path.join("reports", "gpu_capability.json")
            ),
            "acceleration_policy": self.read_json_file(
                os.path.join("reports", "acceleration_policy.json")
            )
        }

    def read_json_file(self, relative_path):
        file_path = os.path.join(
            self.project_path,
            relative_path
        )

        if not os.path.exists(file_path):
            return {
                "status": "missing",
                "file": relative_path,
                "data": None
            }

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)

            return {
                "status": "loaded",
                "file": relative_path,
                "data": data
            }

        except Exception as error:
            return {
                "status": "error",
                "file": relative_path,
                "message": str(error),
                "data": None
            }

    def read_jsonl_file(self, relative_path):
        file_path = os.path.join(
            self.project_path,
            relative_path
        )

        if not os.path.exists(file_path):
            return {
                "status": "missing",
                "file": relative_path,
                "records": []
            }

        records = []
        errors = []

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line_number, line in enumerate(file, start=1):
                    line = line.strip()

                    if not line:
                        continue

                    try:
                        records.append(
                            json.loads(line)
                        )
                    except Exception as error:
                        errors.append(
                            {
                                "line_number": line_number,
                                "message": str(error)
                            }
                        )

            return {
                "status": "loaded" if not errors else "partial",
                "file": relative_path,
                "records": records,
                "parse_errors": errors
            }

        except Exception as error:
            return {
                "status": "error",
                "file": relative_path,
                "message": str(error),
                "records": []
            }

    def read_operation_progress_files(self):
        operations_dir = os.path.join(
            self.project_path,
            "operations"
        )

        if not os.path.exists(operations_dir):
            return {
                "status": "missing",
                "directory": "operations",
                "records": []
            }

        pattern = os.path.join(
            operations_dir,
            "*_progress.json"
        )

        records = []
        errors = []

        for file_path in sorted(glob.glob(pattern)):
            relative_path = os.path.relpath(
                file_path,
                self.project_path
            )

            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                records.append(
                    {
                        "file": relative_path,
                        "data": data
                    }
                )

            except Exception as error:
                errors.append(
                    {
                        "file": relative_path,
                        "message": str(error)
                    }
                )

        return {
            "status": "loaded" if not errors else "partial",
            "directory": "operations",
            "records": records,
            "errors": errors
        }

    def read_pending_actions(self):
        if PendingActions is None:
            return {
                "status": "unavailable",
                "pending_count": 0,
                "pending_actions": [],
                "message": "PendingActions module is not available."
            }

        try:
            reader = PendingActions(
                self.project_path
            )

            return reader.list_pending_actions()

        except Exception as error:
            return {
                "status": "error",
                "pending_count": 0,
                "pending_actions": [],
                "message": str(error)
            }
