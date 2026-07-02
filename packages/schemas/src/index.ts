export type ApprovalStatus = "draft" | "pending_review" | "approved" | "rejected" | "archived";
export type ExperimentStatus = "draft" | "running" | "paused" | "completed" | "invalidated";
export type EventName =
  | "impression"
  | "click"
  | "session_start"
  | "signup"
  | "lead"
  | "purchase"
  | "revenue"
  | "custom_conversion";

export interface CreativeTreatment {
  id: string;
  organizationId: string;
  briefId?: string;
  brandPackId?: string;
  name: string;
  objective: string;
  targetAudience: string;
  channel: string;
  placement?: string;
  angle?: string;
  hook?: string;
  cta?: string;
  offer?: string;
  copy?: string;
  mediaMetadata: Record<string, unknown>;
  aiGenerated: boolean;
  humanEdited: boolean;
  complianceStatus: string;
  approvalStatus: ApprovalStatus;
  metricsSnapshot: Record<string, unknown>;
}

export interface ExperimentVariant {
  key: string;
  creativeTreatmentId?: string;
  allocation: number;
  isControl?: boolean;
}

export interface Experiment {
  id: string;
  organizationId: string;
  name: string;
  hypothesis: string;
  primaryMetric: string;
  guardrailMetric?: string;
  variants: ExperimentVariant[];
  randomizationUnit: string;
  status: ExperimentStatus;
  channel?: string;
}

export interface ExperimentAssignment {
  experiment_id: string;
  unit_id: string;
  variant_key: string;
  creative_treatment_id?: string;
  allocation: number;
  is_control: boolean;
}

export interface CreativeLiftEvent {
  event_name: EventName;
  timestamp: string;
  anonymous_id?: string;
  user_id?: string;
  creative_treatment_id: string;
  experiment_id?: string;
  variant_id?: string;
  channel?: string;
  placement?: string;
  value?: number;
  currency?: string;
  properties?: Record<string, unknown>;
}

export interface EventHealth {
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
}

export interface ExperimentResult {
  experimentId: string;
  recommendation: "winner" | "loser" | "inconclusive" | "invalid_srm" | "needs_more_data";
  comparison: Record<string, number | string>;
  srm: Record<string, number | boolean>;
}

export interface ExperimentInsight {
  experiment_id: string;
  recommendation: string;
  winning_variant_key?: string | null;
  decision_summary: string;
  recommended_action: string;
  confidence_note: string;
  evidence: string[];
  next_steps: string[];
}
