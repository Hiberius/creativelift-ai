import type { CreativeLiftEvent, EventHealth, ExperimentAssignment, ExperimentInsight } from "@creativelift/schemas";

export interface CreativeLiftClientOptions {
  apiKey: string;
  baseUrl?: string;
}

export class CreativeLiftClient {
  private readonly apiKey: string;
  private readonly baseUrl: string;

  constructor(options: CreativeLiftClientOptions) {
    this.apiKey = options.apiKey;
    this.baseUrl = options.baseUrl ?? "http://localhost:8000";
  }

  async ingest(events: CreativeLiftEvent[], idempotencyKey?: string): Promise<{ accepted: number }> {
    const response = await fetch(`${this.baseUrl}/v1/events/ingest`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": this.apiKey,
        ...(idempotencyKey ? { "Idempotency-Key": idempotencyKey } : {})
      },
      body: JSON.stringify({ events })
    });
    if (!response.ok) {
      throw new Error(`CreativeLift ingestion failed: ${response.status}`);
    }
    return response.json() as Promise<{ accepted: number }>;
  }

  async assign(experimentId: string, unitId: string): Promise<ExperimentAssignment> {
    const response = await fetch(
      `${this.baseUrl}/v1/experiments/${experimentId}/assign?unit_id=${encodeURIComponent(unitId)}`,
      {
        method: "GET",
        headers: {
          "X-API-Key": this.apiKey
        }
      }
    );
    if (!response.ok) {
      throw new Error(`CreativeLift assignment failed: ${response.status}`);
    }
    return response.json() as Promise<ExperimentAssignment>;
  }

  async eventHealth(): Promise<EventHealth> {
    const response = await fetch(`${this.baseUrl}/v1/events/health`, {
      method: "GET",
      headers: {
        "X-API-Key": this.apiKey
      }
    });
    if (!response.ok) {
      throw new Error(`CreativeLift event health failed: ${response.status}`);
    }
    return response.json() as Promise<EventHealth>;
  }

  async experimentInsight(experimentId: string): Promise<ExperimentInsight> {
    const response = await fetch(`${this.baseUrl}/v1/experiments/${experimentId}/insights`, {
      method: "GET",
      headers: {
        "X-API-Key": this.apiKey
      }
    });
    if (!response.ok) {
      throw new Error(`CreativeLift experiment insight failed: ${response.status}`);
    }
    return response.json() as Promise<ExperimentInsight>;
  }
}
