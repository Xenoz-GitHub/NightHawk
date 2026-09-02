FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --upgrade pip && pip install --no-cache-dir .[dev]

COPY src ./src
RUN pip install -e .

FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/

# Config files (present at repo root; copied unconditionally so the image is
# valid even when built from a clean checkout).
COPY scope.yaml /app/scope.yaml
COPY .env.example /app/.env.example

# Run as an unprivileged user; /app/data is the persistent volume.
RUN groupadd -r nighthawk && useradd -r -g nighthawk -d /app nighthawk \
    && mkdir -p /app/data && chown -R nighthawk:nighthawk /app
USER nighthawk

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "uvicorn", "nighthawk.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
