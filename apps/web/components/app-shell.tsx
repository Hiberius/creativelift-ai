import Link from "next/link";
import { BookOpen, ChevronDown, Code2, Github } from "lucide-react";
import { appNavItems } from "@/lib/site-data";
import { Logo } from "./logo";

export function AppShell({ children, title }: { children: React.ReactNode; title: string }) {
  return (
    <div className="min-h-screen bg-ink text-white">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-72 border-r border-white/10 bg-black/35 p-5 xl:block">
        <Logo />
        <p className="mt-5 border-b border-white/10 pb-6 text-sm leading-6 text-slate-400">
          Open-source AI marketing measurement platform
        </p>
        <nav className="mt-5 grid gap-1">
          {appNavItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 rounded-md px-3 py-3 text-sm text-slate-300 hover:bg-cyan/10 hover:text-cyan"
            >
              <item.icon className="h-5 w-5" />
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="absolute bottom-5 left-5 right-5 grid gap-3 border-t border-white/10 pt-5 text-sm text-slate-300">
          <Link className="flex items-center gap-3" href="/open-source">
            <Code2 className="h-5 w-5" />
            Open Source
          </Link>
          <Link className="flex items-center gap-3" href="/github">
            <Github className="h-5 w-5" />
            GitHub
          </Link>
        </div>
      </aside>
      <div className="xl:pl-72">
        <header className="sticky top-0 z-20 border-b border-white/10 bg-ink/80 backdrop-blur-xl">
          <div className="flex h-16 items-center justify-between px-4 md:px-6">
            <div className="flex items-center gap-3">
              <div className="xl:hidden">
                <Logo />
              </div>
              <button className="hidden items-center gap-3 rounded-md border border-white/10 bg-white/[0.03] px-4 py-2 text-sm text-slate-200 md:flex">
                Growth Lab Inc.
                <ChevronDown className="h-4 w-4" />
              </button>
            </div>
            <div className="flex items-center gap-5 text-sm">
              <span className="hidden items-center gap-2 text-slate-300 sm:flex">
                <span className="status-dot" />
                All systems operational
              </span>
              <Link className="flex items-center gap-2 text-slate-300 hover:text-white" href="/docs">
                <BookOpen className="h-5 w-5" />
                Docs
              </Link>
            </div>
          </div>
        </header>
        <main className="px-4 py-6 md:px-6">
          <div className="mb-5 flex items-center justify-between">
            <h1 className="text-2xl font-semibold">{title}</h1>
            <Link className="rounded-md bg-cyan px-4 py-2 text-sm font-semibold text-ink" href="/app/briefs/new">
              New brief
            </Link>
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}
