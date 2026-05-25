import os
import json
from datetime import datetime


class ErrorReporter:
    def __init__(self, project_path):
        self.project_path = project_path
        self.logs_dir = os.path.join(project_path, "logs")
        self.error_file = os.path.join(self.logs_dir, "errors.jsonl")

        os.makedirs(
            self.logs_dir,
            exist_ok=True
        )

    def report_error(
        self,
        module,
        error_code,
        message,
        reason="",
        suggestion="",
        help_url="",
        details=None,
        severity="medium"
    ):
        error_event = {
            "timestamp": self._timestamp(),
            "module": module,
            "error_code": error_code,
            "severity": severity,
            "message": message,
            "reason": reason,
            "suggestion": suggestion,
            "help_url": help_url,
            "details": details or {}
        }

        self._write_error(error_event)

        return error_event

    def report_exception(
        self,
        module,
        exception,
        error_code="UNHANDLED_EXCEPTION",
        suggestion="Review the error details and retry the operation.",
        help_url="",
        severity="high"
    ):
        return self.report_error(
            module=module,
            error_code=error_code,
            message=str(exception),
            reason=exception.__class__.__name__,
            suggestion=suggestion,
            help_url=help_url,
            details={},
            severity=severity
        )

    def _write_error(self, error_event):
        with open(self.error_file, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    error_event,
                    ensure_ascii=False
                ) + "\n"
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
