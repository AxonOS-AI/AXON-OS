import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ACTION_EXECUTOR_DIR = os.path.join(BASE_DIR, "action_executor")
OPERATIONS_DIR = os.path.join(BASE_DIR, "operations")

if ACTION_EXECUTOR_DIR not in sys.path:
    sys.path.append(ACTION_EXECUTOR_DIR)

if OPERATIONS_DIR not in sys.path:
    sys.path.append(OPERATIONS_DIR)

from executor_policy import ExecutorPolicy
from executor_result import ExecutorResult
from operation_progress import OperationProgress
from operation_status import OperationStatus


class SafeActionExecutor:
    def __init__(self, project_path):
        self.project_path = project_path
        self.policy = ExecutorPolicy()
        self.operation_progress = OperationProgress(project_path)

    def execute(
        self,
        action_name,
        operation_name=None,
        context=None
    ):
        operation_name = operation_name or action_name
        context = context or {}

        action_policy = self.policy.get_policy(
            action_name
        )

        current_progress = self.operation_progress.read(
            operation_name
        )

        if action_policy.get("requires_ready_state", True):
            if current_progress.get("status") == "missing":
                return ExecutorResult.blocked(
                    action_name=action_name,
                    reason="Operation progress record was not found.",
                    details={
                        "operation_name": operation_name,
                        "policy": action_policy
                    }
                )

            if current_progress.get("status") != OperationStatus.PENDING:
                return ExecutorResult.blocked(
                    action_name=action_name,
                    reason="Operation is not ready to run.",
                    details={
                        "operation_name": operation_name,
                        "operation_status": current_progress.get("status"),
                        "required_status": OperationStatus.PENDING,
                        "policy": action_policy
                    }
                )

        if not action_policy.get("execution_enabled", False):
            return ExecutorResult.execution_not_enabled(
                action_name=action_name,
                policy=action_policy
            )

        return ExecutorResult.execution_not_implemented_yet(
            action_name=action_name,
            policy=action_policy,
            details={
                "operation_name": operation_name,
                "context": context,
                "safe_mode": True,
                "will_execute_now": False
            }
        )

    def preview(
        self,
        action_name,
        operation_name=None
    ):
        operation_name = operation_name or action_name

        action_policy = self.policy.get_policy(
            action_name
        )

        current_progress = self.operation_progress.read(
            operation_name
        )

        return {
            "status": "preview",
            "action_name": action_name,
            "operation_name": operation_name,
            "policy": action_policy,
            "operation_progress": current_progress,
            "can_execute": (
                action_policy.get("execution_enabled", False)
                and current_progress.get("status") == OperationStatus.PENDING
            )
        }
