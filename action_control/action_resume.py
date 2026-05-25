import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

APPROVALS_DIR = os.path.join(BASE_DIR, "approvals")
OPERATIONS_DIR = os.path.join(BASE_DIR, "operations")

if APPROVALS_DIR not in sys.path:
    sys.path.append(APPROVALS_DIR)

if OPERATIONS_DIR not in sys.path:
    sys.path.append(OPERATIONS_DIR)

from approval_log import ApprovalLog
from operation_progress import OperationProgress
from operation_status import OperationStatus
from action_result import ActionResult


class ActionResume:
    def __init__(self, project_path):
        self.project_path = project_path
        self.approval_log = ApprovalLog(project_path)
        self.operation_progress = OperationProgress(project_path)

    def handle_user_decision(
        self,
        action_name,
        decision,
        operation_name=None,
        progress_type="generic",
        reason="",
        context=None
    ):
        operation_name = operation_name or action_name
        normalized_decision = self._normalize_decision(decision)

        self.approval_log.record_user_decision(
            action_name=action_name,
            decision=normalized_decision,
            reason=reason,
            context=context or {}
        )

        current_progress = self.operation_progress.read(
            operation_name
        )

        if current_progress.get("status") == "missing":
            self.operation_progress.start(
                operation_name=operation_name,
                progress_type=progress_type,
                message="Operation decision received.",
                can_be_cancelled=True,
                details={
                    "created_by": "ActionResume",
                    "decision": normalized_decision,
                    "will_execute_now": False
                }
            )
        else:
            current_progress["progress_type"] = progress_type
            self.operation_progress._write_progress(
                operation_name,
                current_progress
            )

        if normalized_decision == "approved":
            result = ActionResult.approved(
                action_name=action_name,
                operation_name=operation_name,
                details={
                    "decision": normalized_decision,
                    "reason": reason,
                    "context": context or {}
                }
            )

            progress = self.operation_progress.update(
                operation_name=operation_name,
                status=OperationStatus.PENDING,
                message="Operation is approved and ready to run.",
                details={
                    "action_state": result.get("status"),
                    "decision": normalized_decision,
                    "reason": reason,
                    "progress_type": progress_type,
                    "will_execute_now": False
                }
            )

            return {
                "status": result.get("status"),
                "action_result": result,
                "operation_progress": progress
            }

        result = ActionResult.rejected(
            action_name=action_name,
            operation_name=operation_name,
            details={
                "decision": normalized_decision,
                "reason": reason,
                "context": context or {}
            }
        )

        progress = self.operation_progress.cancel(
            operation_name=operation_name,
            message="Operation was rejected by the user.",
            details={
                "action_state": result.get("status"),
                "decision": normalized_decision,
                "reason": reason,
                "progress_type": progress_type,
                "will_execute_now": False
            }
        )

        return {
            "status": result.get("status"),
            "action_result": result,
            "operation_progress": progress
        }

    def build_waiting_result(
        self,
        action_name,
        operation_name=None,
        progress_type="generic",
        details=None
    ):
        operation_name = operation_name or action_name

        result = ActionResult.waiting_for_approval(
            action_name=action_name,
            operation_name=operation_name,
            details=details or {}
        )

        current_progress = self.operation_progress.read(
            operation_name
        )

        if current_progress.get("status") == "missing":
            self.operation_progress.start(
                operation_name=operation_name,
                progress_type=progress_type,
                message="Operation is waiting for user approval.",
                can_be_cancelled=True,
                details={
                    "action_state": result.get("status"),
                    "will_execute_now": False
                }
            )
        else:
            current_progress["progress_type"] = progress_type
            self.operation_progress._write_progress(
                operation_name,
                current_progress
            )

        progress = self.operation_progress.mark_waiting_for_approval(
            operation_name=operation_name,
            message="Operation is waiting for user approval.",
            details={
                "action_state": result.get("status"),
                "progress_type": progress_type,
                "will_execute_now": False
            }
        )

        return {
            "status": result.get("status"),
            "action_result": result,
            "operation_progress": progress
        }

    def _normalize_decision(self, decision):
        decision = str(decision).strip().lower()

        if decision in ["approve", "approved", "yes", "y", "allow", "allowed"]:
            return "approved"

        return "rejected"
