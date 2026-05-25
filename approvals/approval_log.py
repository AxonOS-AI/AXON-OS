import os
import json
from datetime import datetime


class ApprovalLog:
    def __init__(self, project_path):
        self.project_path = project_path
        self.log_file = os.path.join(
            project_path,
            "approval_log.jsonl"
        )

    def record_approval_request(
        self,
        action_name,
        question,
        policy,
        context=None
    ):
        event = {
            "timestamp": self._timestamp(),
            "event_type": "approval_request",
            "action_name": action_name,
            "question": question,
            "policy": policy,
            "context": context or {},
            "user_decision": None
        }

        self._write_event(event)

        return event

    def record_user_decision(
        self,
        action_name,
        decision,
        reason="",
        context=None
    ):
        event = {
            "timestamp": self._timestamp(),
            "event_type": "user_decision",
            "action_name": action_name,
            "decision": decision,
            "approved": decision == "approved",
            "reason": reason,
            "context": context or {}
        }

        self._write_event(event)

        return event

    def record_auto_allowed(
        self,
        action_name,
        reason="",
        context=None
    ):
        event = {
            "timestamp": self._timestamp(),
            "event_type": "auto_allowed",
            "action_name": action_name,
            "approved": True,
            "reason": reason,
            "context": context or {}
        }

        self._write_event(event)

        return event

    def _write_event(self, event):
        with open(self.log_file, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False
                ) + "\n"
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
