import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

CREDENTIALS_DIR = os.path.join(BASE_DIR, "credentials")

if CREDENTIALS_DIR not in sys.path:
    sys.path.append(CREDENTIALS_DIR)

from kaggle_credentials import KaggleCredentials


class KaggleSource:
    def __init__(self):
        self.credentials = KaggleCredentials()

    def inspect_credentials(self, credentials_path=None):
        return self.credentials.inspect(
            credentials_path=credentials_path
        )

    def prepare_search_plan(self, query, project_path):
        credentials_status = self.inspect_credentials()

        return {
            "status": "planned",
            "source": "kaggle",
            "query": query,
            "credentials": credentials_status,
            "target_path": os.path.join(
                project_path,
                "data",
                "kaggle"
            ),
            "requires": {
                "internet": True,
                "credentials": True,
                "user_approval_before_search": True,
                "user_approval_before_download": True
            },
            "security": {
                "credentials_managed_by": "CredentialManager",
                "secret_content_read": False,
                "secret_content_stored": False,
                "no_download_executed": True,
                "no_internet_request_executed": True
            },
            "message": "Kaggle search plan prepared through Secure Access Manager. No internet request or download has been executed yet."
        }
