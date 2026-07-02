const CREATIVE_LIFT_API_URL = window.CREATIVE_LIFT_API_URL ?? "http://localhost:8000";
const CREATIVE_LIFT_API_KEY = window.CREATIVE_LIFT_API_KEY ?? "dev-api-key";

async function creativeLiftFetch(path, init = {}) {
  const response = await fetch(`${CREATIVE_LIFT_API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": CREATIVE_LIFT_API_KEY,
      ...(init.headers ?? {})
    }
  });
  if (!response.ok) {
    throw new Error(`CreativeLift request failed: ${response.status}`);
  }
  return response.json();
}

export async function assignCreativeLiftVariant({ experimentId, anonymousId }) {
  return creativeLiftFetch(`/v1/experiments/${experimentId}/assign?unit_id=${encodeURIComponent(anonymousId)}`);
}

export async function trackCreativeLiftEvent(event, idempotencyKey = `evt_${crypto.randomUUID()}`) {
  return creativeLiftFetch("/v1/events/ingest", {
    method: "POST",
    headers: { "Idempotency-Key": idempotencyKey },
    body: JSON.stringify({ events: [event] })
  });
}

export async function assignAndTrackImpression({ experimentId, anonymousId, channel = "landing_page", placement = "hero" }) {
  const assignment = await assignCreativeLiftVariant({ experimentId, anonymousId });
  await trackCreativeLiftEvent({
    event_name: "impression",
    timestamp: new Date().toISOString(),
    anonymous_id: anonymousId,
    experiment_id: experimentId,
    variant_id: assignment.variant_key,
    creative_treatment_id: assignment.creative_treatment_id,
    channel,
    placement,
    properties: { source: "browser_example" }
  });
  return assignment;
}

export async function trackClick({ experimentId, anonymousId, assignment, channel = "landing_page", placement = "hero_cta" }) {
  return trackCreativeLiftEvent({
    event_name: "click",
    timestamp: new Date().toISOString(),
    anonymous_id: anonymousId,
    experiment_id: experimentId,
    variant_id: assignment.variant_key,
    creative_treatment_id: assignment.creative_treatment_id,
    channel,
    placement,
    properties: { source: "browser_example" }
  });
}
