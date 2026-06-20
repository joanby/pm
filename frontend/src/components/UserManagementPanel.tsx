"use client";

import { type FormEvent, useEffect, useState } from "react";
import { createUser, deleteUser, listUsers, updateUserRole, type UserSummary } from "@/lib/users";

type UserManagementPanelProps = {
  token: string;
  currentUserId: string;
  onClose: () => void;
};

export const UserManagementPanel = ({ token, currentUserId, onClose }: UserManagementPanelProps) => {
  const [users, setUsers] = useState<UserSummary[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");

  const refresh = async () => {
    try {
      setUsers(await listUsers(token));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al cargar usuarios");
    }
  };

  useEffect(() => {
    void refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleCreate = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      await createUser(token, username, password, displayName, "member");
      setUsername("");
      setPassword("");
      setDisplayName("");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear usuario");
    }
  };

  const handleToggleRole = async (user: UserSummary) => {
    setError(null);
    try {
      await updateUserRole(token, user.id, user.role === "admin" ? "member" : "admin");
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al actualizar rol");
    }
  };

  const handleDelete = async (user: UserSummary) => {
    setError(null);
    try {
      await deleteUser(token, user.id);
      await refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar usuario");
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 px-4">
      <div className="w-full max-w-2xl rounded-[32px] border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="font-display text-2xl font-semibold text-[var(--navy-dark)]">
            Gestión de usuarios
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold uppercase text-[var(--gray-text)] hover:text-[var(--navy-dark)]"
          >
            Cerrar
          </button>
        </div>

        {error ? (
          <p className="mb-4 rounded-[8px] border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <form onSubmit={handleCreate} className="mb-6 grid gap-3 sm:grid-cols-4">
          <input
            value={username}
            onChange={(event) => setUsername(event.target.value)}
            placeholder="usuario"
            aria-label="Nombre de usuario"
            required
            className="rounded-xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
          />
          <input
            value={displayName}
            onChange={(event) => setDisplayName(event.target.value)}
            placeholder="Nombre visible"
            aria-label="Nombre visible"
            required
            className="rounded-xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
          />
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            placeholder="contraseña"
            aria-label="Contraseña"
            required
            className="rounded-xl border border-[var(--stroke)] px-3 py-2 text-sm outline-none focus:border-[var(--primary-blue)]"
          />
          <button
            type="submit"
            data-testid="add-user-button"
            className="rounded-xl bg-[var(--secondary-purple)] px-3 py-2 text-sm font-semibold text-white transition hover:brightness-110"
          >
            Añadir
          </button>
        </form>

        <ul className="max-h-72 space-y-2 overflow-y-auto" data-testid="user-list">
          {users.map((user) => (
            <li
              key={user.id}
              className="flex items-center justify-between rounded-xl border border-[var(--stroke)] px-4 py-3"
            >
              <div>
                <p className="text-sm font-semibold text-[var(--navy-dark)]">
                  {user.display_name ?? user.username}
                </p>
                <p className="text-xs text-[var(--gray-text)]">
                  @{user.username} · {user.role}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={() => handleToggleRole(user)}
                  className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold uppercase text-[var(--navy-dark)] hover:border-[var(--primary-blue)]"
                >
                  {user.role === "admin" ? "Quitar admin" : "Hacer admin"}
                </button>
                {user.id !== currentUserId ? (
                  <button
                    type="button"
                    onClick={() => handleDelete(user)}
                    className="rounded-full border border-[var(--stroke)] px-3 py-1 text-xs font-semibold uppercase text-red-600 hover:border-red-300"
                  >
                    Eliminar
                  </button>
                ) : null}
              </div>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
};
