import sys
import os

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

WORKSPACE_DIR = os.path.join(BASE_DIR, "workspace")
EXECUTION_CONTROL_DIR = os.path.join(BASE_DIR, "execution_control")
DATA_SOURCES_DIR = os.path.join(BASE_DIR, "data_sources")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
APPROVALS_DIR = os.path.join(BASE_DIR, "approvals")
OPERATIONS_DIR = os.path.join(BASE_DIR, "operations")

if WORKSPACE_DIR not in sys.path:
    sys.path.append(WORKSPACE_DIR)

if EXECUTION_CONTROL_DIR not in sys.path:
    sys.path.append(EXECUTION_CONTROL_DIR)

if DATA_SOURCES_DIR not in sys.path:
    sys.path.append(DATA_SOURCES_DIR)

if REPORTS_DIR not in sys.path:
    sys.path.append(REPORTS_DIR)

if APPROVALS_DIR not in sys.path:
    sys.path.append(APPROVALS_DIR)

if OPERATIONS_DIR not in sys.path:
    sys.path.append(OPERATIONS_DIR)

from project_workspace import ProjectWorkspace
from execution_tracer import ExecutionTracer
from progress_tracker import ProgressTracker
from decision_gate import DecisionGate
from error_reporter import ErrorReporter
from dataset_manager import DatasetManager
from report_builder import ReportBuilder
from approval_gate import ApprovalGate
from operation_progress import OperationProgress


