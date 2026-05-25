import json
from datetime import datetime


class ExecutionTracer:
    def __init__(self, project_path):
        self.project_path = project_path
        self.trace_file = f"{project_path}/execution_trace.jsonl"

    def log_step(
        self,
        step_name,
        status,
        message="",
        details=None
    ):
        event = {
            "timestamp": self._timestamp(),
            "step_name": step_name,
            "status": status,
            "message": message,
            "details": details or {}
        }

        self._write_event(event)

        return event

    def log_info(self, step_name, message="", details=None):
        return self.log_step(
            step_name=step_name,
            status="info",
            message=message,
            details=details
        )

    def log_success(self, step_name, message="", details=None):
        return self.log_step(
            step_name=step_name,
            status="success",
            message=message,
            details=details
        )

    def log_error(self, step_name, message="", details=None):
        return self.log_step(
            step_name=step_name,
            status="error",
            message=message,
            details=details
        )

    def _write_event(self, event):
        with open(self.trace_file, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    event,
                    ensure_ascii=False
                ) + "\n"
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
