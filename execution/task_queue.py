class TaskQueue:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

        print(
            f"[AXON Queue] Task added: {task}"
        )

    def get_next_task(self):
        if not self.tasks:
            print(
                "[AXON Queue] No tasks available"
            )
            return None

        task = self.tasks.pop(0)

        print(
            f"[AXON Queue] Dispatching task: {task}"
        )

        return task

    def get_queue_size(self):
        return len(self.tasks)

    def list_tasks(self):
        return self.tasks
