import os


class MarkdownReport:
    def __init__(self, project_path):
        self.project_path = project_path
        self.reports_dir = os.path.join(
            project_path,
            "reports"
        )
        self.report_file = os.path.join(
            self.reports_dir,
            "final_report.md"
        )

        os.makedirs(
            self.reports_dir,
            exist_ok=True
        )

    def build(self, summary):
        workflow = summary.get("workflow", "unknown")
        workflow_status = summary.get("workflow_status", "unknown")
        workflow_message = summary.get("workflow_message", "")

        intent = summary.get("intent", {})
        task = summary.get("task", {})
        progress = summary.get("progress", {})
        dataset_source = summary.get("dataset_source", {})
        execution_stats = summary.get("execution_stats", {})
        environment_summary = summary.get("environment_summary", {})
        installation_plan_summary = summary.get("installation_plan_summary", {})
        installation_approval_summary = summary.get("installation_approval_summary", {})
        virtualization_summary = summary.get("virtualization_summary", {})
        gpu_capability_summary = summary.get("gpu_capability_summary", {})
        acceleration_policy_summary = summary.get("acceleration_policy_summary", {})
        approvals_summary = summary.get("approvals_summary", {})
        operation_progress_summary = summary.get("operation_progress_summary", {})
        pending_actions_summary = summary.get("pending_actions_summary", {})
        privacy = summary.get("privacy", {})
        errors = summary.get("errors", [])
        decisions = summary.get("decisions", [])

        lines = []

        lines.append("# AXON Execution Report")
        lines.append("")
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Workflow: `{workflow}`")
        lines.append(f"- Status: `{workflow_status}`")
        lines.append(f"- Message: {workflow_message}")
        lines.append(f"- Project Path: `{summary.get('project_path')}`")
        lines.append(f"- Generated At: `{summary.get('generated_at')}`")
        lines.append("")

        lines.append("## Intent")
        lines.append("")
        lines.append(f"- Intent Name: `{intent.get('intent_name')}`")
        lines.append(f"- Domain: `{intent.get('domain')}`")
        lines.append(f"- Action: `{intent.get('action')}`")
        lines.append(f"- Confidence: `{intent.get('confidence')}`")
        lines.append("")

        lines.append("## Task")
        lines.append("")
        lines.append(f"- Task ID: `{task.get('id')}`")
        lines.append(f"- Task Name: `{task.get('name')}`")
        lines.append(f"- Task Status: `{task.get('status')}`")
        lines.append("")

        lines.append("## Progress")
        lines.append("")
        lines.append(f"- Percent: `{progress.get('percent')}%`")
        lines.append(f"- Status: `{progress.get('status')}`")
        lines.append(f"- Message: {progress.get('message')}")
        lines.append(f"- Step: `{progress.get('current_step')}/{progress.get('total_steps')}`")
        lines.append("")

        lines.append("## Dataset Source")
        lines.append("")
        lines.append(f"- Selected Option: `{dataset_source.get('selected_option')}`")
        lines.append(f"- Status: `{dataset_source.get('status')}`")
        lines.append(f"- Plan Status: `{dataset_source.get('plan_status')}`")
        lines.append(f"- Source: `{dataset_source.get('source')}`")
        lines.append("")

        lines.append("## Environment Summary")
        lines.append("")
        lines.append(f"- Available: `{environment_summary.get('available')}`")
        lines.append(f"- Status: `{environment_summary.get('status')}`")
        lines.append(f"- Execution Mode: `{environment_summary.get('execution_mode')}`")
        lines.append(f"- GPU Support Mode: `{environment_summary.get('gpu_support_mode')}`")
        lines.append(f"- Current Machine GPU Detected: `{environment_summary.get('current_machine_gpu_detected')}`")
        lines.append(f"- CUDA Available On Current Machine: `{environment_summary.get('cuda_available')}`")
        lines.append(f"- GPU Count On Current Machine: `{environment_summary.get('gpu_count')}`")
        lines.append(f"- CPU Workflows Supported: `{environment_summary.get('can_run_cpu_workflows')}`")
        lines.append(f"- GPU Workflows Available On Current Machine: `{environment_summary.get('can_run_gpu_workflows')}`")
        lines.append(f"- Requires Installation Before Full AI Workflows: `{environment_summary.get('requires_installation_before_full_ai_workflows')}`")
        lines.append("")

        missing_tools = environment_summary.get("missing_tools", [])
        missing_packages = environment_summary.get("missing_packages", [])

        lines.append("### Missing Tools")
        lines.append("")
        if not missing_tools:
            lines.append("No missing tools were detected.")
        else:
            for tool in missing_tools:
                lines.append(f"- `{tool}`")
        lines.append("")

        lines.append("### Missing Packages")
        lines.append("")
        if not missing_packages:
            lines.append("No missing packages were detected.")
        else:
            for package in missing_packages:
                lines.append(f"- `{package}`")
        lines.append("")

        if environment_summary.get("note"):
            lines.append("### Environment Note")
            lines.append("")
            lines.append(environment_summary.get("note"))
            lines.append("")

        lines.append("## Installation Plan Summary")
        lines.append("")
        lines.append(f"- Available: `{installation_plan_summary.get('available')}`")
        lines.append(f"- Status: `{installation_plan_summary.get('status')}`")
        lines.append(f"- Total Install Items: `{installation_plan_summary.get('total_install_items')}`")
        lines.append(f"- Execution Enabled: `{installation_plan_summary.get('execution_enabled')}`")
        lines.append(f"- Requires User Approval: `{installation_plan_summary.get('requires_user_approval')}`")
        lines.append(f"- Planning Only: `{installation_plan_summary.get('planning_only')}`")
        lines.append(f"- No Installation Executed: `{installation_plan_summary.get('no_installation_executed')}`")
        lines.append(f"- No System Changes Made: `{installation_plan_summary.get('no_system_changes_made')}`")
        lines.append("")

        install_items = installation_plan_summary.get("items", [])

        if not install_items:
            lines.append("No installation items were planned.")
        else:
            for item in install_items:
                lines.append(f"- Install Item: `{item.get('item_name')}`")
                lines.append(f"  - Source: `{item.get('source')}`")
                lines.append(f"  - Install Type: `{item.get('install_type')}`")
                lines.append(f"  - Package Name: `{item.get('package_name')}`")
                lines.append(f"  - Install Command: `{item.get('install_command')}`")
                lines.append(f"  - Risk Level: `{item.get('risk_level')}`")
                lines.append(f"  - Requires Approval: `{item.get('requires_approval')}`")
                lines.append(f"  - Execution Enabled: `{item.get('execution_enabled')}`")
                lines.append(f"  - Will Execute Now: `{item.get('will_execute_now')}`")
        lines.append("")

        lines.append("## Installation Approval Summary")
        lines.append("")
        lines.append(f"- Available: `{installation_approval_summary.get('available')}`")
        lines.append(f"- Status: `{installation_approval_summary.get('status')}`")
        lines.append(f"- Total Items: `{installation_approval_summary.get('total_items')}`")
        lines.append(f"- Approval Requests Created: `{installation_approval_summary.get('approval_requests_created')}`")
        lines.append(f"- Planning Only: `{installation_approval_summary.get('planning_only')}`")
        lines.append(f"- No Installation Executed: `{installation_approval_summary.get('no_installation_executed')}`")
        lines.append(f"- No System Changes Made: `{installation_approval_summary.get('no_system_changes_made')}`")
        lines.append(f"- No Pip Command Executed: `{installation_approval_summary.get('no_pip_command_executed')}`")
        lines.append(f"- Requires User Approval Before Install: `{installation_approval_summary.get('requires_user_approval_before_install')}`")
        lines.append("")

        approval_items = installation_approval_summary.get("items", [])

        if not approval_items:
            lines.append("No installation approval items were found.")
        else:
            for item in approval_items:
                lines.append(f"- Approval Action: `{item.get('action_name')}`")
                lines.append(f"  - Operation Name: `{item.get('operation_name')}`")
                lines.append(f"  - Item Name: `{item.get('item_name')}`")
                lines.append(f"  - Install Type: `{item.get('install_type')}`")
                lines.append(f"  - Risk Level: `{item.get('risk_level')}`")
                lines.append(f"  - Policy Status: `{item.get('policy_status')}`")
                lines.append(f"  - Base Action: `{item.get('base_action')}`")
                lines.append(f"  - Progress Type: `{item.get('progress_type')}`")
                lines.append(f"  - Approval Status: `{item.get('approval_status')}`")
                lines.append(f"  - Will Execute Now: `{item.get('will_execute_now')}`")
        lines.append("")

        lines.append("## Virtualization Summary")
        lines.append("")
        lines.append(f"- Available: `{virtualization_summary.get('available')}`")
        lines.append(f"- Status: `{virtualization_summary.get('status')}`")
        lines.append(f"- Virtualization Detected: `{virtualization_summary.get('virtualization_detected')}`")
        lines.append(f"- Virtualization Type: `{virtualization_summary.get('virtualization_type')}`")
        lines.append(f"- Recommended Mode: `{virtualization_summary.get('recommended_mode')}`")
        lines.append(f"- Safe Mode: `{virtualization_summary.get('safe_mode')}`")
        lines.append(f"- Auto Install GPU Drivers: `{virtualization_summary.get('auto_install_gpu_drivers')}`")
        lines.append(f"- Auto Install ROCm: `{virtualization_summary.get('auto_install_rocm')}`")
        lines.append(f"- Auto Install NVIDIA Drivers: `{virtualization_summary.get('auto_install_nvidia_drivers')}`")
        lines.append(f"- Auto Install bitsandbytes: `{virtualization_summary.get('auto_install_bitsandbytes')}`")
        lines.append("")
        if virtualization_summary.get("reason"):
            lines.append("### Virtualization Reason")
            lines.append("")
            lines.append(virtualization_summary.get("reason"))
            lines.append("")

        lines.append("## GPU Capability Summary")
        lines.append("")
        lines.append(f"- Available: `{gpu_capability_summary.get('available')}`")
        lines.append(f"- Status: `{gpu_capability_summary.get('status')}`")
        lines.append(f"- Guest GPU Visible: `{gpu_capability_summary.get('guest_gpu_visible')}`")
        lines.append(f"- GPU Vendor: `{gpu_capability_summary.get('gpu_vendor')}`")
        lines.append(f"- Virtual GPU Detected: `{gpu_capability_summary.get('virtual_gpu_detected')}`")
        lines.append(f"- GPU Passthrough Status: `{gpu_capability_summary.get('gpu_passthrough_status')}`")
        lines.append(f"- NVIDIA SMI Available: `{gpu_capability_summary.get('nvidia_smi_available')}`")
        lines.append(f"- ROCm SMI Available: `{gpu_capability_summary.get('rocm_smi_available')}`")
        lines.append(f"- Torch Available: `{gpu_capability_summary.get('torch_available')}`")
        lines.append(f"- Torch Version: `{gpu_capability_summary.get('torch_version')}`")
        lines.append(f"- CUDA Available: `{gpu_capability_summary.get('cuda_available')}`")
        lines.append(f"- Torch CUDA Version: `{gpu_capability_summary.get('torch_cuda_version')}`")
        lines.append(f"- GPU Count: `{gpu_capability_summary.get('gpu_count')}`")
        lines.append(f"- Recommended Backend: `{gpu_capability_summary.get('recommended_backend')}`")
        lines.append(f"- Execution Mode: `{gpu_capability_summary.get('execution_mode')}`")
        lines.append(f"- GPU Acceleration Ready: `{gpu_capability_summary.get('gpu_acceleration_ready')}`")
        lines.append(f"- Allow Optional GPU Packages: `{gpu_capability_summary.get('allow_optional_gpu_packages')}`")
        lines.append("")

        gpu_devices = gpu_capability_summary.get("gpu_devices", [])
        lines.append("### GPU Devices")
        lines.append("")
        if not gpu_devices:
            lines.append("No GPU devices were reported.")
        else:
            for device in gpu_devices:
                lines.append(f"- `{device}`")
        lines.append("")

        if gpu_capability_summary.get("reason"):
            lines.append("### GPU Capability Reason")
            lines.append("")
            lines.append(gpu_capability_summary.get("reason"))
            lines.append("")

        lines.append("## Acceleration Policy Summary")
        lines.append("")
        lines.append(f"- Available: `{acceleration_policy_summary.get('available')}`")
        lines.append(f"- Status: `{acceleration_policy_summary.get('status')}`")
        lines.append(f"- Mode: `{acceleration_policy_summary.get('mode')}`")
        lines.append(f"- Backend: `{acceleration_policy_summary.get('backend')}`")
        lines.append(f"- GPU Acceleration Ready: `{acceleration_policy_summary.get('gpu_acceleration_ready')}`")
        lines.append(f"- Allow GPU Packages: `{acceleration_policy_summary.get('allow_gpu_packages')}`")
        lines.append(f"- Allow GPU Driver Plan: `{acceleration_policy_summary.get('allow_gpu_driver_plan')}`")
        lines.append(f"- Recommended For Release: `{acceleration_policy_summary.get('recommended_for_release')}`")
        lines.append(f"- bitsandbytes Status: `{acceleration_policy_summary.get('bitsandbytes_status')}`")
        lines.append(f"- bitsandbytes Allowed Now: `{acceleration_policy_summary.get('bitsandbytes_allowed_now')}`")
        lines.append(f"- NVIDIA SMI Auto Install Allowed: `{acceleration_policy_summary.get('nvidia_smi_auto_install_allowed')}`")
        lines.append(f"- ROCm Auto Install Allowed: `{acceleration_policy_summary.get('rocm_auto_install_allowed')}`")
        lines.append(f"- GPU Driver Auto Install Allowed: `{acceleration_policy_summary.get('gpu_driver_auto_install_allowed')}`")
        lines.append(f"- Requires Explicit User Approval: `{acceleration_policy_summary.get('requires_explicit_user_approval')}`")
        lines.append("")

        if acceleration_policy_summary.get("summary"):
            lines.append("### Acceleration Summary")
            lines.append("")
            lines.append(acceleration_policy_summary.get("summary"))
            lines.append("")

        if acceleration_policy_summary.get("message"):
            lines.append("### User Guidance")
            lines.append("")
            lines.append(acceleration_policy_summary.get("message"))
            lines.append("")

        next_steps = acceleration_policy_summary.get("recommended_next_steps", [])
        lines.append("### Recommended Next Steps")
        lines.append("")
        if not next_steps:
            lines.append("No acceleration-specific next steps were provided.")
        else:
            for step in next_steps:
                lines.append(f"- {step}")
        lines.append("")

        lines.append("## Execution Statistics")
        lines.append("")
        lines.append(f"- Trace Events: `{execution_stats.get('trace_events')}`")
        lines.append(f"- Decision Events: `{execution_stats.get('decision_events')}`")
        lines.append(f"- Approval Events: `{execution_stats.get('approval_events')}`")
        lines.append(f"- Operation Progress Files: `{execution_stats.get('operation_progress_files')}`")
        lines.append(f"- Pending Actions: `{execution_stats.get('pending_actions')}`")
        lines.append(f"- Environment Report Available: `{execution_stats.get('environment_report_available')}`")
        lines.append(f"- Installation Plan Available: `{execution_stats.get('installation_plan_available')}`")
        lines.append(f"- Installation Items: `{execution_stats.get('installation_items')}`")
        lines.append(f"- Error Events: `{execution_stats.get('error_events')}`")
        lines.append("")

        lines.append("## Approvals Summary")
        lines.append("")
        lines.append(f"- Total Events: `{approvals_summary.get('total_events')}`")
        lines.append(f"- Approval Requests: `{approvals_summary.get('approval_requests')}`")
        lines.append(f"- User Decisions: `{approvals_summary.get('user_decisions')}`")
        lines.append(f"- Auto Allowed: `{approvals_summary.get('auto_allowed')}`")
        lines.append(f"- Approved: `{approvals_summary.get('approved')}`")
        lines.append(f"- Rejected: `{approvals_summary.get('rejected')}`")
        lines.append(f"- Waiting For User Decision: `{approvals_summary.get('waiting_for_user_decision')}`")
        lines.append("")

        approval_actions = approvals_summary.get("actions", [])

        if approval_actions:
            lines.append("### Approval Actions")
            lines.append("")

            for action in approval_actions:
                lines.append(f"- Action: `{action.get('action_name')}`")
                lines.append(f"  - Event Type: `{action.get('event_type')}`")
                lines.append(f"  - Approved: `{action.get('approved')}`")
                lines.append(f"  - Risk Level: `{action.get('risk_level')}`")
            lines.append("")

        lines.append("## Operation Progress Summary")
        lines.append("")
        lines.append(f"- Total Operations: `{operation_progress_summary.get('total_operations')}`")
        lines.append("")

        operations = operation_progress_summary.get("operations", [])

        if not operations:
            lines.append("No operation progress records were found.")
        else:
            for operation in operations:
                lines.append(f"- Operation: `{operation.get('operation_name')}`")
                lines.append(f"  - Type: `{operation.get('progress_type')}`")
                lines.append(f"  - Status: `{operation.get('status')}`")
                lines.append(f"  - Percent: `{operation.get('percent')}%`")
                lines.append(f"  - Message: {operation.get('message')}")
                lines.append(f"  - Can Be Cancelled: `{operation.get('can_be_cancelled')}`")
                lines.append(f"  - File: `{operation.get('file')}`")
        lines.append("")

        lines.append("## Pending Actions Summary")
        lines.append("")
        lines.append(f"- Status: `{pending_actions_summary.get('status')}`")
        lines.append(f"- Pending Count: `{pending_actions_summary.get('pending_count')}`")
        lines.append("")

        pending_actions = pending_actions_summary.get("actions", [])

        if not pending_actions:
            lines.append("No pending actions were found.")
        else:
            for action in pending_actions:
                lines.append(f"- Pending Action: `{action.get('action_name')}`")
                lines.append(f"  - Risk Level: `{action.get('risk_level')}`")
                lines.append(f"  - Progress Type: `{action.get('progress_type')}`")
                lines.append(f"  - Operation Status: `{action.get('operation_status')}`")
                lines.append(f"  - Operation Percent: `{action.get('operation_percent')}%`")
                lines.append(f"  - Operation File: `{action.get('operation_file')}`")
        lines.append("")

        lines.append("## Decisions")
        lines.append("")

        if not decisions:
            lines.append("No decisions were recorded.")
        else:
            for decision in decisions:
                lines.append(f"- Step: `{decision.get('step_name')}`")
                lines.append(f"  - Selected: `{decision.get('selected_option')}`")
                lines.append(f"  - Reason: {decision.get('reason')}")
        lines.append("")

        lines.append("## Errors")
        lines.append("")

        if not errors:
            lines.append("No errors were recorded.")
        else:
            for error in errors:
                lines.append(f"- Error Code: `{error.get('error_code')}`")
                lines.append(f"  - Module: `{error.get('module')}`")
                lines.append(f"  - Message: {error.get('message')}")
                lines.append(f"  - Suggestion: {error.get('suggestion')}")
        lines.append("")

        lines.append("## Privacy")
        lines.append("")
        lines.append(f"- Personal Information Included: `{privacy.get('personal_information_included')}`")
        lines.append(f"- Secret Values Included: `{privacy.get('secret_values_included')}`")
        lines.append(f"- File Contents Included: `{privacy.get('file_contents_included')}`")
        lines.append(f"- Safe For Developer Review: `{privacy.get('safe_for_developer_review')}`")
        lines.append("")

        content = "\n".join(lines)

        with open(self.report_file, "w", encoding="utf-8") as file:
            file.write(content)

        return {
            "status": "created",
            "report_file": self.report_file
        }
