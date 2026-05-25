def run(task):
    payload = task.get("payload", {})
    intent = payload.get("intent", {})

    raw_input = intent.get("raw_input", "")
    domain = intent.get("domain", "unknown")
    action = intent.get("action", "unknown")

    steps = [
        "Receive analysis request",
        "Identify analysis target",
        "Validate input data",
        "Select analysis method",
        "Prepare analysis execution plan"
    ]

    result = {
        "workflow": "analysis_workflow",
        "status": "prepared",
        "message": "Analysis workflow prepared successfully",
        "input": raw_input,
        "domain": domain,
        "action": action,
        "steps": steps
    }

    return result
