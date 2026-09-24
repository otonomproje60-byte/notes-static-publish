# Notes Static Publish - Multi-stage Docker build
FROM python:3.12-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Runtime stage
FROM python:3.12-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/data /app/notes /app/dist && \
    chown -R appuser:appuser /app && \
    apt-get update && apt-get install -y --no-install-recommends wget && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application code
COPY --chown=appuser:appuser publish.py .
COPY --chown=appuser:appuser templates/ templates/
COPY --chown=appuser:appuser static/ static/
COPY --chown=appuser:appuser source/ source/

# Copy any existing notes and dist (will be overridden by volumes)
COPY --chown=appuser:appuser notes/ notes/
COPY --chown=appuser:appuser dist/ dist/

USER appuser

# Expose ports
EXPOSE 5001 8080

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5001/healthz || exit 1

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DATABASE_PATH=/app/data/notes.db \
    NOTES_DIR=/app/notes \
    DIST_DIR=/app/dist \
    TEMPLATES_DIR=/app/templates \
    STATIC_DIR=/app/static

# Default command runs both API and static file server
CMD ["sh", "-c", "python source/api/app.py & python -m http.server 8080 --directory /app/dist"]