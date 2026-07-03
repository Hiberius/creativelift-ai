import { AlertTriangle, RefreshCcw } from "lucide-react";

interface DemoDataBadgeProps {
  label?: string;
}

/**
 * Discrete badge shown next to a section title whenever the panel is
 * displaying local fallback/demo data instead of a real API response.
 * Never render this alongside real data — it must disappear the moment
 * a fetch succeeds.
 */
export function DemoDataBadge({ label = "Demo data" }: DemoDataBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-md border border-amber-400/30 bg-amber-400/10 px-2 py-1 text-xs font-medium text-amber-300">
      <span className="h-1.5 w-1.5 rounded-full bg-amber-400" />
      {label}
    </span>
  );
}

interface ApiErrorBannerProps {
  message: string;
  onRetry?: () => void;
  retrying?: boolean;
}

/**
 * Full-width banner shown when a fetch to the API failed. Always pairs
 * with an honest, non-technical message and an optional Retry action.
 * Never surface raw fetch/network errors (e.g. "Failed to fetch") — pass
 * a human-readable message instead.
 */
export function ApiErrorBanner({ message, onRetry, retrying = false }: ApiErrorBannerProps) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-start gap-2">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
        <span>{message}</span>
      </div>
      {onRetry ? (
        <button
          className="inline-flex w-fit shrink-0 items-center rounded-md border border-red-400/30 px-3 py-1.5 text-xs font-medium text-red-100 hover:bg-red-400/10 disabled:opacity-50"
          disabled={retrying}
          onClick={onRetry}
          type="button"
        >
          <RefreshCcw className={`mr-1.5 h-3.5 w-3.5 ${retrying ? "animate-spin" : ""}`} />
          {retrying ? "Retrying..." : "Retry"}
        </button>
      ) : null}
    </div>
  );
}

/**
 * Turns a caught error into a calm, user-facing message. Never leaks raw
 * browser/network error text (e.g. "Failed to fetch", "NetworkError").
 */
export function toApiErrorMessage(err: unknown, fallback: string): string {
  if (err instanceof Error && err.message && !/fetch/i.test(err.message)) {
    return err.message;
  }
  return fallback;
}
