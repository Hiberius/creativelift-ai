# Docker Notes

The root `docker-compose.yml` starts Postgres, Redis, FastAPI, and Next.js for local development.

Production deployments should provide managed Postgres/Redis, TLS termination, secret management, database backups, and separate worker autoscaling.
