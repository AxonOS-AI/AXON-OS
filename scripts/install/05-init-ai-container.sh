#!/bin/bash
# =============================================================================
# Axon OS — 05-init-ai-container.sh
# =============================================================================
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under the Apache License, Version 2.0
# https://www.apache.org/licenses/LICENSE-2.0
# =============================================================================
# الوظيفة: تجهيز البنية الأساسية لـ AI Container
# قابل للاستئناف: نعم — يتخطى كل خطوة مكتملة مسبقاً
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

log_info()    { echo -e "${CYAN}[INFO]${RESET}  $*"; }
log_success() { echo -e "${GREEN}[OK]${RESET}    $*"; }
log_warn()    { echo -e "${YELLOW}[WARN]${RESET}  $*"; }
log_error()   { echo -e "${RED}[ERROR]${RESET} $*" >&2; }
log_section() {
  echo -e "\n${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
  echo -e "${BOLD}${CYAN}  $*${RESET}"
  echo -e "${BOLD}${CYAN}══════════════════════════════════════════${RESET}"
}

# ─────────────────────────────────────────────
# المسارات
# ─────────────────────────────────────────────
AXON_HOME="${HOME}/AxonOS"
AXON_STATE="${HOME}/.axon/state"
STEP_DONE="${AXON_STATE}/05-init-ai-container.done"
AI_DIR="${AXON_HOME}/ai-container"

# تحميل .env إن وجد
ENV_FILE="${AXON_HOME}/.env"
if [[ -f "${ENV_FILE}" ]]; then
  source "${ENV_FILE}"
fi

DOCKER_IMAGE="${DOCKER_IMAGE:-axon-ai:latest}"
CONTAINER_NAME="${DOCKER_CONTAINER_NAME:-axon-ai}"

# ─────────────────────────────────────────────
# فحص الاستئناف
# ─────────────────────────────────────────────
if [[ -f "${STEP_DONE}" ]]; then
  log_warn "AI Container مُجهَّز مسبقاً → تخطي"
  log_info "لإعادة التنفيذ: rm ${STEP_DONE}"
  exit 0
fi

log_section "Step 5 · تجهيز AI Container"

mkdir -p "${AXON_STATE}"

# ─────────────────────────────────────────────
# فحص Docker
# ─────────────────────────────────────────────
log_info "فحص Docker..."
if ! command -v docker &>/dev/null; then
  log_error "Docker غير مثبت — شغّل الخطوة 4 أولاً"
  exit 1
fi
log_success "Docker متاح"

# ─────────────────────────────────────────────
# إنشاء Dockerfile
# ─────────────────────────────────────────────
DOCKERFILE="${AI_DIR}/Dockerfile"
DOCKER_DONE="${AXON_STATE}/05-dockerfile.done"

if [[ -f "${DOCKER_DONE}" ]]; then
  log_warn "Dockerfile موجود → تخطي"
else
  log_info "إنشاء Dockerfile..."
  cat > "${DOCKERFILE}" << 'DOCKERFILE_CONTENT'
# =============================================================================
# Axon OS — AI Container Dockerfile
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

FROM python:3.12-slim

LABEL maintainer="Abdullah — Axon OS Project"
LABEL version="1.0.0"
LABEL description="Axon OS AI Container"

WORKDIR /axon-ai

# متغيرات البيئة
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV AXON_AI_HOME=/axon-ai

# تثبيت متطلبات النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# نسخ ملف المتطلبات
COPY requirements.txt .

# تثبيت مكتبات Python
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# نسخ سكربتات التشغيل
COPY assistant/ ./assistant/
COPY agents/ ./agents/

# منفذ التطبيق
EXPOSE 8080

# أمر التشغيل
CMD ["python", "assistant/main.py"]
DOCKERFILE_CONTENT

  log_success "Dockerfile تم إنشاؤه"
  echo "done" > "${DOCKER_DONE}"
fi

# ─────────────────────────────────────────────
# إنشاء requirements.txt
# ─────────────────────────────────────────────
REQ_FILE="${AI_DIR}/requirements.txt"
REQ_DONE="${AXON_STATE}/05-requirements.done"

if [[ -f "${REQ_DONE}" ]]; then
  log_warn "requirements.txt موجود → تخطي"
else
  log_info "إنشاء requirements.txt..."
  cat > "${REQ_FILE}" << 'EOF'
# Axon OS — AI Container Requirements
# Copyright (c) 2025 Abdullah — Axon OS Project

# Core AI
torch>=2.0.0
transformers>=4.30.0
accelerate>=0.20.0

# API & Server
fastapi>=0.100.0
uvicorn>=0.22.0
pydantic>=2.0.0

# Utilities
numpy>=1.24.0
psutil>=5.9.0
python-dotenv>=1.0.0
EOF

  log_success "requirements.txt تم إنشاؤه"
  echo "done" > "${REQ_DONE}"
fi

# ─────────────────────────────────────────────
# إنشاء سكربت تشغيل المساعد الأساسي
# ─────────────────────────────────────────────
MAIN_FILE="${AI_DIR}/assistant/main.py"
MAIN_DONE="${AXON_STATE}/05-main.done"

if [[ -f "${MAIN_DONE}" ]]; then
  log_warn "assistant/main.py موجود → تخطي"
else
  log_info "إنشاء assistant/main.py..."
  mkdir -p "${AI_DIR}/assistant"
  cat > "${MAIN_FILE}" << 'PYTHON_CONTENT'
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
PYTHON_CONTENT

  log_success "assistant/main.py تم إنشاؤه"
  echo "done" > "${MAIN_DONE}"
fi

# ─────────────────────────────────────────────
# إنشاء docker-compose.yml
# ─────────────────────────────────────────────
COMPOSE_FILE="${AI_DIR}/docker-compose.yml"
COMPOSE_DONE="${AXON_STATE}/05-compose.done"

if [[ -f "${COMPOSE_DONE}" ]]; then
  log_warn "docker-compose.yml موجود → تخطي"
else
  log_info "إنشاء docker-compose.yml..."

  # فحص GPU
  GPU_SECTION=""
  if command -v nvidia-smi &>/dev/null; then
    GPU_SECTION="    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]"
    log_info "GPU مكتشف — سيُستخدم في الحاوية"
  fi

  cat > "${COMPOSE_FILE}" << COMPOSE_CONTENT
# =============================================================================
# Axon OS — Docker Compose
# Copyright (c) 2025 Abdullah — Axon OS Project
# Licensed under Apache License 2.0
# =============================================================================

version: '3.8'

services:
  axon-ai:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: ${CONTAINER_NAME}
    image: ${DOCKER_IMAGE}
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - ./models:/axon-ai/models
      - ./libraries:/axon-ai/libraries
    environment:
      - AI_RUNTIME=\${AI_RUNTIME:-cpu}
      - AI_MAX_MEMORY=\${AI_MAX_MEMORY:-4096}
${GPU_SECTION}

networks:
  default:
    name: axon-network
COMPOSE_CONTENT

  log_success "docker-compose.yml تم إنشاؤه"
  echo "done" > "${COMPOSE_DONE}"
fi

# ─────────────────────────────────────────────
# حفظ حالة الاكتمال
# ─────────────────────────────────────────────
echo "completed=$(date '+%Y-%m-%dT%H:%M:%S')" > "${STEP_DONE}"

log_section "النتيجة"
log_success "✓ الخطوة 5 مكتملة — AI Container مُجهَّز"
log_info "لبناء الحاوية شغّل: cd ${AI_DIR} && docker compose build"