def run(task):
    workspace_manager = ProjectWorkspace()

    payload = task.get("payload", {})
    intent = payload.get("intent", {})

    dataset_selection = payload.get(
        "dataset_selection",
        {}
    )

    approval_decisions = payload.get(
        "approval_decisions",
        {}
    )

    raw_input = intent.get("raw_input", "")
    domain = intent.get("domain", "unknown")
    action = intent.get("action", "unknown")

    project = workspace_manager.create_workspace(
        workflow_name="training_workflow",
        task=task,
        intent=intent
    )

    project_path = project["project_path"]

    tracer = ExecutionTracer(project_path)
    progress = ProgressTracker(project_path)
    decision_gate = DecisionGate(project_path)
    error_reporter = ErrorReporter(project_path)
    dataset_manager = DatasetManager()
    approval_gate = ApprovalGate(project_path)
    operation_progress = OperationProgress(project_path)

    total_steps = 10

    try:
        progress.mark_started(
            total_steps=total_steps,
            message="Training workflow started"
        )

        tracer.log_info(
            "workflow_started",
            "Training workflow started",
            {
                "workflow": "training_workflow",
                "project_path": project_path
            }
        )

        progress.mark_running(
            current_step=1,
            total_steps=total_steps,
            message="Project workspace created"
        )

        tracer.log_success(
            "workspace_created",
            "Project workspace created successfully",
            {
                "project": project
            }
        )

        plan_approval = approval_gate.request_approval(
            action_name="prepare_plan",
            context={
                "workflow": "training_workflow",
                "project_path": project_path
            }
        )

        progress.mark_running(
            current_step=2,
            total_steps=total_steps,
            message="Plan approval policy evaluated",
            details={
                "approval_status": plan_approval.get("status")
            }
        )

        tracer.log_info(
            "plan_approval_evaluated",
            "Plan approval policy evaluated",
            {
                "approval": plan_approval
            }
        )

        dataset_options = decision_gate.build_dataset_source_options()

        selected_dataset_option = dataset_selection.get(
            "source",
            "skip"
        )

        dataset_source_options = dataset_selection.get(
            "options",
            {}
        )

        decision_gate.record_decision(
            step_name="dataset_source_selection",
            question="Choose dataset source",
            options=dataset_options,
            selected_option=selected_dataset_option,
            reason="Dataset source selected from task payload or safe default.",
            details={
                "requires_user_interaction": selected_dataset_option == "skip",
                "current_mode": "planning",
                "dataset_source_options": dataset_source_options
            }
        )

        progress.mark_running(
            current_step=3,
            total_steps=total_steps,
            message="Dataset source decision prepared",
            details={
                "selected_option": selected_dataset_option
            }
        )

        tracer.log_info(
            "dataset_decision_prepared",
            "Dataset source options prepared",
            {
                "selected_option": selected_dataset_option,
                "dataset_source_options": dataset_source_options
            }
        )

        approval_results = {
            "prepare_plan": plan_approval
        }

        if selected_dataset_option == "kaggle":
            search_approval = approval_gate.request_approval(
                action_name="search_internet",
                question=(
                    "AXON needs your approval before searching Kaggle for datasets. "
                    "This may use the internet and configured Kaggle credentials. "
                    "No dataset will be downloaded at this step. Do you approve?"
                ),
                context={
                    "source": "kaggle",
                    "query": dataset_source_options.get("query", ""),
                    "no_download_executed": True
                },
                user_decision=approval_decisions.get("search_internet"),
                reason="User decision for Kaggle dataset search."
            )

            download_approval = approval_gate.request_approval(
                action_name="download_dataset",
                question=(
                    "AXON needs your approval before downloading any dataset to this device. "
                    "No download is executed during the planning stage. Do you approve?"
                ),
                context={
                    "source": "kaggle",
                    "target_path": os.path.join(project_path, "data", "kaggle"),
                    "planning_only": True
                },
                user_decision=approval_decisions.get("download_dataset"),
                reason="User decision for future dataset download."
            )

            approval_results["search_internet"] = search_approval
            approval_results["download_dataset"] = download_approval

        elif selected_dataset_option == "url":
            download_approval = approval_gate.request_approval(
                action_name="download_dataset",
                question=(
                    "AXON needs your approval before downloading a dataset from the provided URL. "
                    "No download is executed during the planning stage. Do you approve?"
                ),
                context={
                    "source": "url",
                    "url": dataset_source_options.get("url", ""),
                    "target_path": os.path.join(project_path, "data", "raw"),
                    "planning_only": True
                },
                user_decision=approval_decisions.get("download_dataset"),
                reason="User decision for future URL dataset download."
            )

            approval_results["download_dataset"] = download_approval

        elif selected_dataset_option == "local_dataset":
            local_file_approval = approval_gate.request_approval(
                action_name="access_local_file",
                question=(
                    "AXON needs your approval before accessing the selected local dataset file. "
                    "Only file metadata will be inspected at this planning stage. Do you approve?"
                ),
                context={
                    "source": "local_dataset",
                    "local_path": dataset_source_options.get("local_path", ""),
                    "metadata_only": True
                },
                user_decision=approval_decisions.get("access_local_file"),
                reason="User decision for local dataset file access."
            )

            approval_results["access_local_file"] = local_file_approval

        progress.mark_running(
            current_step=4,
            total_steps=total_steps,
            message="Approval gates evaluated",
            details={
                "approval_actions": list(approval_results.keys())
            }
        )

        tracer.log_info(
            "approval_gates_evaluated",
            "Approval gates evaluated",
            {
                "approval_results": approval_results
            }
        )

        operation_progress_records = {}

        for operation_name, approval in approval_results.items():
            if not approval.get("requires_progress"):
                continue

            progress_type = approval.get(
                "progress_type",
                "generic"
            )

            can_be_cancelled = approval.get(
                "can_be_cancelled",
                True
            )

            if approval.get("approved"):
                operation_progress_records[operation_name] = operation_progress.start(
                    operation_name=operation_name,
                    progress_type=progress_type,
                    message="Operation is approved and ready to run.",
                    can_be_cancelled=can_be_cancelled,
                    details={
                        "approval_status": approval.get("status"),
                        "planning_only": True,
                        "will_execute_now": False
                    }
                )
            else:
                operation_progress.start(
                    operation_name=operation_name,
                    progress_type=progress_type,
                    message="Operation is waiting for user approval.",
                    can_be_cancelled=can_be_cancelled,
                    details={
                        "approval_status": approval.get("status"),
                        "planning_only": True,
                        "will_execute_now": False
                    }
                )

                operation_progress_records[operation_name] = operation_progress.mark_waiting_for_approval(
                    operation_name=operation_name,
                    message="Operation is waiting for user approval.",
                    details={
                        "approval_status": approval.get("status"),
                        "risk_level": approval.get("risk_level"),
                        "planning_only": True,
                        "will_execute_now": False
                    }
                )

        progress.mark_running(
            current_step=5,
            total_steps=total_steps,
            message="Operation progress records prepared",
            details={
                "operations": list(operation_progress_records.keys())
            }
        )

        tracer.log_info(
            "operation_progress_prepared",
            "Operation progress records prepared",
            {
                "operation_progress": operation_progress_records
            }
        )

        dataset_plan = dataset_manager.prepare_dataset_source(
            selected_source=selected_dataset_option,
            project_path=project_path,
            options=dataset_source_options
        )

        progress.mark_running(
            current_step=6,
            total_steps=total_steps,
            message="Dataset manager prepared selected source",
            details={
                "dataset_plan_status": dataset_plan.get("status"),
                "dataset_source": dataset_plan.get("source")
            }
        )

        tracer.log_info(
            "dataset_manager_prepared",
            "Dataset manager prepared selected source",
            {
                "dataset_plan": dataset_plan
            }
        )

        kaggle_path = os.path.join(
            project_path,
            "data",
            "kaggle"
        )

        progress.mark_running(
            current_step=7,
            total_steps=total_steps,
            message="Kaggle dataset directory prepared",
            details={
                "kaggle_path": kaggle_path
            }
        )

        tracer.log_success(
            "kaggle_directory_ready",
            "Kaggle dataset directory is ready",
            {
                "path": kaggle_path
            }
        )

        steps = [
            "Receive training request",
            "Create project workspace",
            "Evaluate plan approval policy",
            "Prepare dataset decision gate",
            "Evaluate approval gates",
            "Prepare operation progress records",
            "Prepare dataset source with DatasetManager",
            "Prepare Kaggle dataset directory",
            "Return training execution plan",
            "Generate final execution reports"
        ]

        progress.mark_running(
            current_step=8,
            total_steps=total_steps,
            message="Training execution plan prepared"
        )

        reports_dir = os.path.join(
            project_path,
            "reports"
        )

        reports = {
            "execution_summary": os.path.join(
                reports_dir,
                "execution_summary.json"
            ),
            "markdown_report": os.path.join(
                reports_dir,
                "final_report.md"
            )
        }

        result = {
            "workflow": "training_workflow",
            "status": "prepared",
            "message": "Training workflow prepared successfully",
            "input": raw_input,
            "domain": domain,
            "action": action,
            "project": project,
            "dataset_source": {
                "provider": "decision_gate",
                "status": "prepared_by_dataset_manager",
                "selected_option": selected_dataset_option,
                "dataset_options": dataset_source_options,
                "dataset_plan": dataset_plan,
                "kaggle_path": kaggle_path
            },
            "approvals": approval_results,
            "operation_progress": operation_progress_records,
            "reports": reports,
            "steps": steps
        }

        workspace_manager.save_workflow_result(
            project_path,
            result
        )

        progress.mark_running(
            current_step=9,
            total_steps=total_steps,
            message="Preparing final execution reports",
            details={
                "reports": reports
            }
        )

        tracer.log_info(
            "final_reports_prepared",
            "Final report generation prepared",
            {
                "reports": reports
            }
        )

        progress.mark_completed(
            total_steps=total_steps,
            message="Training workflow completed"
        )

        tracer.log_success(
            "workflow_completed",
            "Training workflow completed successfully",
            {
                "status": "prepared"
            }
        )

        report_builder = ReportBuilder(
            project_path
        )

        report_builder.build_execution_summary()

        return result

    except Exception as error:
        error_event = error_reporter.report_exception(
            module="training_workflow",
            exception=error,
            suggestion="Review the training workflow logs and retry the operation."
        )

        tracer.log_error(
            "workflow_failed",
            "Training workflow failed",
            {
                "error": error_event
            }
        )

        progress.mark_failed(
            current_step=0,
            total_steps=total_steps,
            message="Training workflow failed",
            details={
                "error_code": error_event.get("error_code")
            }
        )

        return {
            "workflow": "training_workflow",
            "status": "error",
            "message": str(error),
            "project": project,
            "error": error_event
        }
