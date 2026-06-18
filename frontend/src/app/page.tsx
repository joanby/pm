"use client";

import { useAuth } from "@/lib/auth";
import { LoginForm } from "@/components/LoginForm";
import { KanbanBoard } from "@/components/KanbanBoard";

export default function Home() {
  const { session, isLoading, error, login, logout } = useAuth();

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-[#032147] via-[#209dd7]/10 to-[#753991]/10">
        <div className="text-center">
          <p className="text-sm text-[var(--gray-text)]">Cargando...</p>
        </div>
      </div>
    );
  }

  if (!session) {
    return <LoginForm onLogin={login} isLoading={isLoading} error={error} />;
  }

  return (
    <div className="min-h-screen">
      <button
        onClick={logout}
        className="fixed top-4 right-4 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:text-[var(--navy-dark)] hover:border-[var(--navy-dark)] z-50"
      >
        Cerrar sesión
      </button>
      <KanbanBoard />
    </div>
  );
}

