from action_state import ActionState


class ActionResult:
    @staticmethod
    def approved(action_name, operation_name=None, message="Action approved and ready to run.", details=None):
        return {
            "status": ActionState.READY_TO_RUN,
            "action_name": action_name,
            "operation_name": operation_name or action_name,
            "approved": True,
            "message": message,
            "details": details or {}
        }

    @staticmethod
    def rejected(action_name, operation_name=None, message="Action rejected by user.", details=None):
        return {
            "status": ActionState.REJECTED,
            "action_name": action_name,
            "operation_name": operation_name or action_name,
            "approved": False,
            "message": message,
            "details": details or {}
        }

    @staticmethod
    def waiting_for_approval(action_name, operation_name=None, message="Action is waiting for user approval.", details=None):
        return {
            "status": ActionState.WAITING_FOR_APPROVAL,
            "action_name": action_name,
            "operation_name": operation_name or action_name,
            "approved": False,
            "message": message,
            "details": details or {}
        }

    @staticmethod
    def failed(action_name, operation_name=None, message="Action handling failed.", error=None, details=None):
        final_details = details or {}

        if error is not None:
            final_details["error"] = error

        return {
            "status": ActionState.FAILED,
            "action_name": action_name,
            "operation_name": operation_name or action_name,
            "approved": False,
            "message": message,
            "details": final_details
        }

    @staticmethod
    def completed(action_name, operation_name=None, message="Action completed.", details=None):
        return {
            "status": ActionState.COMPLETED,
            "action_name": action_name,
            "operation_name": operation_name or action_name,
            "approved": True,
            "message": message,
            "details": details or {}
        }
