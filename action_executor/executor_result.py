class ExecutorResult:
    @staticmethod
    def ready(action_name, message="Action is ready for execution.", details=None):
        return {
            "status": "ready",
            "action_name": action_name,
            "can_execute": True,
            "executed": False,
            "message": message,
            "details": details or {}
        }

    @staticmethod
    def blocked(action_name, message="Action execution is blocked.", reason="", details=None):
        return {
            "status": "blocked",
            "action_name": action_name,
            "can_execute": False,
            "executed": False,
            "message": message,
            "reason": reason,
            "details": details or {}
        }

    @staticmethod
    def execution_not_enabled(action_name, policy=None):
        return {
            "status": "execution_not_enabled",
            "action_name": action_name,
            "can_execute": False,
            "executed": False,
            "message": "Execution is not enabled for this action.",
            "policy": policy or {}
        }

    @staticmethod
    def execution_not_implemented_yet(action_name, policy=None, details=None):
        return {
            "status": "execution_not_implemented_yet",
            "action_name": action_name,
            "can_execute": False,
            "executed": False,
            "message": "Execution logic is not implemented yet for this action.",
            "policy": policy or {},
            "details": details or {}
        }

    @staticmethod
    def completed(action_name, message="Action executed successfully.", details=None):
        return {
            "status": "completed",
            "action_name": action_name,
            "can_execute": True,
            "executed": True,
            "message": message,
            "details": details or {}
        }

    @staticmethod
    def failed(action_name, message="Action execution failed.", error=None, details=None):
        final_details = details or {}

        if error is not None:
            final_details["error"] = error

        return {
            "status": "failed",
            "action_name": action_name,
            "can_execute": False,
            "executed": False,
            "message": message,
            "details": final_details
        }
