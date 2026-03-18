# AxonOS/ai-container/assistant/server.py
# ─────────────────────────────────────────────────────────────────
# Copyright (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# Purpose: Minimal FastAPI server inside the AI container.
#          Platform Layer calls this REST API to run inference.
# ─────────────────────────────────────────────────────────────────

import os
import json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="Axon OS AI Runtime", version="1.0.0")
MODELS_DIR = "/axon/models"


class InferenceRequest(BaseModel):
    prompt: str
    model_id: str = "default"
    max_tokens: int = 256


@app.get("/health")
def health():
    return {"status": "ok", "layer": "ai-container"}


@app.get("/models")
def list_models():
    registry_path = os.path.join(MODELS_DIR, "registry.json")
    if os.path.exists(registry_path):
        with open(registry_path) as f:
            return json.load(f)
    return {"models": [], "note": "No models loaded yet"}


@app.post("/infer")
def infer(req: InferenceRequest):
    # Phase 5 will implement actual model inference here
    return {
        "prompt": req.prompt,
        "response": "[AI inference — Phase 5 implementation]",
        "model": req.model_id,
        "status": "scaffold"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
