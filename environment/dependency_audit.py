import importlib.util
import importlib.metadata


class DependencyAudit:
    def __init__(self):
        self.default_packages = {
            "torch": "torch",
            "transformers": "transformers",
            "datasets": "datasets",
            "accelerate": "accelerate",
            "peft": "peft",
            "trl": "trl",
            "bitsandbytes": "bitsandbytes",
            "sentencepiece": "sentencepiece",
            "tokenizers": "tokenizers",
            "safetensors": "safetensors",
            "numpy": "numpy",
            "pandas": "pandas",
            "scikit-learn": "sklearn",
            "opencv-python": "cv2",
            "Pillow": "PIL",
            "matplotlib": "matplotlib",
            "jupyterlab": "jupyterlab"
        }

    def check_package(self, package_name, import_name=None):
        import_name = import_name or package_name

        spec = importlib.util.find_spec(import_name)

        result = {
            "package": package_name,
            "import_name": import_name,
            "available": spec is not None,
            "version": None,
            "error": None
        }

        if spec is None:
            result["error"] = "Package import was not found."
            return result

        try:
            result["version"] = importlib.metadata.version(package_name)
        except Exception:
            result["version"] = "unknown"

        return result

    def audit_packages(self, packages=None):
        packages = packages or self.default_packages

        results = []

        for package_name, import_name in packages.items():
            results.append(
                self.check_package(
                    package_name=package_name,
                    import_name=import_name
                )
            )

        available_count = sum(
            1 for item in results if item.get("available")
        )

        missing = [
            item.get("package")
            for item in results
            if not item.get("available")
        ]

        return {
            "status": "completed",
            "total_packages": len(results),
            "available_count": available_count,
            "missing_count": len(missing),
            "missing_packages": missing,
            "packages": results
        }
