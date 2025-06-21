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

# Set PATH for user installations during build
ENV PATH=/root/.local/bin:$PATH

# Copy requirements and install in builder stage
COPY requirements-production.txt .
RUN pip install --no-cache-dir --user --upgrade pip setuptools wheel --root-user-action=ignore
RUN pip install --no-cache-dir --user -r requirements-production.txt --root-user-action=ignore

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

# Verify imports work in production stage
RUN python -c "from google.adk.agents import SequentialAgent; from query_history_cloud import query_history; print('✅ All imports working in production stage')"

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

# Use a simple startup command that's more reliable
CMD ["python", "api_server.py"]
