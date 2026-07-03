"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";
import { Logo } from "./logo";
import { toApiErrorMessage } from "./ui/data-source-notice";
import { creativeLiftApi } from "@/lib/api-client";

type Mode = "login" | "register";

const emptyRegisterFields = { name: "", organizationName: "" };

export function LoginForm() {
  const router = useRouter();
  const [mode, setMode] = useState<Mode>("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [registerFields, setRegisterFields] = useState(emptyRegisterFields);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const isRegister = mode === "register";

  function toggleMode() {
    setMode((current) => (current === "login" ? "register" : "login"));
    setError(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitting(true);
    setError(null);
    try {
      if (isRegister) {
        await creativeLiftApi.register({
          email,
          password,
          name: registerFields.name,
          organization_name: registerFields.organizationName
        });
      } else {
        await creativeLiftApi.login(email, password);
      }
      router.push("/app/dashboard");
    } catch (err) {
      setError(
        toApiErrorMessage(
          err,
          isRegister ? "Could not create your account. Please try again." : "Could not sign in. Please try again."
        )
      );
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-ink px-4 py-12 text-white">
      <div className="w-full max-w-md">
        <div className="mb-8 flex justify-center">
          <Logo />
        </div>
        <form className="panel grid gap-5 rounded-lg p-8" onSubmit={handleSubmit}>
          <div>
            <h1 className="text-xl font-semibold">{isRegister ? "Create your account" : "Sign in"}</h1>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              {isRegister
                ? "Set up your organization to start measuring creative performance."
                : "Sign in to access your measurement dashboard."}
            </p>
          </div>

          {isRegister ? (
            <label className="grid gap-2 text-sm text-slate-300">
              Your name
              <input
                autoComplete="name"
                className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) => setRegisterFields((current) => ({ ...current, name: event.target.value }))}
                required
                type="text"
                value={registerFields.name}
              />
            </label>
          ) : null}

          {isRegister ? (
            <label className="grid gap-2 text-sm text-slate-300">
              Organization name
              <input
                autoComplete="organization"
                className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
                onChange={(event) =>
                  setRegisterFields((current) => ({ ...current, organizationName: event.target.value }))
                }
                required
                type="text"
                value={registerFields.organizationName}
              />
            </label>
          ) : null}

          <label className="grid gap-2 text-sm text-slate-300">
            Email
            <input
              autoComplete="email"
              className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
              onChange={(event) => setEmail(event.target.value)}
              required
              type="email"
              value={email}
            />
          </label>

          <label className="grid gap-2 text-sm text-slate-300">
            Password
            <input
              autoComplete={isRegister ? "new-password" : "current-password"}
              className="rounded-md border border-white/10 bg-white/[0.03] px-3 py-3 text-white outline-none focus:border-cyan"
              minLength={isRegister ? 8 : undefined}
              onChange={(event) => setPassword(event.target.value)}
              required
              type="password"
              value={password}
            />
          </label>

          <button
            className="rounded-md bg-cyan px-5 py-3 font-semibold text-ink disabled:opacity-50"
            disabled={submitting}
            type="submit"
          >
            {submitting ? (isRegister ? "Creating account..." : "Signing in...") : isRegister ? "Create account" : "Sign in"}
          </button>

          {error ? (
            <div className="rounded-lg border border-red-400/30 bg-red-400/10 p-4 text-sm text-red-200">{error}</div>
          ) : null}

          <button
            className="text-sm text-slate-400 hover:text-cyan"
            onClick={toggleMode}
            type="button"
          >
            {isRegister ? "Already have an account? Sign in" : "New here? Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
