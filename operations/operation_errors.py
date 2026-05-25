class OperationErrors:
    @staticmethod
    def approval_required(operation_name, action_name):
        return {
            "status": "waiting_for_approval",
            "error_code": "APPROVAL_REQUIRED",
            "operation_name": operation_name,
            "action_name": action_name,
            "message": "This operation requires user approval before it can run.",
            "suggestion": "Ask the user for approval before continuing."
        }

    @staticmethod
    def approval_rejected(operation_name, action_name):
        return {
            "status": "cancelled",
            "error_code": "APPROVAL_REJECTED",
            "operation_name": operation_name,
            "action_name": action_name,
            "message": "The user rejected this operation.",
            "suggestion": "Do not run this operation unless the user approves it later."
        }

    @staticmethod
    def operation_failed(operation_name, reason="", suggestion=""):
        return {
            "status": "failed",
            "error_code": "OPERATION_FAILED",
            "operation_name": operation_name,
            "message": "The operation failed.",
            "reason": reason,
            "suggestion": suggestion
        }

    @staticmethod
    def operation_cancelled(operation_name, reason=""):
        return {
            "status": "cancelled",
            "error_code": "OPERATION_CANCELLED",
            "operation_name": operation_name,
            "message": "The operation was cancelled.",
            "reason": reason
        }

    @staticmethod
    def operation_timeout(operation_name, timeout_seconds=None):
        return {
            "status": "failed",
            "error_code": "OPERATION_TIMEOUT",
            "operation_name": operation_name,
            "message": "The operation timed out.",
            "timeout_seconds": timeout_seconds,
            "suggestion": "Retry the operation or increase the timeout limit."
        }

    @staticmethod
    def network_error(operation_name, reason=""):
        return {
            "status": "failed",
            "error_code": "NETWORK_ERROR",
            "operation_name": operation_name,
            "message": "A network error occurred during the operation.",
            "reason": reason,
            "suggestion": "Check the internet connection and retry."
        }

    @staticmethod
    def insufficient_disk_space(operation_name, required_space_mb=None, available_space_mb=None):
        return {
            "status": "failed",
            "error_code": "INSUFFICIENT_DISK_SPACE",
            "operation_name": operation_name,
            "message": "There is not enough disk space to complete this operation.",
            "required_space_mb": required_space_mb,
            "available_space_mb": available_space_mb,
            "suggestion": "Free disk space or choose another storage location."
        }
