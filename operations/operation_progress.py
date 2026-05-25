import os
import json
from datetime import datetime

from operation_status import OperationStatus


class OperationProgress:
    def __init__(self, project_path):
        self.project_path = project_path
        self.operations_dir = os.path.join(
            project_path,
            "operations"
        )

        os.makedirs(
            self.operations_dir,
            exist_ok=True
        )

    def start(
        self,
        operation_name,
        progress_type="generic",
        message="Operation started.",
        total_items=None,
        can_be_cancelled=True,
        details=None
    ):
        progress = {
            "operation_name": operation_name,
            "progress_type": progress_type,
            "status": OperationStatus.RUNNING,
            "percent": 0,
            "message": message,
            "current_item": None,
            "current_index": 0,
            "total_items": total_items,
            "speed": None,
            "eta": None,
            "can_be_cancelled": can_be_cancelled,
            "started_at": self._timestamp(),
            "updated_at": self._timestamp(),
            "details": details or {}
        }

        self._write_progress(
            operation_name,
            progress
        )

        return progress

    def update(
        self,
        operation_name,
        percent=None,
        status=None,
        message="",
        current_item=None,
        current_index=None,
        total_items=None,
        speed=None,
        eta=None,
        details=None
    ):
        progress = self.read(
            operation_name
        )

        if progress.get("status") == "missing":
            progress = {
                "operation_name": operation_name,
                "progress_type": "generic",
                "status": OperationStatus.PENDING,
                "percent": 0,
                "message": "",
                "current_item": None,
                "current_index": 0,
                "total_items": None,
                "speed": None,
                "eta": None,
                "can_be_cancelled": True,
                "started_at": None,
                "updated_at": self._timestamp(),
                "details": {}
            }

        if percent is not None:
            progress["percent"] = self._clamp_percent(
                percent
            )

        if status is not None:
            progress["status"] = OperationStatus.normalize(
                status
            )

        if message:
            progress["message"] = message

        if current_item is not None:
            progress["current_item"] = current_item

        if current_index is not None:
            progress["current_index"] = current_index

        if total_items is not None:
            progress["total_items"] = total_items

        if speed is not None:
            progress["speed"] = speed

        if eta is not None:
            progress["eta"] = eta

        if details is not None:
            progress["details"] = details

        progress["updated_at"] = self._timestamp()

        self._write_progress(
            operation_name,
            progress
        )

        return progress

    def complete(
        self,
        operation_name,
        message="Operation completed successfully.",
        details=None
    ):
        return self.update(
            operation_name=operation_name,
            percent=100,
            status=OperationStatus.COMPLETED,
            message=message,
            details=details
        )

    def fail(
        self,
        operation_name,
        message="Operation failed.",
        error=None,
        details=None
    ):
        final_details = details or {}

        if error is not None:
            final_details["error"] = error

        return self.update(
            operation_name=operation_name,
            status=OperationStatus.FAILED,
            message=message,
            details=final_details
        )

    def cancel(
        self,
        operation_name,
        message="Operation cancelled.",
        details=None
    ):
        return self.update(
            operation_name=operation_name,
            status=OperationStatus.CANCELLED,
            message=message,
            details=details
        )

    def mark_waiting_for_approval(
        self,
        operation_name,
        message="Operation is waiting for user approval.",
        details=None
    ):
        return self.update(
            operation_name=operation_name,
            status=OperationStatus.WAITING_FOR_APPROVAL,
            message=message,
            details=details
        )

    def read(self, operation_name):
        file_path = self._progress_file(
            operation_name
        )

        if not os.path.exists(file_path):
            return {
                "status": "missing",
                "operation_name": operation_name,
                "message": "No progress file found for this operation."
            }

        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_progress(self, operation_name, progress):
        file_path = self._progress_file(
            operation_name
        )

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                progress,
                file,
                indent=2,
                ensure_ascii=False
            )

    def _progress_file(self, operation_name):
        safe_name = self._safe_name(
            operation_name
        )

        return os.path.join(
            self.operations_dir,
            f"{safe_name}_progress.json"
        )

    def _safe_name(self, name):
        name = str(name).strip().lower()
        allowed = []

        for char in name:
            if char.isalnum() or char in ["_", "-"]:
                allowed.append(char)
            elif char == " ":
                allowed.append("_")

        safe_name = "".join(allowed)

        if not safe_name:
            safe_name = "operation"

        return safe_name

    def _clamp_percent(self, percent):
        try:
            percent = int(percent)
        except Exception:
            percent = 0

        if percent < 0:
            return 0

        if percent > 100:
            return 100

        return percent

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
