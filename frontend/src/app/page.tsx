"use client";

import { useState } from "react";
import { useAuth } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";
import { KanbanBoard } from "@/components/KanbanBoard";
import { ChangePasswordPanel } from "@/components/ChangePasswordPanel";

export default function Home() {
  const { session, isLoading, error, login, register, logout } = useAuth();
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="font-mono text-sm text-[var(--gray-text)]">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return (
      <LoginForm onLogin={login} onRegister={register} isLoading={isLoading} error={error} />
    );
  }

  return (
    <div className="min-h-screen">
      <div className="fixed top-4 right-4 z-50 flex items-center gap-2">
        <button
          onClick={() => setIsChangingPassword(true)}
          className="rounded-lg border border-[var(--stroke)] bg-[var(--panel)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] backdrop-blur-xl transition hover:text-[var(--text)] hover:border-[var(--primary-blue)]"
        >
          Cambiar contraseña
        </button>
        <button
          onClick={logout}
          className="rounded-lg border border-[var(--stroke)] bg-[var(--panel)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] backdrop-blur-xl transition hover:text-[var(--text)] hover:border-[var(--accent-yellow)]"
        >
          Cerrar sesión
        </button>
      </div>
      <KanbanBoard userId={session.id} token={session.token} role={session.role} />
      {isChangingPassword ? (
        <ChangePasswordPanel
          token={session.token}
          onClose={() => setIsChangingPassword(false)}
        />
      ) : null}
    </div>
  );
}

