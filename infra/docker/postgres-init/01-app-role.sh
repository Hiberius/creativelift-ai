#!/bin/sh
# Creates the non-superuser runtime role for the API. Superusers bypass
# Postgres Row-Level Security, so the app must NOT connect as the bootstrap
# user. Runs only on first database initialization (empty volume).
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'creativelift_app') THEN
    CREATE ROLE creativelift_app LOGIN PASSWORD '${APP_DB_PASSWORD:-creativelift_app_dev}';
  END IF;
END \$\$;
SQL
