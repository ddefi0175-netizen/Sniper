# Crypto Sniper - Multi-stage Production Dockerfile
# Build: docker build -t crypto-sniper .
# Run: docker run -p 8000:8000 --env-file .env crypto-sniper

# ============================================================
# Stage 1: Builder
# ============================================================
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


# ============================================================
# Stage 2: Production
# ============================================================
FROM python:3.11-slim as production

# Security: Run as non-root user
RUN groupadd -r sniper && useradd -r -g sniper sniper

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY --chown=sniper:sniper . .

# Remove unnecessary files
RUN rm -rf tests/ docs/ *.md .git/ .github/ __pycache__/ .pytest_cache/

# Environment configuration
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Expose port
EXPOSE 8000

# Switch to non-root user
USER sniper

# Start command
CMD ["uvicorn", "backend.ai_predict:app", "--host", "0.0.0.0", "--port", "8000"]
