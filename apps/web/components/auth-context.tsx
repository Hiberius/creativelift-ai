"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import { ApiRequestError, AuthSession, creativeLiftApi } from "@/lib/api-client";

type AuthStatus = "loading" | "authenticated" | "demo" | "unauthenticated";

interface AuthContextValue {
  status: AuthStatus;
  session: AuthSession | null;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

/**
 * Resolves the current identity on mount:
 *  1. GET /v1/auth/session — a real logged-in human, cookie-backed.
 *  2. If that 401s, GET /v1/me — the dev/demo principal FastAPI grants
 *     when no auth is configured (non-production only).
 *  3. If both fail, there is no way to use the app: redirect to /login.
 *
 * This mirrors the API's own fallback order in `get_principal`, so the
 * web app never blocks local/demo usage while still gating access once
 * real auth is enforced (production).
 */
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const [status, setStatus] = useState<AuthStatus>("loading");
  const [session, setSession] = useState<AuthSession | null>(null);

  const resolveIdentity = useCallback(async () => {
    setStatus("loading");
    try {
      const activeSession = await creativeLiftApi.getAuthSession();
      setSession(activeSession);
      setStatus("authenticated");
      return;
    } catch (err) {
      if (!(err instanceof ApiRequestError) || err.status !== 401) {
        // Unexpected failure (network, 5xx): don't lock the user out on a hiccup.
        setSession(null);
        setStatus("demo");
        return;
      }
    }

    try {
      await creativeLiftApi.getMe();
      setSession(null);
      setStatus("demo");
    } catch (err) {
      setSession(null);
      setStatus("unauthenticated");
      if (err instanceof ApiRequestError && err.status === 401) {
        router.push("/login");
      }
    }
  }, [router]);

  useEffect(() => {
    void resolveIdentity();
  }, [resolveIdentity]);

  const logout = useCallback(async () => {
    try {
      await creativeLiftApi.logout();
    } finally {
      setSession(null);
      setStatus("unauthenticated");
      router.push("/login");
    }
  }, [router]);

  const value = useMemo<AuthContextValue>(
    () => ({ status, session, refresh: resolveIdentity, logout }),
    [status, session, resolveIdentity, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuthSession(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthSession must be used within an AuthProvider");
  }
  return context;
}
