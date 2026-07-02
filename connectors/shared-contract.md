# Connector Contract

Every connector should expose:

```python
class Connector:
    def validate_config(self, config: dict) -> None: ...
    def pull(self, since: str | None = None) -> list[dict]: ...
    def normalize(self, raw: dict) -> dict: ...
```

Normalized records must include:

- `source`
- `record_type`
- `external_id`
- `occurred_at`
- `organization_id` when resolved
- `payload`

Connectors must never log secrets.
