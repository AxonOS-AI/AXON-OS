import os
import json
from datetime import datetime

from report_reader import ReportReader
from markdown_report import MarkdownReport


class ReportBuilder:
    def __init__(self, project_path):
        self.project_path = project_path
        self.reports_dir = os.path.join(
            project_path,
            "reports"
        )
        self.summary_file = os.path.join(
            self.reports_dir,
            "execution_summary.json"
        )

        os.makedirs(
            self.reports_dir,
            exist_ok=True
        )

    def build_execution_summary(self):
        reader = ReportReader(
            self.project_path
        )

        data = reader.read_project_files()

        workflow_result = self._extract_data(data.get("workflow_result"))
        progress = self._extract_data(data.get("progress"))
        intent = self._extract_data(data.get("intent"))
        task = self._extract_data(data.get("task"))
        environment_data = self._extract_data(data.get("environment_discovery"))
        installation_data = self._extract_data(data.get("installation_plan"))
        installation_approval_data = self._extract_data(
            data.get("installation_approval_plan")
        )

        virtualization_data = self._extract_data(
            data.get("virtualization_check")
        )

        gpu_capability_data = self._extract_data(
            data.get("gpu_capability")
        )

        acceleration_policy_data = self._extract_data(
            data.get("acceleration_policy")
        )

        execution_trace = data.get("execution_trace", {}).get("records", [])
        decisions = data.get("decisions", {}).get("records", [])
        approvals = data.get("approvals", {}).get("records", [])
        errors = data.get("errors", {}).get("records", [])
        operation_progress_records = data.get(
            "operation_progress",
            {}
        ).get("records", [])
        pending_actions = data.get("pending_actions", {})

        dataset_source = workflow_result.get("dataset_source", {})

        environment_summary = self._build_environment_summary(
            environment_data
        )

        installation_plan_summary = self._build_installation_plan_summary(
            installation_data
        )

        installation_approval_summary = self._build_installation_approval_summary(
            installation_approval_data
        )

        virtualization_summary = self._build_virtualization_summary(
            virtualization_data
        )

        gpu_capability_summary = self._build_gpu_capability_summary(
            gpu_capability_data
        )

        acceleration_policy_summary = self._build_acceleration_policy_summary(
            acceleration_policy_data
        )

        summary = {
            "report_type": "execution_summary",
            "generated_at": self._timestamp(),
            "project_path": self.project_path,
            "workflow": workflow_result.get("workflow"),
            "workflow_status": workflow_result.get("status"),
            "workflow_message": workflow_result.get("message"),
            "intent": {
                "intent_name": intent.get("intent_name"),
                "domain": intent.get("domain"),
                "action": intent.get("action"),
                "confidence": intent.get("confidence")
            },
            "task": {
                "id": task.get("id"),
                "name": task.get("name"),
                "status": task.get("status")
            },
            "progress": {
                "percent": progress.get("percent"),
                "status": progress.get("status"),
                "message": progress.get("message"),
                "current_step": progress.get("current_step"),
                "total_steps": progress.get("total_steps")
            },
            "dataset_source": {
                "selected_option": dataset_source.get("selected_option"),
                "status": dataset_source.get("status"),
                "plan_status": dataset_source.get(
                    "dataset_plan",
                    {}
                ).get("status"),
                "source": dataset_source.get(
                    "dataset_plan",
                    {}
                ).get("source")
            },
            "execution_stats": {
                "trace_events": len(execution_trace),
                "decision_events": len(decisions),
                "approval_events": len(approvals),
                "operation_progress_files": len(operation_progress_records),
                "pending_actions": pending_actions.get("pending_count", 0),
                "environment_report_available": environment_summary.get("available"),
                "installation_plan_available": installation_plan_summary.get("available"),
                "installation_items": installation_plan_summary.get("total_install_items"),
                "installation_approval_plan_available": installation_approval_summary.get("available"),
                "installation_approval_requests": installation_approval_summary.get("approval_requests_created"),
                "virtualization_report_available": virtualization_summary.get("available"),
                "gpu_capability_report_available": gpu_capability_summary.get("available"),
                "acceleration_policy_report_available": acceleration_policy_summary.get("available"),
                "acceleration_mode": acceleration_policy_summary.get("mode"),
                "acceleration_backend": acceleration_policy_summary.get("backend"),
                "error_events": len(errors)
            },
            "environment_summary": environment_summary,
            "installation_plan_summary": installation_plan_summary,
            "installation_approval_summary": installation_approval_summary,
            "virtualization_summary": virtualization_summary,
            "gpu_capability_summary": gpu_capability_summary,
            "acceleration_policy_summary": acceleration_policy_summary,
            "approvals_summary": self._build_approvals_summary(approvals),
            "operation_progress_summary": self._build_operation_progress_summary(
                operation_progress_records
            ),
            "pending_actions_summary": self._build_pending_actions_summary(
                pending_actions
            ),
            "errors": errors,
            "decisions": decisions,
            "approvals": approvals,
            "privacy": {
                "personal_information_included": False,
                "secret_values_included": False,
                "file_contents_included": False,
                "safe_for_developer_review": True
            }
        }

        self._write_json(self.summary_file, summary)

        markdown = MarkdownReport(self.project_path)
        markdown_result = markdown.build(summary)

        summary["generated_files"] = {
            "execution_summary": self.summary_file,
            "markdown_report": markdown_result.get("report_file")
        }

        self._write_json(self.summary_file, summary)

        return summary

    def _build_environment_summary(self, environment_data):
        if not environment_data:
            return {
                "available": False,
                "status": "missing",
                "message": "Environment discovery report was not found.",
                "execution_mode": None,
                "gpu_support_mode": None,
                "can_run_cpu_workflows": None,
                "can_run_gpu_workflows": None,
                "missing_tools": [],
                "missing_packages": []
            }

        recommendation = environment_data.get("recommendation", {})
        gpu = environment_data.get("gpu", {})

        return {
            "available": True,
            "status": environment_data.get("status"),
            "report_type": environment_data.get("report_type"),
            "execution_mode": recommendation.get("execution_mode"),
            "gpu_support_mode": gpu.get("gpu_support_mode"),
            "current_machine_gpu_detected": gpu.get("current_machine_gpu_detected"),
            "cuda_available": gpu.get("cuda_available"),
            "gpu_count": gpu.get("gpu_count"),
            "can_run_cpu_workflows": recommendation.get("can_run_cpu_workflows"),
            "can_run_gpu_workflows": recommendation.get("can_run_gpu_workflows"),
            "missing_tools": recommendation.get("missing_tools", []),
            "missing_packages": recommendation.get("missing_packages", []),
            "requires_installation_before_full_ai_workflows": recommendation.get(
                "requires_installation_before_full_ai_workflows"
            ),
            "note": gpu.get("note")
        }

    def _build_installation_plan_summary(self, installation_data):
        if not installation_data:
            return {
                "available": False,
                "status": "missing",
                "message": "Installation plan report was not found.",
                "total_install_items": 0,
                "execution_enabled": False,
                "requires_user_approval": False,
                "no_installation_executed": True,
                "items": []
            }

        summary = installation_data.get("summary", {})
        safety = installation_data.get("safety", {})

        items = []

        for item in installation_data.get("items", []):
            mapping = item.get("mapping", {})
            policy = item.get("policy", {})

            items.append(
                {
                    "item_name": item.get("item_name"),
                    "source": item.get("source"),
                    "install_type": mapping.get("install_type"),
                    "package_name": mapping.get("package_name"),
                    "install_command": mapping.get("install_command"),
                    "risk_level": policy.get("risk_level"),
                    "requires_approval": item.get("requires_approval"),
                    "execution_enabled": item.get("execution_enabled"),
                    "will_execute_now": item.get("will_execute_now")
                }
            )

        return {
            "available": True,
            "status": installation_data.get("status"),
            "report_type": installation_data.get("report_type"),
            "missing_tools_count": summary.get("missing_tools_count"),
            "missing_packages_count": summary.get("missing_packages_count"),
            "total_install_items": summary.get("total_install_items"),
            "execution_enabled": summary.get("execution_enabled"),
            "requires_user_approval": summary.get("requires_user_approval"),
            "planning_only": safety.get("planning_only"),
            "no_installation_executed": safety.get("no_installation_executed"),
            "no_system_changes_made": safety.get("no_system_changes_made"),
            "items": items
        }

    def _build_installation_approval_summary(self, approval_data):
        if not approval_data:
            return {
                "available": False,
                "status": "missing",
                "message": "Installation approval plan report was not found.",
                "total_items": 0,
                "approval_requests_created": 0,
                "no_installation_executed": True,
                "no_pip_command_executed": True,
                "items": []
            }

        safety = approval_data.get("safety", {})

        items = []

        for item in approval_data.get("items", []):
            approval = item.get("approval", {})
            request_event = approval.get("request_event", {})
            policy = request_event.get("policy", {})

            items.append(
                {
                    "action_name": item.get("action_name"),
                    "operation_name": item.get("operation_name"),
                    "item_name": item.get("item_name"),
                    "install_type": item.get("install_type"),
                    "risk_level": item.get("risk_level"),
                    "policy_status": policy.get("status"),
                    "base_action": policy.get("base_action"),
                    "progress_type": policy.get("progress_type"),
                    "approval_status": approval.get("status"),
                    "will_execute_now": item.get("will_execute_now")
                }
            )

        return {
            "available": True,
            "status": approval_data.get("status"),
            "report_type": approval_data.get("report_type"),
            "total_items": approval_data.get("total_items"),
            "approval_requests_created": approval_data.get("approval_requests_created"),
            "planning_only": safety.get("planning_only"),
            "no_installation_executed": safety.get("no_installation_executed"),
            "no_system_changes_made": safety.get("no_system_changes_made"),
            "no_pip_command_executed": safety.get("no_pip_command_executed"),
            "requires_user_approval_before_install": safety.get(
                "requires_user_approval_before_install"
            ),
            "items": items
        }

    def _build_virtualization_summary(self, virtualization_data):
        if not virtualization_data:
            return {
                "available": False,
                "status": "missing",
                "virtualization_detected": None,
                "virtualization_type": None,
                "recommended_mode": None,
                "safe_mode": None,
                "auto_install_gpu_drivers": False
            }

        policy = virtualization_data.get("policy", {})

        return {
            "available": True,
            "status": virtualization_data.get("status"),
            "report_type": virtualization_data.get("report_type"),
            "virtualization_detected": virtualization_data.get("virtualization_detected"),
            "virtualization_type": virtualization_data.get("virtualization_type"),
            "recommended_mode": virtualization_data.get("recommended_mode"),
            "safe_mode": virtualization_data.get("safe_mode"),
            "auto_install_gpu_drivers": policy.get("auto_install_gpu_drivers"),
            "auto_install_rocm": policy.get("auto_install_rocm"),
            "auto_install_nvidia_drivers": policy.get("auto_install_nvidia_drivers"),
            "auto_install_bitsandbytes": policy.get("auto_install_bitsandbytes"),
            "reason": policy.get("reason")
        }

    def _build_gpu_capability_summary(self, gpu_data):
        if not gpu_data:
            return {
                "available": False,
                "status": "missing",
                "gpu_vendor": None,
                "recommended_backend": None,
                "execution_mode": None,
                "gpu_acceleration_ready": False
            }

        gpu = gpu_data.get("gpu", {})
        tools = gpu_data.get("tools", {})
        torch_info = gpu_data.get("torch", {})
        recommendation = gpu_data.get("recommendation", {})
        policy = gpu_data.get("policy", {})

        return {
            "available": True,
            "status": gpu_data.get("status"),
            "report_type": gpu_data.get("report_type"),
            "guest_gpu_visible": gpu.get("guest_gpu_visible"),
            "gpu_vendor": gpu.get("gpu_vendor"),
            "virtual_gpu_detected": gpu.get("virtual_gpu_detected"),
            "gpu_passthrough_status": gpu.get("gpu_passthrough_status"),
            "gpu_devices": gpu.get("gpu_devices", []),
            "nvidia_smi_available": tools.get("nvidia_smi_available"),
            "rocm_smi_available": tools.get("rocm_smi_available"),
            "torch_available": torch_info.get("torch_available"),
            "torch_version": torch_info.get("torch_version"),
            "cuda_available": torch_info.get("cuda_available"),
            "torch_cuda_version": torch_info.get("torch_cuda_version"),
            "gpu_count": torch_info.get("gpu_count"),
            "gpu_names": torch_info.get("gpu_names", []),
            "recommended_backend": recommendation.get("recommended_backend"),
            "execution_mode": recommendation.get("execution_mode"),
            "gpu_acceleration_ready": recommendation.get("gpu_acceleration_ready"),
            "allow_optional_gpu_packages": recommendation.get("allow_optional_gpu_packages"),
            "auto_install_gpu_drivers": policy.get("auto_install_gpu_drivers"),
            "auto_install_bitsandbytes": policy.get("auto_install_bitsandbytes"),
            "reason": recommendation.get("reason")
        }

    def _build_acceleration_policy_summary(self, acceleration_data):
        if not acceleration_data:
            return {
                "available": False,
                "status": "missing",
                "mode": None,
                "backend": None,
                "gpu_acceleration_ready": False,
                "allow_gpu_packages": False
            }

        acceleration = acceleration_data.get("acceleration", {})
        package_policy = acceleration_data.get("package_policy", {})
        safety = acceleration_data.get("safety", {})
        user_guidance = acceleration_data.get("user_guidance", {})

        return {
            "available": True,
            "status": acceleration_data.get("status"),
            "report_type": acceleration_data.get("report_type"),
            "mode": acceleration.get("mode"),
            "backend": acceleration.get("backend"),
            "gpu_acceleration_ready": acceleration.get("gpu_acceleration_ready"),
            "allow_gpu_packages": acceleration.get("allow_gpu_packages"),
            "allow_gpu_driver_plan": acceleration.get("allow_gpu_driver_plan"),
            "recommended_for_release": acceleration.get("recommended_for_release"),
            "bitsandbytes_status": package_policy.get("bitsandbytes", {}).get("current_status"),
            "bitsandbytes_allowed_now": package_policy.get("bitsandbytes", {}).get("allowed_now"),
            "nvidia_smi_auto_install_allowed": package_policy.get("nvidia_smi", {}).get("auto_install_allowed"),
            "rocm_auto_install_allowed": package_policy.get("rocm", {}).get("auto_install_allowed"),
            "gpu_driver_auto_install_allowed": safety.get("gpu_driver_auto_install_allowed"),
            "requires_explicit_user_approval": safety.get("requires_explicit_user_approval"),
            "summary": user_guidance.get("summary"),
            "message": user_guidance.get("message"),
            "recommended_next_steps": user_guidance.get("recommended_next_steps", []),
            "reason": acceleration.get("reason")
        }

    def _build_approvals_summary(self, approvals):
        summary = {
            "total_events": len(approvals),
            "approval_requests": 0,
            "user_decisions": 0,
            "auto_allowed": 0,
            "approved": 0,
            "rejected": 0,
            "waiting_for_user_decision": 0,
            "actions": []
        }

        for approval in approvals:
            event_type = approval.get("event_type")
            action_name = approval.get("action_name")

            if event_type == "approval_request":
                summary["approval_requests"] += 1

                if approval.get("user_decision") is None:
                    summary["waiting_for_user_decision"] += 1

            elif event_type == "user_decision":
                summary["user_decisions"] += 1

                if approval.get("approved"):
                    summary["approved"] += 1
                else:
                    summary["rejected"] += 1

            elif event_type == "auto_allowed":
                summary["auto_allowed"] += 1
                summary["approved"] += 1

            summary["actions"].append(
                {
                    "event_type": event_type,
                    "action_name": action_name,
                    "approved": approval.get("approved"),
                    "risk_level": approval.get("policy", {}).get("risk_level")
                }
            )

        return summary

    def _build_operation_progress_summary(self, operation_progress_records):
        operations = []

        for record in operation_progress_records:
            data = record.get("data", {})

            operations.append(
                {
                    "file": record.get("file"),
                    "operation_name": data.get("operation_name"),
                    "progress_type": data.get("progress_type"),
                    "status": data.get("status"),
                    "percent": data.get("percent"),
                    "message": data.get("message"),
                    "can_be_cancelled": data.get("can_be_cancelled"),
                    "updated_at": data.get("updated_at")
                }
            )

        return {
            "total_operations": len(operations),
            "operations": operations
        }

    def _build_pending_actions_summary(self, pending_actions):
        actions = []

        for action in pending_actions.get("pending_actions", []):
            actions.append(
                {
                    "action_name": action.get("action_name"),
                    "risk_level": action.get("risk_level"),
                    "progress_type": action.get("progress_type"),
                    "operation_status": action.get("operation_status"),
                    "operation_percent": action.get("operation_percent"),
                    "operation_file": action.get("operation_file")
                }
            )

        return {
            "status": pending_actions.get("status"),
            "pending_count": pending_actions.get("pending_count", 0),
            "actions": actions
        }

    def _extract_data(self, file_record):
        if not file_record:
            return {}

        return file_record.get("data") or {}

    def _write_json(self, file_path, data):
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False
            )

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
