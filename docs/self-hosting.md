# Self-Hosting

## Storage Profiles

CreativeLift AI ships with two storage profiles:

- **memory** (default outside Docker): no database required, data resets on restart. This keeps `python3 -m pytest` and local API experiments dependency-free.
- **sqlalchemy** (the Docker profile): Postgres-backed persistence. `docker compose up` runs `alembic upgrade head` on boot and sets `RESOURCE_REPOSITORY_BACKEND=sqlalchemy`, so ingested events, Creative Treatments, experiments, audit logs, and event quality snapshots survive restarts. Reset the demo data with `docker compose down -v`.

Local (persistent profile):

```bash
cp .env.example .env
docker compose up --build
```

Local persistent profile without Docker (needs a reachable Postgres):

```bash
python3 -m pip install -e "apps/api[dev]"
export DATABASE_URL=postgresql+psycopg://creativelift:creativelift_dev@localhost:5432/creativelift
export RESOURCE_REPOSITORY_BACKEND=sqlalchemy
(cd apps/api && python3 -m alembic upgrade head)
(cd apps/api && python3 -m uvicorn app.main:app --port 8000)
```

Verify migrations against a disposable Postgres:

```bash
make migration-smoke        # starts the compose postgres and runs apps/api/tests/test_migrations.py
make test-sqlalchemy        # runs the SQLAlchemy backend tests on in-memory SQLite
```

With the sqlalchemy profile `/readyz` performs a real database ping and returns 503 while the database is unreachable.

Production checklist:

- managed Postgres with backups
- managed Redis
- TLS and domain routing
- secret manager
- separate API/web/worker services
- database migrations in deploy pipeline
- object storage for creative assets
- observability and error tracking
- retention policy
- rate limits and WAF

Deployment targets to document next:

- Railway
- Fly.io
- Render
- AWS
- GCP
- Kubernetes
