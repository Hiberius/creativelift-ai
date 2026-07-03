interface SkeletonProps {
  className?: string;
}

/** Pulsing placeholder surface, coherent with the existing panel design system. */
export function Skeleton({ className = "" }: SkeletonProps) {
  return <div className={`animate-pulse rounded-md bg-white/[0.06] ${className}`} />;
}

/** Skeleton for the metric-card grid used across dashboard summaries. */
export function MetricGridSkeleton({ count = 6 }: { count?: number }) {
  return (
    <section className="grid gap-3 md:grid-cols-2 xl:grid-cols-6" aria-busy="true" aria-label="Loading metrics">
      {Array.from({ length: count }).map((_, index) => (
        <article key={index} className="panel rounded-lg p-4">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="mt-3 h-8 w-20" />
          <Skeleton className="mt-2 h-3 w-16" />
          <Skeleton className="mt-4 h-8 w-full" />
        </article>
      ))}
    </section>
  );
}

/** Skeleton for a detail panel header (title + hypothesis/objective line). */
export function DetailHeaderSkeleton() {
  return (
    <div aria-busy="true" aria-label="Loading details">
      <Skeleton className="h-7 w-64" />
      <Skeleton className="mt-3 h-4 w-full max-w-2xl" />
      <Skeleton className="mt-2 h-4 w-3/4 max-w-xl" />
    </div>
  );
}
