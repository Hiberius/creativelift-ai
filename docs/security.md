# Security

## Defaults

- no committed secrets
- `.env.example` only
- hashed API keys
- CORS allowlist
- request size limits
- request ID middleware
- audit log model
- tenant IDs on multi-tenant tables
- RBAC middleware scaffold
- rate limiting hooks

## RLS Roadmap

Postgres RLS should be enabled per tenant table with policies using an application-set `app.organization_id` setting. The schema is RLS-ready because every multi-tenant table includes `organization_id`.

## Responsible Disclosure

Use the process in `SECURITY.md`.
