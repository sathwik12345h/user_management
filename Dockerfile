# Base stage
FROM python:3.12-bookworm as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=true \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    QR_CODE_DIR=/myapp/qr_codes

WORKDIR /myapp

# Update system and install required packages (no forced libc-bin version)
RUN apt-get update \
    && apt-get upgrade -y \ 
    && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies in /.venv
COPY requirements.txt .
RUN python -m venv /.venv \
    && /.venv/bin/pip install --upgrade pip \
    && /.venv/bin/pip install -r requirements.txt

# Final runtime stage
FROM python:3.12-slim-bookworm as final

# Install minimal system dependencies if needed (no forced libc-bin install)
RUN apt-get update \
    && apt-get upgrade -y \  
    && apt-get install -y --no-install-recommends \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the base stage
COPY --from=base /.venv /.venv

# Set environment variables
ENV PATH="/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    QR_CODE_DIR=/myapp/qr_codes

WORKDIR /myapp

# Create and switch to non-root user
RUN useradd -m myuser
USER myuser

# Copy application code
COPY --chown=myuser:myuser . .

# Expose app port
EXPOSE 8000

# Entry point
ENTRYPOINT ["uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]