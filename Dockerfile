# Multi-stage build for optimized image size
# Stage 1: Builder stage
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install UV (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install Python dependencies using UV
RUN uv pip install --system -e .

# Stage 2: Runtime stage (smaller final image)
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app:$PATH"

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 hedgefund && \
    mkdir -p /app && \
    chown -R hedgefund:hedgefund /app

# Set working directory
WORKDIR /app

# Copy Python packages from builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=hedgefund:hedgefund . .

# Switch to non-root user
USER hedgefund

# Create directory for cache
RUN mkdir -p /app/.cache

# Set entrypoint
ENTRYPOINT ["python", "src/main.py"]

# Default command (can be overridden)
CMD ["--ticker", "AAPL", "--show-reasoning"]

