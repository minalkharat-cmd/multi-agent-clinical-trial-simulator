# =============================================================================
# Multi-Agent Clinical Trial Simulator
# Production Docker Image
# =============================================================================

# Build stage for dependencies
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
        libpq-dev \
            && rm -rf /var/lib/apt/lists/*

            # Create virtual environment
            RUN python -m venv /opt/venv
            ENV PATH="/opt/venv/bin:$PATH"

            # Install Python dependencies
            COPY requirements.txt .
            RUN pip install --no-cache-dir --upgrade pip && \
                pip install --no-cache-dir -r requirements.txt


                # =============================================================================
                # Production stage
                # =============================================================================
                FROM python:3.11-slim as production

                # Set environment variables
                ENV PYTHONDONTWRITEBYTECODE=1 \
                    PYTHONUNBUFFERED=1 \
                        PYTHONPATH=/app \
                            APP_ENV=production

                            # Create non-root user for security
                            RUN groupadd --gid 1000 appgroup && \
                                useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

                                WORKDIR /app

                                # Install runtime dependencies only
                                RUN apt-get update && apt-get install -y --no-install-recommends \
                                    libpq5 \
                                        curl \
                                            && rm -rf /var/lib/apt/lists/* \
                                                && apt-get clean

                                                # Copy virtual environment from builder
                                                COPY --from=builder /opt/venv /opt/venv
                                                ENV PATH="/opt/venv/bin:$PATH"

                                                # Copy application code
                                                COPY --chown=appuser:appgroup . .

                                                # Create necessary directories
                                                RUN mkdir -p /app/logs /app/data /app/temp && \
                                                    chown -R appuser:appgroup /app

                                                    # Switch to non-root user
                                                    USER appuser

                                                    # Expose port
                                                    EXPOSE 8000

                                                    # Health check
                                                    HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
                                                        CMD curl -f http://localhost:8000/health || exit 1

                                                        # Default command - run with Gunicorn for production
                                                        CMD ["gunicorn", "src.api.main:app", \
                                                             "--bind", "0.0.0.0:8000", \
                                                                  "--workers", "4", \
                                                                       "--worker-class", "uvicorn.workers.UvicornWorker", \
                                                                            "--timeout", "120", \
                                                                                 "--keep-alive", "5", \
                                                                                      "--access-logfile", "-", \
                                                                                           "--error-logfile", "-", \
                                                                                                "--capture-output"]


                                                                                                # =============================================================================
                                                                                                # Development stage
                                                                                                # =============================================================================
                                                                                                FROM production as development

                                                                                                USER root

                                                                                                # Install development dependencies
                                                                                                RUN pip install --no-cache-dir \
                                                                                                    pytest \
                                                                                                        pytest-cov \
                                                                                                            pytest-asyncio \
                                                                                                                black \
                                                                                                                    isort \
                                                                                                                        flake8 \
                                                                                                                            mypy \
                                                                                                                                ipython
                                                                                                                                
                                                                                                                                # Switch back to non-root user
                                                                                                                                USER appuser
                                                                                                                                
                                                                                                                                # Development command with hot reload
                                                                                                                                CMD ["uvicorn", "src.api.main:app", \
                                                                                                                                     "--host", "0.0.0.0", \
                                                                                                                                          "--port", "8000", \
                                                                                                                                               "--reload"]
                                                                                                                                               
