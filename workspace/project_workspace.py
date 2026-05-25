import os
import json
import uuid
from datetime import datetime


class ProjectWorkspace:
    def __init__(self, base_projects_dir=None):
        if base_projects_dir is None:
            base_projects_dir = os.path.expanduser("~/AxonProjects")

        self.base_projects_dir = base_projects_dir

        os.makedirs(
            self.base_projects_dir,
            exist_ok=True
        )

    def create_workspace(self, workflow_name, task=None, intent=None):
        safe_workflow_name = self._safe_name(workflow_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:6]

        project_name = f"{safe_workflow_name}_{timestamp}_{unique_id}"

        project_path = os.path.join(
            self.base_projects_dir,
            project_name
        )

        self._create_structure(project_path)

        if intent is not None:
            self._write_json(
                os.path.join(project_path, "intent.json"),
                intent
            )

        if task is not None:
            self._write_json(
                os.path.join(project_path, "task.json"),
                task
            )

        return {
            "project_name": project_name,
            "project_path": project_path,
            "created_at": timestamp,
            "unique_id": unique_id
        }

    def save_workflow_result(self, project_path, result):
        self._write_json(
            os.path.join(project_path, "workflow_result.json"),
            result
        )

    def _create_structure(self, project_path):
        directories = [
            project_path,
            os.path.join(project_path, "data"),
            os.path.join(project_path, "data", "raw"),
            os.path.join(project_path, "data", "processed"),
            os.path.join(project_path, "data", "kaggle"),
            os.path.join(project_path, "models"),
            os.path.join(project_path, "logs"),
            os.path.join(project_path, "outputs"),
            os.path.join(project_path, "reports"),
            os.path.join(project_path, "notebooks"),
            os.path.join(project_path, "src")
        ]

        for directory in directories:
            os.makedirs(
                directory,
                exist_ok=True
            )

    def _write_json(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
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
            safe_name = "axon_project"

        return safe_name
