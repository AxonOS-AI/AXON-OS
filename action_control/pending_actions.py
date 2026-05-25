import os
import json
import glob


class PendingActions:
    def __init__(self, project_path):
        self.project_path = project_path
        self.approval_log_file = os.path.join(
            project_path,
            "approval_log.jsonl"
        )
        self.operations_dir = os.path.join(
            project_path,
            "operations"
        )

    def list_pending_actions(self):
        approval_records = self._read_approval_records()
        approval_requests = self._filter_approval_requests(
            approval_records
        )
        decided_actions = self._build_decided_actions(
            approval_records
        )
        operation_progress = self._read_operation_progress()

        pending_actions = []

        for approval in approval_requests:
            action_name = approval.get("action_name")

            if not action_name:
                continue

            if action_name in decided_actions:
                continue

            if approval.get("user_decision") is not None:
                continue

            operation = operation_progress.get(action_name, {})

            pending_actions.append(
                {
                    "action_name": action_name,
                    "question": approval.get("question"),
                    "risk_level": approval.get("policy", {}).get("risk_level"),
                    "requires_progress": approval.get("policy", {}).get("requires_progress"),
                    "progress_type": approval.get("policy", {}).get("progress_type"),
                    "can_be_cancelled": approval.get("policy", {}).get("can_be_cancelled"),
                    "approval_status": "waiting_for_user_decision",
                    "operation_status": operation.get("status"),
                    "operation_percent": operation.get("percent"),
                    "operation_file": operation.get("file"),
                    "context": approval.get("context", {})
                }
            )

        return {
            "status": "success",
            "project_path": self.project_path,
            "pending_count": len(pending_actions),
            "pending_actions": pending_actions
        }

    def _read_approval_records(self):
        if not os.path.exists(self.approval_log_file):
            return []

        records = []

        with open(self.approval_log_file, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()

                if not line:
                    continue

                try:
                    record = json.loads(line)
                except Exception:
                    continue

                records.append(record)

        return records

    def _filter_approval_requests(self, records):
        approval_requests = []

        for record in records:
            if record.get("event_type") == "approval_request":
                approval_requests.append(record)

        return approval_requests

    def _build_decided_actions(self, records):
        decided_actions = {}

        for record in records:
            if record.get("event_type") != "user_decision":
                continue

            action_name = record.get("action_name")

            if not action_name:
                continue

            decided_actions[action_name] = {
                "decision": record.get("decision"),
                "approved": record.get("approved"),
                "timestamp": record.get("timestamp")
            }

        return decided_actions

    def _read_operation_progress(self):
        if not os.path.exists(self.operations_dir):
            return {}

        result = {}

        pattern = os.path.join(
            self.operations_dir,
            "*_progress.json"
        )

        for file_path in sorted(glob.glob(pattern)):
            try:
                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)
            except Exception:
                continue

            operation_name = data.get("operation_name")

            if not operation_name:
                continue

            data["file"] = os.path.relpath(
                file_path,
                self.project_path
            )

            result[operation_name] = data

        return result
