class OperationStatus:
    PENDING = "pending"
    WAITING_FOR_APPROVAL = "waiting_for_approval"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SKIPPED = "skipped"

    @staticmethod
    def list_statuses():
        return [
            OperationStatus.PENDING,
            OperationStatus.WAITING_FOR_APPROVAL,
            OperationStatus.RUNNING,
            OperationStatus.PAUSED,
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
            OperationStatus.SKIPPED
        ]

    @staticmethod
    def is_valid(status):
        return status in OperationStatus.list_statuses()

    @staticmethod
    def is_terminal(status):
        return status in [
            OperationStatus.COMPLETED,
            OperationStatus.FAILED,
            OperationStatus.CANCELLED,
            OperationStatus.SKIPPED
        ]

    @staticmethod
    def normalize(status):
        status = str(status).strip().lower()

        if OperationStatus.is_valid(status):
            return status

        return OperationStatus.FAILED
