"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  closestCorners,
  DndContext,
  DragOverlay,
  PointerSensor,
  pointerWithin,
  useSensor,
  useSensors,
  type CollisionDetection,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import {
  getSessionUsername,
  isSessionActive,
  setSessionActive,
  validateCredentials,
} from "@/lib/auth";
import {
  createCard as createCardRequest,
  deleteCard as deleteCardRequest,
  fetchBoard,
  KanbanApiError,
  moveCardOnBoard,
  renameColumn as renameColumnRequest,
} from "@/lib/kanban-api";
import { getCardPlacement, moveCard, type BoardData } from "@/lib/kanban";

export const KanbanBoard = () => {
  const [board, setBoard] = useState<BoardData | null>(null);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(() => {
    if (!isSessionActive()) {
      return false;
    }
    return Boolean(getSessionUsername());
  });
  const [sessionUsername, setSessionUsername] = useState<string | null>(() =>
    getSessionUsername()
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState<string | null>(null);
  const [isLoadingBoard, setIsLoadingBoard] = useState(false);
  const [boardError, setBoardError] = useState<string | null>(null);
  const [isSyncing, setIsSyncing] = useState(false);
  const renameTimeouts = useRef<Record<string, number>>({});

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  const collisionDetection: CollisionDetection = (args) => {
    const pointerCollisions = pointerWithin(args);
    if (pointerCollisions.length > 0) {
      return pointerCollisions;
    }
    return closestCorners(args);
  };

  const loadBoard = useCallback(async (activeUsername: string) => {
    setIsLoadingBoard(true);
    setBoardError(null);
    try {
      const data = await fetchBoard(activeUsername);
      setBoard(data);
    } catch (error) {
      const message =
        error instanceof KanbanApiError
          ? "Unable to load your board from the server."
          : "Unexpected error while loading the board.";
      setBoardError(message);
      setBoard(null);
    } finally {
      setIsLoadingBoard(false);
    }
  }, []);

  useEffect(() => {
    const hasSession = isSessionActive();
    const storedUsername = getSessionUsername();
    if (hasSession && !storedUsername) {
      setSessionActive(false);
      setIsAuthenticated(false);
      setSessionUsername(null);
      return;
    }
    setIsAuthenticated(hasSession);
    setSessionUsername(storedUsername);
    if (hasSession && storedUsername) {
      void loadBoard(storedUsername);
    }
  }, [loadBoard]);

  useEffect(() => {
    return () => {
      Object.values(renameTimeouts.current).forEach((timeoutId) => {
        window.clearTimeout(timeoutId);
      });
    };
  }, []);

  const cardsById = useMemo(() => board?.cards ?? {}, [board?.cards]);

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id || !board || !sessionUsername) {
      return;
    }

    const previousBoard = board;
    const nextBoard: BoardData = {
      ...board,
      columns: moveCard(board.columns, active.id as string, over.id as string),
    };
    const placement = getCardPlacement(nextBoard.columns, active.id as string);

    if (!placement) {
      return;
    }

    setBoard(nextBoard);
    setIsSyncing(true);
    setBoardError(null);

    try {
      const syncedBoard = await moveCardOnBoard(
        sessionUsername,
        active.id as string,
        placement.columnId,
        placement.position
      );
      setBoard(syncedBoard);
    } catch {
      setBoard(previousBoard);
      setBoardError("Unable to save the card move. Your last change was reverted.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleRenameColumn = (columnId: string, title: string) => {
    if (!board || !sessionUsername) {
      return;
    }

    setBoard((prev) =>
      prev
        ? {
            ...prev,
            columns: prev.columns.map((column) =>
              column.id === columnId ? { ...column, title } : column
            ),
          }
        : prev
    );

    if (renameTimeouts.current[columnId]) {
      window.clearTimeout(renameTimeouts.current[columnId]);
    }

    renameTimeouts.current[columnId] = window.setTimeout(async () => {
      try {
        await renameColumnRequest(sessionUsername, columnId, title);
      } catch {
        setBoardError("Unable to save the column name.");
        await loadBoard(sessionUsername);
      }
    }, 400);
  };

  const handleAddCard = async (columnId: string, title: string, details: string) => {
    if (!board || !sessionUsername) {
      return;
    }

    setIsSyncing(true);
    setBoardError(null);

    try {
      const created = await createCardRequest(sessionUsername, columnId, {
        title,
        details: details || "No details yet.",
      });
      setBoard((prev) => {
        if (!prev) {
          return prev;
        }
        return {
          ...prev,
          cards: {
            ...prev.cards,
            [created.id]: created,
          },
          columns: prev.columns.map((column) =>
            column.id === columnId
              ? { ...column, cardIds: [...column.cardIds, created.id] }
              : column
          ),
        };
      });
    } catch {
      setBoardError("Unable to create the card.");
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDeleteCard = async (columnId: string, cardId: string) => {
    if (!board || !sessionUsername) {
      return;
    }

    const previousBoard = board;
    setBoard((prev) => {
      if (!prev) {
        return prev;
      }
      return {
        ...prev,
        cards: Object.fromEntries(
          Object.entries(prev.cards).filter(([id]) => id !== cardId)
        ),
        columns: prev.columns.map((column) =>
          column.id === columnId
            ? {
                ...column,
                cardIds: column.cardIds.filter((id) => id !== cardId),
              }
            : column
        ),
      };
    });

    setIsSyncing(true);
    setBoardError(null);

    try {
      await deleteCardRequest(sessionUsername, cardId);
    } catch {
      setBoard(previousBoard);
      setBoardError("Unable to delete the card.");
    } finally {
      setIsSyncing(false);
    }
  };

  const activeCard = activeCardId ? cardsById[activeCardId] : null;

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!validateCredentials(username, password)) {
      setAuthError("Invalid credentials. Use user/password.");
      return;
    }

    setSessionActive(true, username);
    setIsAuthenticated(true);
    setSessionUsername(username);
    setAuthError(null);
    setPassword("");
    await loadBoard(username);
  };

  const handleLogout = () => {
    setSessionActive(false);
    setIsAuthenticated(false);
    setSessionUsername(null);
    setBoard(null);
    setUsername("");
    setPassword("");
    setAuthError(null);
    setBoardError(null);
  };

  if (!isAuthenticated) {
    return (
      <main className="mx-auto flex min-h-screen max-w-xl items-center px-6 py-16">
        <section className="w-full rounded-3xl border border-[var(--stroke)] bg-white p-8 shadow-[var(--shadow)]">
          <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
            MVP Access
          </p>
          <h1 className="mt-3 font-display text-3xl font-semibold text-[var(--navy-dark)]">
            Sign in to Kanban Studio
          </h1>
          <p className="mt-2 text-sm text-[var(--gray-text)]">
            Use the demo credentials to continue.
          </p>

          <form className="mt-6 space-y-4" onSubmit={handleLogin}>
            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
                Username
              </span>
              <input
                value={username}
                onChange={(event) => setUsername(event.target.value)}
                className="w-full rounded-xl border border-[var(--stroke)] px-4 py-3 text-sm outline-none ring-[var(--primary-blue)] transition focus:ring-2"
                placeholder="user"
                autoComplete="username"
              />
            </label>

            <label className="block">
              <span className="mb-2 block text-xs font-semibold uppercase tracking-[0.2em] text-[var(--gray-text)]">
                Password
              </span>
              <input
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                className="w-full rounded-xl border border-[var(--stroke)] px-4 py-3 text-sm outline-none ring-[var(--primary-blue)] transition focus:ring-2"
                placeholder="password"
                autoComplete="current-password"
              />
            </label>

            {authError ? (
              <p role="alert" className="text-sm font-medium text-red-600">
                {authError}
              </p>
            ) : null}

            <button
              type="submit"
              className="w-full rounded-xl bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white transition hover:opacity-90"
            >
              Sign in
            </button>
          </form>
        </section>
      </main>
    );
  }

  if (isLoadingBoard || !board) {
    return (
      <main className="mx-auto flex min-h-screen max-w-xl items-center px-6 py-16">
        <section className="w-full rounded-3xl border border-[var(--stroke)] bg-white p-8 text-center shadow-[var(--shadow)]">
          {boardError ? (
            <>
              <p role="alert" className="text-sm font-medium text-red-600">
                {boardError}
              </p>
              {sessionUsername ? (
                <button
                  type="button"
                  onClick={() => void loadBoard(sessionUsername)}
                  className="mt-4 rounded-xl bg-[var(--secondary-purple)] px-4 py-3 text-sm font-semibold text-white"
                >
                  Retry
                </button>
              ) : null}
            </>
          ) : (
            <p className="text-sm text-[var(--gray-text)]">Loading your board...</p>
          )}
        </section>
      </main>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.25)_0%,_rgba(32,157,215,0.05)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.18)_0%,_rgba(117,57,145,0.05)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        {boardError ? (
          <p
            role="alert"
            className="rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
          >
            {boardError}
          </p>
        ) : null}

        <header className="flex flex-col gap-6 rounded-[32px] border border-[var(--stroke)] bg-white/80 p-8 shadow-[var(--shadow)] backdrop-blur">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
                Single Board Kanban
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--navy-dark)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Keep momentum visible. Rename columns, drag cards between stages,
                and capture quick notes without getting buried in settings.
              </p>
              {isSyncing ? (
                <p className="mt-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--primary-blue)]">
                  Saving...
                </p>
              ) : null}
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--surface)] px-5 py-4">
                <p className="text-xs font-semibold uppercase tracking-[0.25em] text-[var(--gray-text)]">
                  Focus
                </p>
                <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                  One board. Five columns. Zero clutter.
                </p>
              </div>
              <button
                type="button"
                onClick={handleLogout}
                className="rounded-xl border border-[var(--stroke)] bg-white px-4 py-2 text-sm font-semibold text-[var(--navy-dark)] transition hover:bg-[var(--surface)]"
              >
                Log out
              </button>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-[0.2em] text-[var(--navy-dark)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        <DndContext
          sensors={sensors}
          collisionDetection={collisionDetection}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <section className="grid gap-6 lg:grid-cols-5">
            {board.columns.map((column) => (
              <KanbanColumn
                key={column.id}
                column={column}
                cards={column.cardIds.map((cardId) => board.cards[cardId])}
                onRename={handleRenameColumn}
                onAddCard={handleAddCard}
                onDeleteCard={handleDeleteCard}
              />
            ))}
          </section>
          <DragOverlay>
            {activeCard ? (
              <div className="w-[260px]">
                <KanbanCardPreview card={activeCard} />
              </div>
            ) : null}
          </DragOverlay>
        </DndContext>
      </main>
    </div>
  );
};
