"use client";

import { type FormEvent, useState } from "react";
import { changePassword } from "@/lib/users";

type ChangePasswordPanelProps = {
  token: string;
  onClose: () => void;
};

export const ChangePasswordPanel = ({ token, onClose }: ChangePasswordPanelProps) => {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (newPassword !== confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    try {
      await changePassword(token, currentPassword, newPassword);
      setSuccess(true);
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cambiar la contraseña");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-2xl border border-[var(--stroke)] bg-[var(--panel-strong)] p-8 shadow-[var(--shadow)] backdrop-blur-xl">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl font-semibold text-[var(--text)]">
            Cambiar contraseña
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold uppercase text-[var(--gray-text)] hover:text-[var(--text)]"
          >
            Cerrar
          </button>
        </div>

        {success ? (
          <p className="mb-4 rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300">
            Contraseña actualizada correctamente.
          </p>
        ) : null}

        {error ? (
          <p className="mb-4 rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-2 text-sm text-red-300">
            {error}
          </p>
        ) : null}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label htmlFor="currentPassword" className="block text-sm font-semibold text-[var(--text)] mb-2">
              Contraseña actual
            </label>
            <input
              id="currentPassword"
              type="password"
              value={currentPassword}
              onChange={(event) => setCurrentPassword(event.target.value)}
              required
              className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
            />
          </div>
          <div>
            <label htmlFor="newPassword" className="block text-sm font-semibold text-[var(--text)] mb-2">
              Nueva contraseña
            </label>
            <input
              id="newPassword"
              type="password"
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
              required
              className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
            />
          </div>
          <div>
            <label htmlFor="confirmPassword" className="block text-sm font-semibold text-[var(--text)] mb-2">
              Confirmar nueva contraseña
            </label>
            <input
              id="confirmPassword"
              type="password"
              value={confirmPassword}
              onChange={(event) => setConfirmPassword(event.target.value)}
              required
              className="w-full rounded-lg border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-3 text-sm text-[var(--text)] outline-none focus:border-[var(--primary-blue)] focus:shadow-[var(--glow-blue)]"
            />
          </div>
          <button
            type="submit"
            className="w-full rounded-lg bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold uppercase tracking-wide text-white transition hover:shadow-[var(--glow-purple)]"
          >
            Guardar nueva contraseña
          </button>
        </form>
      </div>
    </div>
  );
};
