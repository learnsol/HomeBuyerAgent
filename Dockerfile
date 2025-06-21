# Single-stage build for reliable Cloud Run deployment
FROM python:3.10-slim

# Install system dependencies needed for google-adk and other packages
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

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FLASK_ENV=production
ENV PORT=8080

# Copy requirements and install Python dependencies
COPY requirements-production.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel --root-user-action=ignore
RUN pip install --no-cache-dir -r requirements-production.txt --root-user-action=ignore

# Verify critical packages are installed
RUN python -c "import flask; print('✅ Flask installed successfully')"
RUN python -c "from google.adk.agents import SequentialAgent; print('✅ Google ADK installed successfully')"

# Copy application code
COPY . .

# Verify imports work with application code
RUN python -c "import flask; print('✅ Flask working with app code')"
RUN python -c "from google.adk.agents import SequentialAgent; print('✅ ADK working with app code')"
RUN python -c "from query_history_cloud import query_history; print('✅ Query history imports working')"

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=60s --timeout=10s --start-period=30s --retries=2 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health', timeout=5)" || exit 1

# Use gunicorn for production WSGI server
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 api_server:app
