# Multi-stage build for optimized Cloud Run deployment
FROM python:3.10-slim as builder

# Install build dependencies and system packages needed for google-adk
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    build-essential \
    pkg-config \
    libffi-dev \
    libssl-dev \
    graphviz \
    graphviz-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install in builder stage
COPY requirements-production.txt .
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --user -r requirements-production.txt

# Verify google-adk installation works
RUN python -c "from google.adk.agents import SequentialAgent; print('✅ Google ADK installed successfully')"

# Production stage
FROM python:3.10-slim

# Install runtime dependencies for google-adk
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Add local Python packages to PATH
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY . .

# Set environment variables for Cloud Run
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port (Cloud Run uses PORT environment variable)
EXPOSE 8080

# Health check optimized for Cloud Run
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=2 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Use gunicorn for production WSGI server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 api_server:app
