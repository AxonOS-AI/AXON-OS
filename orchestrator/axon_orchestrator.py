import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

AI_RUNTIME_DIR = os.path.join(BASE_DIR, "ai-runtime")
INTENT_DIR = os.path.join(AI_RUNTIME_DIR, "intent")
EXECUTION_DIR = os.path.join(BASE_DIR, "execution")

sys.path.append(AI_RUNTIME_DIR)
sys.path.append(INTENT_DIR)
sys.path.append(EXECUTION_DIR)

from inference_engine import InferenceEngine
from intent_parser import IntentParser
from prompts import build_intent_prompt
from task_manager import TaskManager


class AxonOrchestrator:
    def __init__(self):
        self.intent_engine = InferenceEngine()
        self.intent_parser = IntentParser()
        self.task_manager = TaskManager()

        self.intent_model_name = "tinyllama-intent"

    def initialize(self):
        print("[AXON Orchestrator] Starting AXON Runtime")

        initialized = self.intent_engine.initialize(
            self.intent_model_name
        )

        if initialized:
            print(
                f"[AXON Orchestrator] Intent model ready: {self.intent_model_name}"
            )
        else:
            print(
                "[AXON Orchestrator] Intent model failed, fallback parser will be used"
            )

        return initialized

    def process_request(self, user_input):
        print(
            f"[AXON Orchestrator] Processing request: {user_input}"
        )

        intent = self.detect_intent(user_input)

        print(
            f"[AXON Intent] Final Intent: {intent}"
        )

        response = self.route_intent(intent)

        return response

    def detect_intent(self, user_input):
        prompt = build_intent_prompt(user_input)

        llm_result = self.intent_engine.run_inference(prompt)

        if llm_result.get("status") == "success":
            raw_response = llm_result.get("response", "")

            intent = self.intent_parser.parse_llm_output(
                raw_response,
                raw_input=user_input
            )

            if intent.intent_name != "unknown":
                print("[AXON Intent] Intent detected by TinyLlama")
                return intent

        print("[AXON Intent] Falling back to rule-based parser")

        return self.intent_parser.parse(user_input)

    def route_intent(self, intent):
        workflow_map = {
            "train_model": "training_workflow",
            "search_query": "search_workflow",
            "open_application": "application_launcher",
            "analyze_data": "analysis_workflow",
            "generate_code": "code_generation_workflow"
        }

        workflow_name = workflow_map.get(
            intent.intent_name,
            "unknown_workflow"
        )

        if workflow_name == "unknown_workflow":
            return {
                "status": "unknown",
                "workflow": workflow_name,
                "message": "No suitable workflow found",
                "intent": intent.to_dict()
            }

        task = self.task_manager.create_task(
            name=workflow_name,
            payload={
                "intent": intent.to_dict(),
                "workflow": workflow_name
            }
        )

        completed_task = self.task_manager.run_next_task()

        return {
            "status": "executed",
            "workflow": workflow_name,
            "message": "Workflow task created and executed",
            "intent": intent.to_dict(),
            "task": completed_task
        }


if __name__ == "__main__":
    orchestrator = AxonOrchestrator()

    orchestrator.initialize()

    result = orchestrator.process_request(
        "Train a model to classify emails"
    )

    print(result)
