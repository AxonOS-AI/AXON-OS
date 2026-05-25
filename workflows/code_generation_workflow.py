def run(task):
    payload = task.get("payload", {})
    intent = payload.get("intent", {})

    raw_input = intent.get("raw_input", "")
    domain = intent.get("domain", "unknown")
    action = intent.get("action", "unknown")

    steps = [
        "Receive code generation request",
        "Analyze programming intent",
        "Identify target language or framework",
        "Prepare code generation context",
        "Select code generation model",
        "Return code generation execution plan"
    ]

    result = {
        "workflow": "code_generation_workflow",
        "status": "prepared",
        "message": "Code generation workflow prepared successfully",
        "input": raw_input,
        "domain": domain,
        "action": action,
        "steps": steps
    }

    return result
