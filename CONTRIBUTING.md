# Contributing to CreativeLift AI

Thanks for helping build an open-source measurement layer for AI marketing.

## Development Principles

- Treat Creative Treatment lineage as the product center.
- Prefer privacy-first, self-hostable defaults.
- Mark scaffolds honestly when an integration is not live.
- Add tests for statistical behavior and ingestion contracts.
- Keep tenant isolation visible in models, services, and docs.

## Local Workflow

```bash
make setup
make test
make lint
docker compose up --build
```

## Pull Requests

Every PR should include:

- What changed and why.
- Screenshots for UI changes.
- Test coverage or a clear reason tests are not applicable.
- Security/privacy impact notes for ingestion, auth, connectors, or data retention.

## Labels

See `docs/labels.md` for suggested GitHub labels.
