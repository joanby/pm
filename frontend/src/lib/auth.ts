"use client";

import { useState, useEffect, useCallback } from "react";

export type AuthSession = {
  id: string;
  username: string;
  displayName: string | null;
  role: "admin" | "member";
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

  const applySession = (data: {
    id: string;
    username: string;
    display_name: string | null;
    role: "admin" | "member";
    token: string;
  }) => {
    const authSession: AuthSession = {
      id: data.id,
      username: data.username,
      displayName: data.display_name,
      role: data.role,
      token: data.token,
    };
    setSession(authSession);
    localStorage.setItem("auth_session", JSON.stringify(authSession));
  };

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

        applySession(await response.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error de autenticación");
      } finally {
        setIsLoading(false);
      }
    },
    []
  );

  const register = useCallback(
    async (username: string, password: string, displayName: string) => {
      setIsLoading(true);
      setError(null);

      try {
        const response = await fetch("/api/auth/register", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ username, password, display_name: displayName }),
        });

        if (!response.ok) {
          const body = await response.json().catch(() => null);
          throw new Error(body?.detail ?? "No se pudo crear la cuenta");
        }

        applySession(await response.json());
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al registrarse");
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

  return { session, isLoading, error, login, register, logout };
};
