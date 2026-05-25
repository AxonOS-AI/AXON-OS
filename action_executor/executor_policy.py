class ExecutorPolicy:
    def __init__(self):
        self.action_policies = {
            "search_internet": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Internet search execution is not enabled yet."
            },
            "download_dataset": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Dataset download execution is not enabled yet."
            },
            "download_model": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Model download execution is not enabled yet."
            },
            "run_training": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Training execution is not enabled yet."
            },
            "process_dataset": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Dataset processing execution is not enabled yet."
            },
            "access_local_file": {
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Local file execution is not enabled yet."
            },
            "prepare_plan": {
                "execution_enabled": True,
                "requires_ready_state": False,
                "requires_approval": False,
                "safe_mode_only": True,
                "reason": "Plan preparation is safe and does not execute external or destructive operations."
            }
        }

    def get_policy(self, action_name):
        policy = self.action_policies.get(action_name)

        if policy is None:
            return {
                "status": "unknown_action",
                "action_name": action_name,
                "execution_enabled": False,
                "requires_ready_state": True,
                "requires_approval": True,
                "safe_mode_only": True,
                "reason": "Unknown actions are blocked by default."
            }

        return {
            "status": "known_action",
            "action_name": action_name,
            **policy
        }

    def is_execution_enabled(self, action_name):
        policy = self.get_policy(action_name)
        return policy.get("execution_enabled", False)

    def list_policies(self):
        return self.action_policies
