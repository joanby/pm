"use client";

import { useState, useEffect, useCallback } from "react";

type AuthSession = {
  username: string;
  token: string;
};

export const useAuth = () => {
  const [session, setSession] = useState<AuthSession | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem("auth_session");
    if (stored) {
      try {
        setSession(JSON.parse(stored));
      } catch {
        localStorage.removeItem("auth_session");
      }
    }
    setIsLoading(false);
  }, []);

  const login = useCallback(
    async (username: string, password: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/auth/login", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password }),
        });

        if (!response.ok) {
          throw new Error("Credenciales incorrectas");
        }

        const data = await response.json();
        const authSession: AuthSession = {
          username: data.username,
          token: data.token,
        };
        setSession(authSession);
        localStorage.setItem("auth_session", JSON.stringify(authSession));
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error de autenticación");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await fetch("/api/auth/logout", {
        method: "POST",
        headers: session ? { Authorization: `Bearer ${session.token}` } : undefined,
      });
    } catch {
      // Ignore errors on logout
    } finally {
      setSession(null);
      localStorage.removeItem("auth_session");
      setIsLoading(false);
    }
  }, [session]);

  return { session, isLoading, error, login, logout };
};
