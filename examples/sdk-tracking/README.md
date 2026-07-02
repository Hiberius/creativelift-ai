# SDK Tracking Examples

Small local examples for wiring assignment and event ingestion.

Files:

- `browser-tracker.js`: browser-side assignment and impression/click tracking with `fetch`
- `server-side-python.py`: server-side conversion tracking with the Python SDK

Local demo defaults:

```text
CREATIVELIFT_API_URL=http://localhost:8000
CREATIVELIFT_API_KEY=dev-api-key
```

For production, do not expose privileged API keys in public browser code. Use a scoped public ingestion key or a server proxy.
