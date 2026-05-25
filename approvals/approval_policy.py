class ApprovalPolicy:
    def __init__(self):
        self.action_policies = {
            "prepare_plan": {
                "requires_approval": False,
                "requires_progress": False,
                "progress_type": "none",
                "can_be_cancelled": False,
                "risk_level": "low",
                "reason": "This action only prepares an execution plan and does not perform external, destructive, or resource-heavy operations."
            },
            "access_local_file": {
                "requires_approval": True,
                "requires_progress": False,
                "progress_type": "none",
                "can_be_cancelled": True,
                "risk_level": "medium",
                "reason": "This action accesses a local file selected by the user."
            },
            "search_internet": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "network_search",
                "can_be_cancelled": True,
                "risk_level": "medium",
                "reason": "This action may use the internet to search for external resources."
            },
            "download_dataset": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "download",
                "can_be_cancelled": True,
                "risk_level": "medium",
                "reason": "This action downloads external dataset files to the device."
            },
            "download_model": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "download",
                "can_be_cancelled": True,
                "risk_level": "high",
                "reason": "This action downloads model files and may consume disk space and bandwidth."
            },
            "use_credentials": {
                "requires_approval": True,
                "requires_progress": False,
                "progress_type": "none",
                "can_be_cancelled": True,
                "risk_level": "high",
                "reason": "This action may use a configured credential. Secret values must never be exposed."
            },
            "install_packages": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "installation",
                "can_be_cancelled": True,
                "risk_level": "high",
                "reason": "This action installs software packages or dependencies on the device."
            },
            "process_dataset": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "data_processing",
                "can_be_cancelled": True,
                "risk_level": "medium",
                "reason": "This action processes dataset files and may consume CPU, memory, and disk resources."
            },
            "run_training": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "training",
                "can_be_cancelled": True,
                "risk_level": "high",
                "reason": "This action may consume CPU, GPU, memory, disk space, and time."
            },
            "save_model": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "file_write",
                "can_be_cancelled": False,
                "risk_level": "medium",
                "reason": "This action writes model files to disk."
            },
            "send_report": {
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "upload",
                "can_be_cancelled": True,
                "risk_level": "high",
                "reason": "This action may send a safe report outside this device."
            }
        }

    def get_action_policy(self, action_name):
        policy = self.action_policies.get(action_name)

        if policy is None and str(action_name).startswith("install_"):
            install_policy = self.action_policies.get("install_packages", {})

            return {
                "status": "known_dynamic_action",
                "action_name": action_name,
                "base_action": "install_packages",
                **install_policy
            }

        if policy is None:
            return {
                "status": "unknown_action",
                "action_name": action_name,
                "requires_approval": True,
                "requires_progress": True,
                "progress_type": "unknown",
                "can_be_cancelled": True,
                "risk_level": "unknown",
                "reason": "Unknown actions require approval and progress tracking by default."
            }

        return {
            "status": "known_action",
            "action_name": action_name,
            **policy
        }

    def requires_approval(self, action_name):
        policy = self.get_action_policy(action_name)
        return policy.get("requires_approval", True)

    def requires_progress(self, action_name):
        policy = self.get_action_policy(action_name)
        return policy.get("requires_progress", True)

    def list_policies(self):
        return self.action_policies
