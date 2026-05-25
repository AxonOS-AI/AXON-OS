class PackageMapper:
    def __init__(self):
        self.package_map = {
            "kaggle": {
                "install_type": "python_package",
                "package_name": "kaggle",
                "install_command": "python3 -m pip install kaggle",
                "purpose": "Enable Kaggle CLI access for dataset search and download.",
                "risk_note": "Requires user approval and Kaggle credentials before use."
            },
            "peft": {
                "install_type": "python_package",
                "package_name": "peft",
                "install_command": "python3 -m pip install peft",
                "purpose": "Enable parameter-efficient fine-tuning workflows such as LoRA.",
                "risk_note": "May install additional machine learning dependencies."
            },
            "trl": {
                "install_type": "python_package",
                "package_name": "trl",
                "install_command": "python3 -m pip install trl",
                "purpose": "Enable supervised fine-tuning and reinforcement learning training utilities.",
                "risk_note": "May install additional training dependencies."
            },
            "bitsandbytes": {
                "install_type": "gpu_package",
                "package_name": "bitsandbytes",
                "install_command": "python3 -m pip install bitsandbytes",
                "purpose": "Enable 8-bit and 4-bit model quantization when supported.",
                "risk_note": "GPU compatibility depends on the user's hardware, CUDA, and platform."
            },
            "sentencepiece": {
                "install_type": "python_package",
                "package_name": "sentencepiece",
                "install_command": "python3 -m pip install sentencepiece",
                "purpose": "Enable tokenizer support for models that require SentencePiece.",
                "risk_note": "Usually safe, but still requires approval before installation."
            },
            "opencv-python": {
                "install_type": "python_package",
                "package_name": "opencv-python",
                "install_command": "python3 -m pip install opencv-python",
                "purpose": "Enable computer vision dataset loading and image processing.",
                "risk_note": "May install large binary wheels."
            },
            "jupyterlab": {
                "install_type": "python_package",
                "package_name": "jupyterlab",
                "install_command": "python3 -m pip install jupyterlab",
                "purpose": "Enable notebook-based experimentation and local AI lab workflows.",
                "risk_note": "May install many dependencies and expose a local web interface."
            },
            "nvidia-smi": {
                "install_type": "system_package",
                "package_name": "nvidia-smi",
                "install_command": None,
                "purpose": "Detect NVIDIA GPU driver status and GPU runtime information.",
                "risk_note": "Do not auto-install GPU drivers. Driver installation must be handled carefully per user device."
            }
        }

    def map_item(self, item_name):
        item = self.package_map.get(item_name)

        if item is None:
            return {
                "status": "unknown",
                "item_name": item_name,
                "install_type": "unknown",
                "package_name": item_name,
                "install_command": None,
                "purpose": "Unknown item. Manual review is required.",
                "risk_note": "Unknown packages must not be installed automatically."
            }

        return {
            "status": "mapped",
            "item_name": item_name,
            **item
        }

    def map_items(self, item_names):
        return [
            self.map_item(item_name)
            for item_name in item_names
        ]

    def list_known_items(self):
        return list(self.package_map.keys())
