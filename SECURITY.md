# Security Policy

CreativeLift AI is built for privacy-first, self-hosted marketing measurement.

## Supported Versions

`v0.1.x` is an MVP release line. Security reports are welcome for all published versions.

## Reporting a Vulnerability

Please do not open public issues for sensitive reports. Email the future maintainer contact listed by your deployment owner. Until a public security mailbox is created, self-hosters should route reports through their internal security owner.

## Secure Defaults

- No secrets are committed.
- API keys are hashed; only prefixes are displayed.
- Request IDs are attached to responses and logs.
- CORS is allowlist-based.
- Event ingestion has idempotency and rate-limit hooks.
- Multi-tenant tables include `organization_id`.
- RLS-ready docs and migration notes are included.

This project does not provide legal advice. Users are responsible for marketing, privacy, advertising, sector-specific, and AI disclosure compliance.
