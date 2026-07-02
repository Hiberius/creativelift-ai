"use client";

export default function Error({ reset }: { error: Error; reset: () => void }) {
  return (
    <main className="min-h-screen bg-ink px-6 py-20 text-white">
      <section className="shell panel rounded-lg p-8">
        <h1 className="text-2xl font-semibold">Something needs attention.</h1>
        <p className="mt-3 max-w-xl text-sm text-slate-400">
          The interface hit an unexpected state. Try reloading the current view.
        </p>
        <button
          onClick={reset}
          className="mt-6 rounded-md bg-cyan px-4 py-2 text-sm font-semibold text-ink"
        >
          Retry
        </button>
      </section>
    </main>
  );
}
