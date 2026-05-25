import shutil
import subprocess


class ToolCheck:
    def __init__(self):
        self.default_tools = [
            "python3",
            "pip",
            "git",
            "curl",
            "wget",
            "kaggle",
            "nvidia-smi"
        ]

    def check_tool(self, tool_name, version_args=None):
        path = shutil.which(tool_name)

        result = {
            "tool": tool_name,
            "available": path is not None,
            "path": path,
            "version": None,
            "version_check_status": "not_checked",
            "error": None
        }

        if path is None:
            result["version_check_status"] = "skipped"
            result["error"] = "Tool was not found in PATH."
            return result

        args = version_args or self._default_version_args(tool_name)

        if not args:
            result["version_check_status"] = "no_version_args"
            return result

        try:
            completed = subprocess.run(
                [tool_name] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )

            output = completed.stdout.strip() or completed.stderr.strip()

            result["version"] = output.splitlines()[0] if output else ""
            result["version_check_status"] = (
                "success" if completed.returncode == 0 else "error"
            )

            if completed.returncode != 0:
                result["error"] = output

        except Exception as error:
            result["version_check_status"] = "error"
            result["error"] = str(error)

        return result

    def check_tools(self, tools=None):
        tools = tools or self.default_tools

        results = []

        for tool in tools:
            results.append(
                self.check_tool(tool)
            )

        available_count = sum(
            1 for item in results if item.get("available")
        )

        missing = [
            item.get("tool")
            for item in results
            if not item.get("available")
        ]

        return {
            "status": "completed",
            "total_tools": len(results),
            "available_count": available_count,
            "missing_count": len(missing),
            "missing_tools": missing,
            "tools": results
        }

    def _default_version_args(self, tool_name):
        version_args = {
            "python3": ["--version"],
            "pip": ["--version"],
            "git": ["--version"],
            "curl": ["--version"],
            "wget": ["--version"],
            "kaggle": ["--version"],
            "nvidia-smi": []
        }

        return version_args.get(tool_name, ["--version"])
