# =============================================================================
# Axon OS — Assistant AI Main Entry Point
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

import os
import logging
from fastapi import FastAPI
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("axon-ai")

app = FastAPI(
    title="Axon OS — AI Assistant",
    description="Axon OS AI Container API",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    prompt: str
    max_tokens: int = 512

@app.get("/health")
def health():
    return {"status": "running", "service": "axon-ai"}

@app.post("/query")
def query(request: QueryRequest):
    # سيتم استبداله بنموذج حقيقي في المرحلة 3
    return {
        "response": f"Axon AI جاهز — المرحلة 1 مكتملة",
        "prompt": request.prompt
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("AI_PORT", 8080))
    logger.info(f"Axon AI يعمل على المنفذ {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
