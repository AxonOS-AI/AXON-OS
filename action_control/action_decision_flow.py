import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

ACTION_CONTROL_DIR = os.path.join(BASE_DIR, "action_control")

if ACTION_CONTROL_DIR not in sys.path:
    sys.path.append(ACTION_CONTROL_DIR)

from pending_actions import PendingActions
from action_resume import ActionResume


class ActionDecisionFlow:
    def __init__(self, project_path):
        self.project_path = project_path
        self.pending_actions = PendingActions(project_path)
        self.action_resume = ActionResume(project_path)

    def list_pending(self):
        return self.pending_actions.list_pending_actions()

    def apply_decision(
        self,
        action_name,
        decision,
        reason="",
        progress_type=None,
        context=None
    ):
        pending_result = self.pending_actions.list_pending_actions()

        pending_actions = pending_result.get(
            "pending_actions",
            []
        )

        target_action = None

        for item in pending_actions:
            if item.get("action_name") == action_name:
                target_action = item
                break

        if target_action is None:
            return {
                "status": "not_found",
                "action_name": action_name,
                "message": "No pending action found with this action name.",
                "pending_count": pending_result.get("pending_count", 0)
            }

        resolved_progress_type = progress_type or target_action.get(
            "progress_type",
            "generic"
        )

        resolved_context = context or target_action.get(
            "context",
            {}
        )

        result = self.action_resume.handle_user_decision(
            action_name=action_name,
            decision=decision,
            operation_name=action_name,
            progress_type=resolved_progress_type,
            reason=reason,
            context=resolved_context
        )

        refreshed_pending = self.pending_actions.list_pending_actions()

        return {
            "status": result.get("status"),
            "action_name": action_name,
            "decision": decision,
            "action_result": result.get("action_result"),
            "operation_progress": result.get("operation_progress"),
            "pending_before": pending_result.get("pending_count", 0),
            "pending_after": refreshed_pending.get("pending_count", 0),
            "remaining_pending_actions": refreshed_pending.get(
                "pending_actions",
                []
            )
        }

    def apply_first_pending(
        self,
        decision,
        reason="",
        context=None
    ):
        pending_result = self.pending_actions.list_pending_actions()

        pending_actions = pending_result.get(
            "pending_actions",
            []
        )

        if not pending_actions:
            return {
                "status": "not_found",
                "message": "No pending actions found.",
                "pending_count": 0
            }

        first_action = pending_actions[0]

        return self.apply_decision(
            action_name=first_action.get("action_name"),
            decision=decision,
            reason=reason,
            progress_type=first_action.get("progress_type"),
            context=context or first_action.get("context", {})
        )
