# Security Policy

CreativeLift AI is built for privacy-first, self-hosted marketing measurement.

## Supported Versions

`v0.1.x` is an MVP release line. Security reports are welcome for all published versions.

## Reporting a Vulnerability

Report vulnerabilities privately via GitHub Security Advisories:
https://github.com/Hiberius/creativelift-ai/security/advisories/new

Please do **not** open public issues for security reports. You can expect an
initial response within 7 days. Coordinated disclosure is appreciated: give us
a reasonable window to ship a fix before publishing details.

## Secure Defaults

- No secrets are committed.
- API keys are hashed; only prefixes are displayed.
- Request IDs are attached to responses and logs.
- CORS is allowlist-based.
- Event ingestion has idempotency and rate-limit hooks.
- Multi-tenant tables include `organization_id`.
- RLS-ready docs and migration notes are included.

This project does not provide legal advice. Users are responsible for marketing, privacy, advertising, sector-specific, and AI disclosure compliance.
