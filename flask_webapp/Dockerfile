# Build stage
FROM python:3.13-alpine as builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    libffi-dev

# Install requirements first for layer caching
COPY requirements.txt .
RUN python -m pip install --user --no-cache-dir \
    --trusted-host pypi.python.org \
    --trusted-host pypi.org \
    --trusted-host files.pythonhosted.org \
    -r requirements.txt

# Final stage
FROM python:3.13-alpine

# Create secure user
RUN adduser -D -u 1000 flaskuser && \
    mkdir -p /app && \
    chown -R flaskuser:flaskuser /app

WORKDIR /app

# Copy from builder
COPY --from=builder --chown=flaskuser /root/.local /home/flaskuser/.local
COPY --chown=flaskuser . .

# Security hardening
RUN apk --no-cache upgrade && \
    find / -type d -name __pycache__ -exec rm -rf {} + && \
    chmod -R 550 /app && \
    chmod 750 /home/flaskuser/.local/bin/gunicorn

USER flaskuser
ENV PATH="/home/flaskuser/.local/bin:${PATH}"
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run with security flags
ENTRYPOINT ["gunicorn"]
CMD ["-b", "0.0.0.0:8000", \
     "--workers", "1", \
     "--threads", "4", \
     "--worker-class", "gthread", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "--log-level", "warning", \
     "main:app"]
