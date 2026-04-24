# ── Stage 1: slim Python runtime ──────────────────────────────────────────────
FROM python:3.11-slim AS base

# Prevents .pyc files and enables unbuffered logging (critical for Cloud Run)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# ── Install system deps ────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python deps (cached layer) ─────────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──────────────────────────────────────────────────────
COPY . .

# ── Cloud Run listens on $PORT ─────────────────────────────────────────────────
EXPOSE 8080

# ── Health check (Cloud Run will also probe /health) ──────────────────────────
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# ── Entrypoint ─────────────────────────────────────────────────────────────────
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port $PORT --workers 1"]
