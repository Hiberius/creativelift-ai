import Link from "next/link";

export default function NotFound() {
  return (
    <main className="min-h-screen bg-ink px-6 py-20 text-white">
      <section className="shell panel rounded-lg p-8">
        <h1 className="text-3xl font-semibold">Page not found</h1>
        <p className="mt-3 text-slate-400">This route is not part of the current CreativeLift AI build.</p>
        <Link className="mt-6 inline-flex rounded-md bg-cyan px-4 py-2 text-sm font-semibold text-ink" href="/">
          Go home
        </Link>
      </section>
    </main>
  );
}
