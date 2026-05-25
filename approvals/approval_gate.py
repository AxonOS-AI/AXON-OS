from approval_policy import ApprovalPolicy
from approval_log import ApprovalLog


class ApprovalGate:
    def __init__(self, project_path):
        self.project_path = project_path
        self.policy = ApprovalPolicy()
        self.log = ApprovalLog(project_path)

    def request_approval(
        self,
        action_name,
        question=None,
        context=None,
        user_decision=None,
        reason=""
    ):
        action_policy = self.policy.get_action_policy(
            action_name
        )

        if not action_policy.get("requires_approval", True):
            auto_event = self.log.record_auto_allowed(
                action_name=action_name,
                reason=action_policy.get("reason", ""),
                context={
                    "policy": action_policy,
                    "context": context or {}
                }
            )

            return {
                "status": "auto_allowed",
                "action_name": action_name,
                "approved": True,
                "requires_approval": False,
                "requires_progress": action_policy.get("requires_progress"),
                "progress_type": action_policy.get("progress_type"),
                "can_be_cancelled": action_policy.get("can_be_cancelled"),
                "risk_level": action_policy.get("risk_level"),
                "event": auto_event
            }

        approval_question = question or self._build_default_question(
            action_name,
            action_policy
        )

        request_event = self.log.record_approval_request(
            action_name=action_name,
            question=approval_question,
            policy=action_policy,
            context=context or {}
        )

        if user_decision is None:
            return {
                "status": "waiting_for_user_decision",
                "action_name": action_name,
                "approved": False,
                "requires_approval": True,
                "requires_progress": action_policy.get("requires_progress"),
                "progress_type": action_policy.get("progress_type"),
                "can_be_cancelled": action_policy.get("can_be_cancelled"),
                "risk_level": action_policy.get("risk_level"),
                "question": approval_question,
                "request_event": request_event
            }

        normalized_decision = self._normalize_decision(
            user_decision
        )

        decision_event = self.log.record_user_decision(
            action_name=action_name,
            decision=normalized_decision,
            reason=reason,
            context={
                "policy": action_policy,
                "context": context or {}
            }
        )

        return {
            "status": "approved" if normalized_decision == "approved" else "rejected",
            "action_name": action_name,
            "approved": normalized_decision == "approved",
            "requires_approval": True,
            "requires_progress": action_policy.get("requires_progress"),
            "progress_type": action_policy.get("progress_type"),
            "can_be_cancelled": action_policy.get("can_be_cancelled"),
            "risk_level": action_policy.get("risk_level"),
            "question": approval_question,
            "request_event": request_event,
            "decision_event": decision_event
        }

    def _build_default_question(self, action_name, action_policy):
        return (
            "AXON needs your approval before running this action. "
            f"Action: {action_name}. "
            f"Reason: {action_policy.get('reason')}. "
            "Do you approve?"
        )

    def _normalize_decision(self, decision):
        decision = str(decision).strip().lower()

        if decision in ["approve", "approved", "yes", "y", "allow", "allowed"]:
            return "approved"

        return "rejected"
