# Build context is the REPOSITORY ROOT (see docker-compose.yml: context "."),
# so the image can install the standalone statistical services that the API
# imports at runtime (experiment_engine, bandit_service, uplift_service,
# mmm_service). All COPY paths below are relative to the repo root.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# API dependencies first so the layer caches on pyproject changes only.
COPY apps/api/pyproject.toml ./
RUN pip install --no-cache-dir .

# Statistical services consumed directly by the API.
COPY services/experiment-engine /tmp/services/experiment-engine
COPY services/bandit-service /tmp/services/bandit-service
COPY services/uplift-service /tmp/services/uplift-service
COPY services/mmm-service /tmp/services/mmm-service
RUN pip install --no-cache-dir \
      /tmp/services/experiment-engine \
      /tmp/services/bandit-service \
      /tmp/services/uplift-service \
      /tmp/services/mmm-service \
    && rm -rf /tmp/services

COPY apps/api/app ./app
COPY apps/api/alembic ./alembic
COPY apps/api/alembic.ini ./
# Connector adapters are loaded from disk by app/services/connector_sync.py.
COPY connectors ./connectors

RUN useradd --system --no-create-home --uid 10001 creativelift
USER creativelift

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/readyz')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
