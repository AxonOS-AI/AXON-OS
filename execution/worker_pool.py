import sys
import os


BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")

if WORKFLOWS_DIR not in sys.path:
    sys.path.append(WORKFLOWS_DIR)


class WorkerPool:
    def __init__(self):
        self.workers = []

    def register_worker(self, worker_name):
        worker = {
            "name": worker_name,
            "status": "idle"
        }

        self.workers.append(worker)

        print(
            f"[AXON WorkerPool] Registered worker: {worker_name}"
        )

        return worker

    def execute_task(self, task):
        if task is None:
            print("[AXON WorkerPool] No task received")
            return None

        print(
            f"[AXON WorkerPool] Executing task: {task['name']}"
        )

        task["status"] = "running"

        workflow_result = self._run_workflow(task)

        task["result"] = workflow_result

        if workflow_result.get("status") == "error":
            task["status"] = "failed"
        else:
            task["status"] = "completed"

        print(
            f"[AXON WorkerPool] Task finished: {task['id']}"
        )

        return task

    def _run_workflow(self, task):
        workflow_name = task.get("name", "")

        workflow_handlers = {
            "training_workflow": self._run_training_workflow,
            "search_workflow": self._run_search_workflow,
            "application_launcher": self._run_application_launcher,
            "analysis_workflow": self._run_analysis_workflow,
            "code_generation_workflow": self._run_code_generation_workflow
        }

        handler = workflow_handlers.get(workflow_name)

        if handler is None:
            return {
                "workflow": workflow_name,
                "status": "unsupported",
                "message": f"No workflow handler found for: {workflow_name}"
            }

        try:
            return handler(task)
        except Exception as error:
            return {
                "workflow": workflow_name,
                "status": "error",
                "message": str(error)
            }

    def _run_training_workflow(self, task):
        from training_workflow import run
        return run(task)

    def _run_search_workflow(self, task):
        from search_workflow import run
        return run(task)

    def _run_application_launcher(self, task):
        from application_launcher import run
        return run(task)

    def _run_analysis_workflow(self, task):
        from analysis_workflow import run
        return run(task)

    def _run_code_generation_workflow(self, task):
        from code_generation_workflow import run
        return run(task)

    def list_workers(self):
        return self.workers
