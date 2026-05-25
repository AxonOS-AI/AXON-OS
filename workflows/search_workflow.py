def run(task):
    payload = task.get("payload", {})
    intent = payload.get("intent", {})

    raw_input = intent.get("raw_input", "")
    domain = intent.get("domain", "unknown")
    action = intent.get("action", "unknown")

    steps = [
        "Receive search request",
        "Identify search domain",
        "Prepare search query",
        "Select search backend",
        "Return search execution plan"
    ]

    result = {
        "workflow": "search_workflow",
        "status": "prepared",
        "message": "Search workflow prepared successfully",
        "input": raw_input,
        "domain": domain,
        "action": action,
        "steps": steps
    }

    return result
