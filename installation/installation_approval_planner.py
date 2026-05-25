import sys
import os
import json
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

APPROVALS_DIR = os.path.join(BASE_DIR, "approvals")
OPERATIONS_DIR = os.path.join(BASE_DIR, "operations")

if APPROVALS_DIR not in sys.path:
    sys.path.append(APPROVALS_DIR)

if OPERATIONS_DIR not in sys.path:
    sys.path.append(OPERATIONS_DIR)

from approval_gate import ApprovalGate
from operation_progress import OperationProgress


class InstallationApprovalPlanner:
    def __init__(self, project_path):
        self.project_path = project_path
        self.approval_gate = ApprovalGate(project_path)
        self.operation_progress = OperationProgress(project_path)

    def plan_approvals_from_installation_plan(self):
        plan_file = os.path.join(
            self.project_path,
            "reports",
            "installation_plan.json"
        )

        if not os.path.exists(plan_file):
            return {
                "status": "error",
                "error_code": "INSTALLATION_PLAN_NOT_FOUND",
                "message": "Installation plan report was not found.",
                "plan_file": plan_file,
                "suggestion": "Build installation_plan.json before creating approval requests."
            }

        with open(plan_file, "r", encoding="utf-8") as file:
            plan = json.load(file)

        items = plan.get("items", [])

        approval_results = []

        for item in items:
            result = self._create_installation_approval(
                item=item
            )

            approval_results.append(result)

        output = {
            "status": "planned",
            "report_type": "installation_approval_plan",
            "generated_at": self._timestamp(),
            "project_path": self.project_path,
            "source_plan": plan_file,
            "total_items": len(items),
            "approval_requests_created": len(approval_results),
            "items": approval_results,
            "safety": {
                "planning_only": True,
                "no_installation_executed": True,
                "no_system_changes_made": True,
                "no_pip_command_executed": True,
                "requires_user_approval_before_install": True
            }
        }

        self._save_output(output)

        return output

    def _create_installation_approval(self, item):
        item_name = item.get("item_name")
        mapping = item.get("mapping", {})
        policy = item.get("policy", {})

        install_type = mapping.get("install_type")
        install_command = mapping.get("install_command")
        risk_level = policy.get("risk_level")

        action_name = f"install_{item_name}"

        question = (
            "AXON needs your approval before planning installation. "
            f"Item: {item_name}. "
            f"Install type: {install_type}. "
            f"Risk level: {risk_level}. "
            "Do you approve preparing this installation action?"
        )

        approval = self.approval_gate.request_approval(
            action_name=action_name,
            question=question,
            context={
                "installation_item": item_name,
                "install_type": install_type,
                "package_name": mapping.get("package_name"),
                "install_command": install_command,
                "purpose": mapping.get("purpose"),
                "risk_note": mapping.get("risk_note"),
                "source": item.get("source"),
                "will_execute_now": False
            }
        )

        operation_name = action_name

        progress = self.operation_progress.start(
            operation_name=operation_name,
            progress_type="installation",
            message="Installation action is waiting for user approval.",
            can_be_cancelled=True,
            details={
                "installation_item": item_name,
                "install_type": install_type,
                "install_command": install_command,
                "risk_level": risk_level,
                "will_execute_now": False
            }
        )

        progress = self.operation_progress.mark_waiting_for_approval(
            operation_name=operation_name,
            message="Installation action is waiting for user approval.",
            details={
                "installation_item": item_name,
                "install_type": install_type,
                "install_command": install_command,
                "risk_level": risk_level,
                "will_execute_now": False
            }
        )

        return {
            "status": "waiting_for_approval",
            "action_name": action_name,
            "operation_name": operation_name,
            "item_name": item_name,
            "install_type": install_type,
            "risk_level": risk_level,
            "install_command": install_command,
            "approval": approval,
            "operation_progress": progress,
            "will_execute_now": False
        }

    def _save_output(self, output):
        reports_dir = os.path.join(
            self.project_path,
            "reports"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        output_file = os.path.join(
            reports_dir,
            "installation_approval_plan.json"
        )

        with open(output_file, "w", encoding="utf-8") as file:
            json.dump(
                output,
                file,
                indent=2,
                ensure_ascii=False
            )

        output["generated_files"] = {
            "installation_approval_plan": output_file
        }

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
