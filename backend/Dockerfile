FROM python:3.14-slim

WORKDIR /app

# Install uv (official binary, no pip overhead)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy project files
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev || uv sync --no-dev

COPY app ./app
COPY locales ./locales

# Non-root user for defense-in-depth (F-04-006, F-10-001)
RUN groupadd --gid 1001 appgroup && \
    useradd --uid 1001 --gid appgroup --no-create-home --shell /bin/false appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Run with uvicorn
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
