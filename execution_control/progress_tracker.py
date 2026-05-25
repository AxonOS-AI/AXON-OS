import json
from datetime import datetime


class ProgressTracker:
    def __init__(self, project_path):
        self.project_path = project_path
        self.progress_file = f"{project_path}/progress.json"

    def update(
        self,
        current_step,
        total_steps,
        status,
        message="",
        details=None
    ):
        percent = 0

        if total_steps > 0:
            percent = int(
                (current_step / total_steps) * 100
            )

        if percent < 0:
            percent = 0

        if percent > 100:
            percent = 100

        progress = {
            "timestamp": self._timestamp(),
            "current_step": current_step,
            "total_steps": total_steps,
            "percent": percent,
            "status": status,
            "message": message,
            "details": details or {}
        }

        self._write_progress(progress)

        return progress

    def mark_started(self, total_steps, message="Workflow started"):
        return self.update(
            current_step=0,
            total_steps=total_steps,
            status="started",
            message=message
        )

    def mark_running(self, current_step, total_steps, message="", details=None):
        return self.update(
            current_step=current_step,
            total_steps=total_steps,
            status="running",
            message=message,
            details=details
        )

    def mark_completed(self, total_steps, message="Workflow completed"):
        return self.update(
            current_step=total_steps,
            total_steps=total_steps,
            status="completed",
            message=message
        )

    def mark_failed(self, current_step, total_steps, message="", details=None):
        return self.update(
            current_step=current_step,
            total_steps=total_steps,
            status="failed",
            message=message,
            details=details
        )

    def _write_progress(self, progress):
        with open(self.progress_file, "w", encoding="utf-8") as file:
            json.dump(
                progress,
                file,
                indent=2,
                ensure_ascii=False
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
