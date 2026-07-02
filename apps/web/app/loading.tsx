export default function Loading() {
  return (
    <main className="min-h-screen bg-ink px-6 py-20 text-white">
      <section className="shell grid gap-4">
        <div className="h-8 w-64 animate-pulse rounded bg-white/10" />
        <div className="h-48 animate-pulse rounded-lg bg-white/10" />
      </section>
    </main>
  );
}
