class ActionState:
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    READY_TO_RUN = "ready_to_run"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @staticmethod
    def list_states():
        return [
            ActionState.WAITING_FOR_APPROVAL,
            ActionState.APPROVED,
            ActionState.REJECTED,
            ActionState.READY_TO_RUN,
            ActionState.RUNNING,
            ActionState.COMPLETED,
            ActionState.FAILED,
            ActionState.CANCELLED
        ]

    @staticmethod
    def is_valid(state):
        return state in ActionState.list_states()

    @staticmethod
    def is_terminal(state):
        return state in [
            ActionState.REJECTED,
            ActionState.COMPLETED,
            ActionState.FAILED,
            ActionState.CANCELLED
        ]

    @staticmethod
    def normalize(state):
        state = str(state).strip().lower()

        if ActionState.is_valid(state):
            return state

        return ActionState.FAILED
