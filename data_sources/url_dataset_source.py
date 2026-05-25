from urllib.parse import urlparse
import os


class UrlDatasetSource:
    def __init__(self):
        self.supported_extensions = {
            ".csv",
            ".json",
            ".jsonl",
            ".txt",
            ".zip",
            ".parquet"
        }

    def inspect(self, dataset_url):
        if not dataset_url:
            return {
                "status": "error",
                "error_code": "DATASET_URL_REQUIRED",
                "message": "Dataset URL is required."
            }

        parsed_url = urlparse(dataset_url)

        if parsed_url.scheme not in ["http", "https"]:
            return {
                "status": "error",
                "error_code": "INVALID_DATASET_URL_SCHEME",
                "message": "Dataset URL must start with http or https.",
                "url": dataset_url
            }

        if not parsed_url.netloc:
            return {
                "status": "error",
                "error_code": "INVALID_DATASET_URL_HOST",
                "message": "Dataset URL host is missing.",
                "url": dataset_url
            }

        file_name = os.path.basename(parsed_url.path)
        file_extension = os.path.splitext(file_name)[1].lower()

        supported = file_extension in self.supported_extensions

        result = {
            "status": "planned" if supported else "unsupported",
            "source": "url",
            "url": dataset_url,
            "host": parsed_url.netloc,
            "file_name": file_name,
            "file_extension": file_extension,
            "supported": supported,
            "supported_extensions": sorted(
                list(self.supported_extensions)
            ),
            "requires": {
                "internet": True,
                "user_approval_before_download": True
            }
        }

        if not file_name:
            result["status"] = "warning"
            result["message"] = "URL does not include a clear file name. AXON may need to inspect headers later."
            result["error_code"] = "URL_FILE_NAME_UNKNOWN"
            return result

        if not supported:
            result["message"] = "URL dataset file extension is not currently supported."
            result["error_code"] = "UNSUPPORTED_URL_DATASET_EXTENSION"
        else:
            result["message"] = "URL dataset source is valid and ready for a future download step."

        return result
