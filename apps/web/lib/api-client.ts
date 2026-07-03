export const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
export const demoApiKey = process.env.NEXT_PUBLIC_DEMO_API_KEY ?? "dev-api-key";

type ApiEnvelope<T> = { data: T };
type CollectionEnvelope<T> = { data: T[]; meta: { total: number; limit: number; offset: number } };

export type ApiKey = {
  id: string;
  organization_id: string;
  name: string;
  prefix: string;
  scopes: string[];
  created_at: string;
  raw_key?: string | null;
};

export type AuditLog = {
  id: string;
  organization_id: string;
  action: string;
  target_type: string;
  target_id?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type Organization = {
  id: string;
  name: string;
  slug: string;
  plan: string;
};

export type Principal = {
  organization_id: string;
  user_id?: string | null;
  role: string;
  scopes: string[];
};

export type MeResponse = {
  organization: Organization;
  principal: Principal;
};

export type AuthUser = {
  id: string;
  email: string;
  name: string;
};

export type AuthSession = {
  user: AuthUser;
  organization: Organization;
  role: string;
  expires_at: string;
};

export type RegisterInput = {
  email: string;
  name: string;
  password: string;
  organization_name: string;
  organization_slug?: string;
};

export type BrandPackInput = {
  name: string;
  voice?: string;
  guardrails?: Record<string, unknown>;
  prohibited_claims?: string[];
  regulated_category?: boolean;
};

export type BrandPack = BrandPackInput & {
  id: string;
  organization_id: string;
};

export type ClaimEvidenceInput = {
  claim: string;
  evidence_url: string;
  source_name?: string;
  notes?: string;
  brand_pack_id?: string | null;
  status?: string;
};

export type ClaimEvidence = ClaimEvidenceInput & {
  id: string;
  organization_id: string;
  created_at: string;
};

export type Brief = {
  id: string;
  organization_id: string;
  brand_pack_id?: string | null;
  name: string;
  objective: string;
  target_audience: string;
  channel: string;
  primary_kpi: string;
  body?: string;
  status: string;
};

export type BriefInput = {
  name: string;
  objective: string;
  target_audience: string;
  channel: string;
  primary_kpi: string;
  body?: string;
};

export type GeneratedVariant = {
  variant_id: string;
  headline: string;
  primary_text: string;
  landing_page_hero: string;
  email_subject: string;
  cta: string;
  angle: string;
  hypothesis: string;
  prompt_lineage: Record<string, unknown>;
};

export type CreativeTreatmentInput = {
  brief_id?: string | null;
  brand_pack_id?: string | null;
  name: string;
  objective: string;
  target_audience: string;
  channel: string;
  placement?: string;
  angle?: string;
  hook?: string;
  cta?: string;
  offer?: string;
  body_copy?: string;
  media_metadata?: Record<string, unknown>;
  ai_generated?: boolean;
  human_edited?: boolean;
  approved_claim_ids?: string[];
};

export type CreativeTreatment = CreativeTreatmentInput & {
  id: string;
  organization_id: string;
  compliance_status: string;
  approval_status: "draft" | "pending_review" | "approved" | "rejected" | "archived";
  metrics_snapshot: Record<string, unknown>;
};

export type ExperimentVariantInput = {
  key: string;
  creative_treatment_id?: string | null;
  allocation: number;
  is_control?: boolean;
};

export type ExperimentInput = {
  name: string;
  hypothesis: string;
  primary_metric: string;
  guardrail_metric?: string | null;
  variants: ExperimentVariantInput[];
  randomization_unit?: string;
  channel?: string;
  decision_rule?: string;
  minimum_detectable_effect?: number | null;
  notes?: string;
};

export type Experiment = ExperimentInput & {
  id: string;
  organization_id: string;
  status: "draft" | "running" | "paused" | "completed" | "invalidated";
  starts_at?: string | null;
  ends_at?: string | null;
};

export type ExperimentAssignment = {
  experiment_id: string;
  unit_id: string;
  variant_key: string;
  creative_treatment_id?: string | null;
  allocation: number;
  is_control: boolean;
};

export type ExperimentResult = {
  experiment_id: string;
  variants: Record<string, Record<string, number | string>>;
  comparison: Record<string, number | string>;
  srm: Record<string, number | boolean>;
  recommendation: string;
};

export type ExperimentInsight = {
  experiment_id: string;
  recommendation: string;
  winning_variant_key?: string | null;
  decision_summary: string;
  recommended_action: string;
  confidence_note: string;
  evidence: string[];
  next_steps: string[];
};

export type DemoScenario = {
  organization: Organization;
  brand_pack: BrandPack;
  brief: Brief;
  claim_evidence: ClaimEvidence;
  creatives: CreativeTreatment[];
  experiment: Experiment;
  ingestion: EventIngestResponse;
  event_health: EventHealth;
  result: ExperimentResult;
  insight: ExperimentInsight;
  results_url: string;
};

export type EventName = "impression" | "click" | "session_start" | "signup" | "lead" | "purchase" | "revenue" | "custom_conversion";

export type EventInput = {
  event_name: EventName;
  timestamp: string;
  anonymous_id?: string | null;
  user_id?: string | null;
  creative_treatment_id: string;
  experiment_id?: string | null;
  variant_id?: string | null;
  channel?: string | null;
  placement?: string | null;
  value?: number | null;
  currency?: string | null;
  properties?: Record<string, unknown>;
};

export type EventIngestResponse = {
  accepted: number;
  deduplicated: number;
  organization_id: string;
};

export type EventRecord = EventInput;

export type EventHealth = {
  total_events: number;
  unique_actors: number;
  events_with_experiment: number;
  events_with_variant: number;
  conversion_events: number;
  revenue: number;
  last_event_at?: string | null;
  event_counts: Record<string, number>;
  channel_counts: Record<string, number>;
  experiment_coverage: number;
  variant_coverage: number;
  revenue_coverage: number;
  quality_score: number;
  warnings: string[];
};

export type Connector = {
  id: string;
  organization_id: string;
  provider: string;
  display_name: string;
  status: string;
  config: Record<string, unknown>;
  last_sync_at?: string | null;
  created_at?: string;
  updated_at?: string;
};

export type MeasurementCard = {
  metric: string;
  value: number;
  delta?: number | null;
  unit: string;
};

export type MeasurementSummary = {
  organization_id: string;
  window: string;
  cards: MeasurementCard[];
  notes: string[];
};

/**
 * Error raised for non-2xx API responses. When the API returns the
 * structured `{error:{code,message}}` envelope, `code` and `message` are
 * populated from it so callers (e.g. the login form) can branch on a
 * stable error code instead of parsing prose.
 */
export class ApiRequestError extends Error {
  status: number;
  code?: string;

  constructor(status: number, message: string, code?: string) {
    super(message);
    this.name = "ApiRequestError";
    this.status = status;
    this.code = code;
  }
}

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl}${path}`, {
    ...init,
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-API-Key": demoApiKey,
      ...(init?.headers ?? {})
    }
  });
  if (!response.ok) {
    const detail = await response.text();
    let code: string | undefined;
    let message = detail || `Request failed with ${response.status}`;
    try {
      const parsed = JSON.parse(detail) as { error?: { code?: string; message?: string } };
      if (parsed?.error?.message) {
        message = parsed.error.message;
        code = parsed.error.code;
      }
    } catch {
      // Response body was not JSON; fall back to the raw text above.
    }
    throw new ApiRequestError(response.status, message, code);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const creativeLiftApi = {
  getMe: () => apiFetch<MeResponse>("/v1/me"),
  getAuthSession: () => apiFetch<AuthSession>("/v1/auth/session"),
  login: (email: string, password: string) =>
    apiFetch<AuthSession>("/v1/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    }),
  register: (payload: RegisterInput) =>
    apiFetch<AuthSession>("/v1/auth/register", {
      method: "POST",
      body: JSON.stringify(payload)
    }),
  logout: () =>
    apiFetch<{ status: string }>("/v1/auth/logout", {
      method: "POST"
    }),
  runDemoScenario: () =>
    apiFetch<DemoScenario>("/v1/demo/scenario", {
      method: "POST"
    }),
  createOrganization: (name: string, slug: string) =>
    apiFetch<Organization>("/v1/organizations", {
      method: "POST",
      body: JSON.stringify({ name, slug })
    }),
  listBrandPacks: () => apiFetch<BrandPack[]>("/v1/brand-packs"),
  createBrandPack: (brandPack: BrandPackInput) =>
    apiFetch<BrandPack>("/v1/brand-packs", {
      method: "POST",
      body: JSON.stringify(brandPack)
    }),
  listClaimEvidence: () => apiFetch<ClaimEvidence[]>("/v1/claim-evidence"),
  createClaimEvidence: (evidence: ClaimEvidenceInput) =>
    apiFetch<ClaimEvidence>("/v1/claim-evidence", {
      method: "POST",
      body: JSON.stringify(evidence)
    }),
  listApiKeys: () => apiFetch<ApiKey[]>("/v1/api-keys"),
  createApiKey: (name: string, scopes: string[] = ["events:write"]) =>
    apiFetch<ApiKey>("/v1/api-keys", {
      method: "POST",
      body: JSON.stringify({ name, scopes })
    }),
  deleteApiKey: (id: string) =>
    apiFetch<void>(`/v1/api-keys/${id}`, {
      method: "DELETE"
    }),
  listAuditLogs: () => apiFetch<AuditLog[]>("/v1/audit-logs"),
  listBriefs: () => apiFetch<Brief[]>("/v1/briefs"),
  createBrief: (brief: BriefInput) =>
    apiFetch<Brief>("/v1/briefs", {
      method: "POST",
      body: JSON.stringify(brief)
    }),
  generateVariants: (brief: BriefInput, n = 3) =>
    apiFetch<GeneratedVariant[]>("/v1/variants/generate", {
      method: "POST",
      body: JSON.stringify({
        brief,
        n,
        provider: "mock",
        temperature: 0.7
      })
    }),
  createCreativeTreatment: (treatment: CreativeTreatmentInput) =>
    apiFetch<CreativeTreatment>("/v1/creative-treatments", {
      method: "POST",
      body: JSON.stringify(treatment)
    }),
  listCreativeTreatments: () => apiFetch<CreativeTreatment[]>("/v1/creative-treatments"),
  getCreativeTreatment: (id: string) => apiFetch<CreativeTreatment>(`/v1/creative-treatments/${id}`),
  approveCreativeTreatment: (id: string, notes = "Approved from approval queue", claimEvidenceUrls: string[] = []) =>
    apiFetch<CreativeTreatment>(`/v1/creative-treatments/${id}/approve`, {
      method: "POST",
      body: JSON.stringify({ notes, claim_evidence_urls: claimEvidenceUrls })
    }),
  rejectCreativeTreatment: (id: string, notes = "Rejected from approval queue") =>
    apiFetch<CreativeTreatment>(`/v1/creative-treatments/${id}/reject`, {
      method: "POST",
      body: JSON.stringify({ notes })
    }),
  listExperiments: () => apiFetch<Experiment[]>("/v1/experiments"),
  getExperiment: (id: string) => apiFetch<Experiment>(`/v1/experiments/${id}`),
  createExperiment: (experiment: ExperimentInput) =>
    apiFetch<Experiment>("/v1/experiments", {
      method: "POST",
      body: JSON.stringify(experiment)
    }),
  setExperimentStatus: (id: string, status: "start" | "pause" | "complete") =>
    apiFetch<Experiment>(`/v1/experiments/${id}/${status}`, {
      method: "POST"
    }),
  assignExperimentVariant: (id: string, unitId: string) =>
    apiFetch<ExperimentAssignment>(`/v1/experiments/${id}/assign?unit_id=${encodeURIComponent(unitId)}`),
  getExperimentResults: (id: string) => apiFetch<ExperimentResult>(`/v1/experiments/${id}/results`),
  getExperimentInsights: (id: string) => apiFetch<ExperimentInsight>(`/v1/experiments/${id}/insights`),
  ingestEvents: (events: EventInput[], idempotencyKey?: string) =>
    apiFetch<EventIngestResponse>("/v1/events/ingest", {
      method: "POST",
      headers: idempotencyKey ? { "Idempotency-Key": idempotencyKey } : undefined,
      body: JSON.stringify({ events })
    }),
  listEvents: () => apiFetch<EventRecord[]>("/v1/events"),
  getEventHealth: () => apiFetch<EventHealth>("/v1/events/health"),
  getMeasurementSummary: async (window = "last_7_days") =>
    (await apiFetch<ApiEnvelope<MeasurementSummary>>(`/v1/measurement/summary?window=${encodeURIComponent(window)}`)).data,
  listConnectors: async () => (await apiFetch<CollectionEnvelope<Connector>>("/v1/connectors")).data,
  createConnector: async (provider: string, display_name: string, config: Record<string, unknown> = {}) =>
    (await apiFetch<ApiEnvelope<Connector>>("/v1/connectors", {
      method: "POST",
      body: JSON.stringify({ provider, display_name, config })
    })).data
};
