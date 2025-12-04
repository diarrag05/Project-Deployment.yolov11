# Multi-stage Dockerfile for YOLOv11 Segmentation Platform
# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_api.txt .

# Create wheels
RUN pip install --user --no-cache-dir -r requirements_api.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

# Create app directories
RUN mkdir -p /app/uploads /app/labeled_data /app/models /app/reports /app/feedback_data /app/logs

# Copy application code
COPY . /app/

# Download model if it doesn't exist
RUN if [ ! -f /app/models/yolov8n-seg_trained.pt ]; then \
    python -c "from ultralytics import YOLO; YOLO('yolov8n-seg.pt')" \
    ; fi

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Expose port
EXPOSE 5000

# Run Flask app
CMD ["python", "app.py"]
