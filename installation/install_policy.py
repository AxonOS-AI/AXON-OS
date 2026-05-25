class InstallPolicy:
    def __init__(self):
        self.install_types = {
            "python_package": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "risk_level": "medium",
                "execution_enabled": False,
                "reason": "Python package installation changes the project environment and must be approved."
            },
            "system_package": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "risk_level": "high",
                "execution_enabled": False,
                "reason": "System package installation changes the operating system and must be approved."
            },
            "gpu_package": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "risk_level": "high",
                "execution_enabled": False,
                "reason": "GPU-related installation may affect CUDA, drivers, and training behavior."
            },
            "cli_tool": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "risk_level": "medium",
                "execution_enabled": False,
                "reason": "CLI tool installation may change available commands and must be approved."
            },
            "unknown": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "risk_level": "unknown",
                "execution_enabled": False,
                "reason": "Unknown installation types are blocked by default until reviewed."
            }
        }

    def get_policy(self, install_type):
        policy = self.install_types.get(install_type)

        if policy is None:
            policy = self.install_types["unknown"]

            return {
                "status": "unknown_install_type",
                "install_type": install_type,
                **policy
            }

        return {
            "status": "known_install_type",
            "install_type": install_type,
            **policy
        }

    def requires_approval(self, install_type):
        policy = self.get_policy(install_type)
        return policy.get("requires_approval", True)

    def is_execution_enabled(self, install_type):
        policy = self.get_policy(install_type)
        return policy.get("execution_enabled", False)

    def list_policies(self):
        return self.install_types
