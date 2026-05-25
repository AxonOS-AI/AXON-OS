import uuid

from task_queue import TaskQueue
from worker_pool import WorkerPool


class TaskManager:
    def __init__(self):
        self.queue = TaskQueue()
        self.worker_pool = WorkerPool()

        self.tasks = {}

        self.worker_pool.register_worker(
            "default-worker"
        )

    def create_task(self, name, payload=None):
        task_id = str(uuid.uuid4())

        task = {
            "id": task_id,
            "name": name,
            "payload": payload or {},
            "status": "created",
            "result": None
        }

        self.tasks[task_id] = task

        self.queue.add_task(task)

        print(
            f"[AXON TaskManager] Created task: {task_id}"
        )

        return task

    def run_next_task(self):
        task = self.queue.get_next_task()

        if task is None:
            return None

        completed_task = self.worker_pool.execute_task(
            task
        )

        return completed_task

    def get_task(self, task_id):
        return self.tasks.get(task_id)

    def list_tasks(self):
        return self.tasks
