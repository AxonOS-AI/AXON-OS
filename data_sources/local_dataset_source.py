import os


class LocalDatasetSource:
    def __init__(self):
        self.supported_extensions = {
            ".csv",
            ".json",
            ".jsonl",
            ".txt",
            ".zip",
            ".parquet"
        }

    def inspect(self, dataset_path):
        if not dataset_path:
            return {
                "status": "error",
                "error_code": "LOCAL_DATASET_PATH_REQUIRED",
                "message": "Local dataset path is required."
            }

        expanded_path = os.path.expanduser(dataset_path)
        absolute_path = os.path.abspath(expanded_path)

        if not os.path.exists(absolute_path):
            return {
                "status": "error",
                "error_code": "LOCAL_DATASET_NOT_FOUND",
                "message": "Local dataset file was not found.",
                "path": absolute_path
            }

        if not os.path.isfile(absolute_path):
            return {
                "status": "error",
                "error_code": "LOCAL_DATASET_NOT_FILE",
                "message": "Local dataset path is not a file.",
                "path": absolute_path
            }

        file_size_bytes = os.path.getsize(absolute_path)
        file_extension = os.path.splitext(absolute_path)[1].lower()

        supported = file_extension in self.supported_extensions

        result = {
            "status": "ready" if supported else "unsupported",
            "source": "local_dataset",
            "path": absolute_path,
            "file_name": os.path.basename(absolute_path),
            "file_extension": file_extension,
            "file_size_bytes": file_size_bytes,
            "file_size_mb": round(file_size_bytes / (1024 * 1024), 2),
            "supported": supported,
            "supported_extensions": sorted(
                list(self.supported_extensions)
            )
        }

        if not supported:
            result["message"] = "Local dataset file extension is not currently supported."
            result["error_code"] = "UNSUPPORTED_LOCAL_DATASET_EXTENSION"
        else:
            result["message"] = "Local dataset file is ready for the next validation step."

        return result
