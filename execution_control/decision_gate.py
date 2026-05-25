import json
from datetime import datetime


class DecisionGate:
    def __init__(self, project_path):
        self.project_path = project_path
        self.decision_file = f"{project_path}/decision_log.jsonl"

    def record_decision(
        self,
        step_name,
        question,
        options,
        selected_option,
        reason="",
        details=None
    ):
        decision_event = {
            "timestamp": self._timestamp(),
            "step_name": step_name,
            "question": question,
            "options": options,
            "selected_option": selected_option,
            "reason": reason,
            "details": details or {}
        }

        self._write_decision(decision_event)

        return decision_event

    def build_dataset_source_options(self):
        return [
            {
                "id": "local_dataset",
                "label": "Use local dataset from this device",
                "requires_internet": False
            },
            {
                "id": "kaggle",
                "label": "Search and download dataset from Kaggle",
                "requires_internet": True
            },
            {
                "id": "url",
                "label": "Use dataset from a direct URL",
                "requires_internet": True
            },
            {
                "id": "skip",
                "label": "Skip dataset selection for now",
                "requires_internet": False
            }
        ]

    def build_model_source_options(self):
        return [
            {
                "id": "auto_select",
                "label": "Let AXON suggest a suitable model",
                "requires_internet": False
            },
            {
                "id": "local_model",
                "label": "Use a local model from this device",
                "requires_internet": False
            },
            {
                "id": "huggingface",
                "label": "Download model from Hugging Face",
                "requires_internet": True
            },
            {
                "id": "skip",
                "label": "Skip model selection for now",
                "requires_internet": False
            }
        ]

    def _write_decision(self, decision_event):
        with open(self.decision_file, "a", encoding="utf-8") as file:
            file.write(
                json.dumps(
                    decision_event,
                    ensure_ascii=False
                ) + "\n"
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
