from local_dataset_source import LocalDatasetSource
from url_dataset_source import UrlDatasetSource
from kaggle_source import KaggleSource


class DatasetManager:
    def __init__(self):
        self.supported_sources = {
            "local_dataset": "Local dataset from user device",
            "kaggle": "Search and download dataset from Kaggle",
            "url": "Download dataset from direct URL",
            "skip": "Skip dataset selection"
        }

        self.local_dataset_source = LocalDatasetSource()
        self.url_dataset_source = UrlDatasetSource()
        self.kaggle_source = KaggleSource()

    def prepare_dataset_source(
        self,
        selected_source,
        project_path,
        options=None
    ):
        options = options or {}

        if selected_source not in self.supported_sources:
            return {
                "status": "error",
                "source": selected_source,
                "error_code": "UNSUPPORTED_DATASET_SOURCE",
                "message": f"Unsupported dataset source: {selected_source}",
                "supported_sources": list(self.supported_sources.keys())
            }

        if selected_source == "local_dataset":
            return self._prepare_local_dataset(
                project_path,
                options
            )

        if selected_source == "kaggle":
            return self._prepare_kaggle_dataset(
                project_path,
                options
            )

        if selected_source == "url":
            return self._prepare_url_dataset(
                project_path,
                options
            )

        if selected_source == "skip":
            return self._prepare_skip_dataset(
                project_path
            )

        return {
            "status": "error",
            "source": selected_source,
            "error_code": "UNKNOWN_DATASET_MANAGER_STATE",
            "message": "Dataset manager reached an unknown state."
        }

    def _prepare_local_dataset(self, project_path, options):
        local_path = options.get("local_path", "")

        if not local_path:
            return {
                "status": "waiting_for_user_input",
                "source": "local_dataset",
                "message": "Local dataset path is required.",
                "requires": {
                    "file_picker": True,
                    "path_input": True
                },
                "project_path": project_path
            }

        inspection = self.local_dataset_source.inspect(
            local_path
        )

        if inspection.get("status") != "ready":
            return {
                "status": "error",
                "source": "local_dataset",
                "error_code": inspection.get(
                    "error_code",
                    "LOCAL_DATASET_INSPECTION_FAILED"
                ),
                "message": inspection.get(
                    "message",
                    "Local dataset inspection failed."
                ),
                "inspection": inspection,
                "project_path": project_path
            }

        return {
            "status": "prepared",
            "source": "local_dataset",
            "message": "Local dataset source prepared and validated.",
            "inspection": inspection,
            "project_path": project_path
        }

    def _prepare_kaggle_dataset(self, project_path, options):
        query = options.get("query", "")

        if not query:
            return {
                "status": "waiting_for_user_input",
                "source": "kaggle",
                "message": "Kaggle search query is required.",
                "requires": {
                    "query_input": True,
                    "internet": True,
                    "credentials": True,
                    "user_approval_before_search": True,
                    "user_approval_before_download": True
                },
                "project_path": project_path
            }

        search_plan = self.kaggle_source.prepare_search_plan(
            query=query,
            project_path=project_path
        )

        return {
            "status": "planned",
            "source": "kaggle",
            "message": "Kaggle dataset source planned and credentials checked. No download was executed.",
            "search_plan": search_plan,
            "requires": {
                "internet": True,
                "credentials": True,
                "user_approval_before_search": True,
                "user_approval_before_download": True
            },
            "target_path": search_plan.get("target_path"),
            "project_path": project_path
        }

    def _prepare_url_dataset(self, project_path, options):
        url = options.get("url", "")

        if not url:
            return {
                "status": "waiting_for_user_input",
                "source": "url",
                "message": "Dataset URL is required.",
                "requires": {
                    "url_input": True,
                    "internet": True
                },
                "project_path": project_path
            }

        inspection = self.url_dataset_source.inspect(
            url
        )

        if inspection.get("status") != "planned":
            return {
                "status": "error",
                "source": "url",
                "error_code": inspection.get(
                    "error_code",
                    "URL_DATASET_INSPECTION_FAILED"
                ),
                "message": inspection.get(
                    "message",
                    "URL dataset inspection failed."
                ),
                "inspection": inspection,
                "project_path": project_path
            }

        return {
            "status": "planned",
            "source": "url",
            "message": "URL dataset source planned and validated. Download is not executed yet.",
            "inspection": inspection,
            "requires": {
                "internet": True,
                "user_approval_before_download": True
            },
            "target_path": f"{project_path}/data/raw",
            "project_path": project_path
        }

    def _prepare_skip_dataset(self, project_path):
        return {
            "status": "skipped",
            "source": "skip",
            "message": "Dataset selection skipped for now.",
            "project_path": project_path
        }

    def list_supported_sources(self):
        return self.supported_sources
