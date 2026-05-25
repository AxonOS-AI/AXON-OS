import os
import sys
import json
from datetime import datetime

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

INSTALLATION_DIR = os.path.join(BASE_DIR, "installation")

if INSTALLATION_DIR not in sys.path:
    sys.path.append(INSTALLATION_DIR)

from package_mapper import PackageMapper
from install_policy import InstallPolicy


class InstallationPlan:
    def __init__(self):
        self.mapper = PackageMapper()
        self.policy = InstallPolicy()

    def build_from_environment_report(self, project_path):
        environment_file = os.path.join(
            project_path,
            "reports",
            "environment_discovery.json"
        )

        if not os.path.exists(environment_file):
            return {
                "status": "error",
                "error_code": "ENVIRONMENT_REPORT_NOT_FOUND",
                "message": "Environment discovery report was not found.",
                "environment_file": environment_file,
                "suggestion": "Run EnvironmentDiscovery.save_discovery_report(project_path) first."
            }

        with open(environment_file, "r", encoding="utf-8") as file:
            environment_report = json.load(file)

        recommendation = environment_report.get("recommendation", {})

        missing_tools = recommendation.get("missing_tools", [])
        missing_packages = recommendation.get("missing_packages", [])

        return self.build_plan(
            project_path=project_path,
            missing_tools=missing_tools,
            missing_packages=missing_packages,
            source_report=environment_file
        )

    def build_plan(
        self,
        project_path,
        missing_tools=None,
        missing_packages=None,
        source_report=None
    ):
        missing_tools = missing_tools or []
        missing_packages = missing_packages or []

        all_items = []

        for item in missing_tools:
            all_items.append(
                {
                    "source": "missing_tool",
                    "name": item
                }
            )

        for item in missing_packages:
            all_items.append(
                {
                    "source": "missing_package",
                    "name": item
                }
            )

        plan_items = []

        for item in all_items:
            mapped = self.mapper.map_item(
                item.get("name")
            )

            install_type = mapped.get(
                "install_type",
                "unknown"
            )

            policy = self.policy.get_policy(
                install_type
            )

            plan_items.append(
                {
                    "source": item.get("source"),
                    "item_name": item.get("name"),
                    "mapping": mapped,
                    "policy": policy,
                    "requires_approval": policy.get("requires_approval", True),
                    "requires_progress": policy.get("requires_progress", True),
                    "execution_enabled": policy.get("execution_enabled", False),
                    "will_execute_now": False
                }
            )

        plan = {
            "status": "planned",
            "report_type": "installation_plan",
            "generated_at": self._timestamp(),
            "project_path": project_path,
            "source_report": source_report,
            "summary": {
                "missing_tools_count": len(missing_tools),
                "missing_packages_count": len(missing_packages),
                "total_install_items": len(plan_items),
                "execution_enabled": False,
                "requires_user_approval": len(plan_items) > 0
            },
            "items": plan_items,
            "safety": {
                "planning_only": True,
                "no_installation_executed": True,
                "no_system_changes_made": True,
                "requires_user_approval_before_install": True
            }
        }

        self._save_plan(
            project_path,
            plan
        )

        return plan

    def _save_plan(self, project_path, plan):
        reports_dir = os.path.join(
            project_path,
            "reports"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        plan_file = os.path.join(
            reports_dir,
            "installation_plan.json"
        )

        with open(plan_file, "w", encoding="utf-8") as file:
            json.dump(
                plan,
                file,
                indent=2,
                ensure_ascii=False
            )

        plan["generated_files"] = {
            "installation_plan": plan_file
        }

    def _timestamp(self):
        return datetime.utcnow().isoformat() + "Z"
