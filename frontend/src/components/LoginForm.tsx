"use client";

import { FormEvent, useState } from "react";

type LoginFormProps = {
  onLogin: (username: string, password: string) => void;
  onRegister: (username: string, password: string, displayName: string) => void;
  isLoading?: boolean;
  error?: string | null;
};

export const LoginForm = ({ onLogin, onRegister, isLoading = false, error }: LoginFormProps) => {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (mode === "login") {
      onLogin(username, password);
    } else {
      onRegister(username, password, displayName);
    }
  };

  const toggleMode = () => {
    setMode((current) => (current === "login" ? "register" : "login"));
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden px-4">
      <div className="pointer-events-none absolute left-1/2 top-0 h-[480px] w-[480px] -translate-x-1/2 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.22)_0%,_rgba(32,157,215,0.05)_55%,_transparent_75%)]" />
      <div className="pointer-events-none absolute bottom-0 right-1/4 h-[420px] w-[420px] translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.22)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <div className="relative w-full max-w-md rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-8 shadow-[var(--shadow)] backdrop-blur-xl">
        <div className="mb-8 text-center">
          <p className="font-mono text-[11px] uppercase tracking-[0.4em] text-[var(--accent-yellow)]">
            Frogames Labs
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--text)]">
            Kanban Studio
          </h1>
          <p className="mt-2 text-xs text-[var(--gray-text)]">
            Organiza tus proyectos de IA, código y matemáticas.
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="username" className="mb-2 block text-sm font-semibold text-[var(--text)]">
              Usuario
            </label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none transition focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
              disabled={isLoading}
            />
          </div>

          {mode === "register" ? (
            <div>
              <label htmlFor="displayName" className="mb-2 block text-sm font-semibold text-[var(--text)]">
                Nombre visible
              </label>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none transition focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
                disabled={isLoading}
              />
            </div>
          ) : null}

          <div>
            <label htmlFor="password" className="mb-2 block text-sm font-semibold text-[var(--text)]">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none transition focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
              disabled={isLoading}
            />
          </div>

          {error ? (
            <div className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-300">
              {error}
            </div>
          ) : null}

          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:shadow-[var(--glow-purple)] disabled:opacity-50"
          >
            {isLoading
              ? "Procesando..."
              : mode === "login"
                ? "Iniciar sesión"
                : "Crear cuenta"}
          </button>
        </form>

        <p className="mt-6 text-center text-xs text-[var(--gray-text)]">
          {mode === "login" ? "¿No tienes cuenta?" : "¿Ya tienes cuenta?"}{" "}
          <button
            type="button"
            onClick={toggleMode}
            className="font-semibold text-[var(--primary-blue)] hover:underline"
          >
            {mode === "login" ? "Regístrate" : "Inicia sesión"}
          </button>
        </p>
      </div>
    </div>
  );
};
