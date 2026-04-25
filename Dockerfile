# ── Nirnay Decision Intelligence Platform ──
# Multi-stage Docker build for production deployment

FROM python:3.11-slim AS base

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 nirnay

WORKDIR /app

# ── Install Python dependencies ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy application code ──
COPY --chown=nirnay:nirnay app.py .
COPY --chown=nirnay:nirnay utils/ ./utils/
COPY --chown=nirnay:nirnay pages/ ./pages/
COPY --chown=nirnay:nirnay .streamlit/ ./.streamlit/

# Switch to non-root user
USER nirnay

# Expose Streamlit default port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the app
ENTRYPOINT ["streamlit", "run", "app.py", \
    "--server.port=8501", \
    "--server.address=0.0.0.0", \
    "--server.headless=true", \
    "--browser.gatherUsageStats=false"]
