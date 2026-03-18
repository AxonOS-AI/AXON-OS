# ─────────────────────────────────────────────────────────────────
# File:       ai-container/Dockerfile
# Purpose:    Axon OS AI Runtime container image.
#             Completely separate from Ubuntu Base OS.
#             Runs Python AI workloads in an isolated environment.
# Layer:      AI Container
# Copyright:  (c) 2024 Abdullah — Axon OS Project (AGPL-3.0)
# ─────────────────────────────────────────────────────────────────

FROM python:3.11-slim

LABEL maintainer="Abdullah — Axon OS Project"
LABEL version="1.0.0"
LABEL org.axonos.layer="ai-container"

WORKDIR /axon

# System dependencies (minimal — no Ubuntu Base modification)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git \
    && rm -rf /var/lib/apt/lists/*

# Python AI libraries (CPU build — GPU variant handled separately)
RUN pip install --no-cache-dir \
    transformers>=4.35.0 \
    huggingface_hub \
    fastapi \
    uvicorn[standard] \
    numpy \
    psutil

# Directory structure
RUN mkdir -p /axon/models /axon/logs /axon/agents/state

# Copy source code
COPY assistant/ /axon/assistant/
COPY agents/    /axon/agents/
COPY libraries/ /axon/libraries/

# Volume: models are stored on host and mounted at runtime
VOLUME ["/axon/models"]

# REST API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python3", "/axon/assistant/server.py"]
