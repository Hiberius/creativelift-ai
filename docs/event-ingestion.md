# Event Ingestion

Endpoint:

`POST /v1/events/ingest`

Health endpoint:

`GET /v1/events/health`

Header:

```text
X-API-Key: dev-api-key
```

Supported events:

- impression
- click
- session_start
- signup
- lead
- purchase
- revenue
- custom_conversion

Required:

- `event_name`
- `timestamp`
- `anonymous_id` or `user_id`
- `creative_treatment_id`

Optional:

- `experiment_id`
- `variant_id`
- `channel`
- `placement`
- `value`
- `currency`
- `properties`

Use `Idempotency-Key` for retries.

The health endpoint returns event totals, experiment and variant coverage, conversion value coverage, event mix, channel mix, quality score, and warnings.

Tracking examples:

- `examples/sdk-tracking/browser-tracker.js`
- `examples/sdk-tracking/server-side-python.py`

Assignment endpoint:

```text
GET /v1/experiments/{experiment_id}/assign?unit_id=anon_123
```

Use the returned `variant_key` when sending experiment exposure or conversion events.

Example payload:

```json
{
  "events": [
    {
      "event_name": "purchase",
      "timestamp": "2026-06-28T10:00:00Z",
      "anonymous_id": "anon_123",
      "creative_treatment_id": "00000000-0000-0000-0000-000000000101",
      "value": 49,
      "currency": "USD",
      "properties": {
        "source": "checkout"
      }
    }
  ]
}
```
