"use client";

import { useEffect, useRef, useState } from "react";
import {
  DndContext,
  DragOverlay,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
  type DragEndEvent,
  type DragStartEvent,
} from "@dnd-kit/core";
import { AiChatPanel } from "@/components/AiChatPanel";
import { BoardSwitcher } from "@/components/BoardSwitcher";
import { UserManagementPanel } from "@/components/UserManagementPanel";
import { KanbanColumn } from "@/components/KanbanColumn";
import { KanbanCardPreview } from "@/components/KanbanCardPreview";
import { createId, initialData, moveCard, type BoardData } from "@/lib/kanban";
import {
  createBoard,
  deleteBoard,
  getBoard,
  listBoards,
  renameBoard,
  updateBoard,
  type BoardSummary,
} from "@/lib/boards";

type KanbanBoardProps = {
  userId: string;
  token: string;
  role: "admin" | "member";
};

const RENAME_SAVE_DEBOUNCE_MS = 500;

export const KanbanBoard = ({ userId, token, role }: KanbanBoardProps) => {
  const [boards, setBoards] = useState<BoardSummary[]>([]);
  const [activeBoardId, setActiveBoardId] = useState<string | null>(null);
  const [board, setBoard] = useState<BoardData>(() => initialData);
  const [activeCardId, setActiveCardId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isManagingUsers, setIsManagingUsers] = useState(false);
  const renameSaveTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: { distance: 6 },
    })
  );

  useEffect(() => {
    const loadBoards = async () => {
      try {
        let summaries = await listBoards(token);
        if (summaries.length === 0) {
          const created = await createBoard(token, "Mi tablero");
          summaries = [{ id: created.id, name: created.name, updated_at: created.updated_at }];
        }
        setBoards(summaries);
        setActiveBoardId(summaries[0].id);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar los tableros");
        setIsLoading(false);
      }
    };
    loadBoards();
  }, [token]);

  useEffect(() => {
    if (!activeBoardId) {
      return;
    }
    const loadBoard = async () => {
      setIsLoading(true);
      try {
        const data = await getBoard(token, activeBoardId);
        setBoard({ columns: data.columns, cards: data.cards });
      } catch (err) {
        setError(err instanceof Error ? err.message : "Error al cargar el tablero");
      } finally {
        setIsLoading(false);
      }
    };
    loadBoard();
  }, [token, activeBoardId]);

  useEffect(() => {
    return () => {
      if (renameSaveTimeout.current) {
        clearTimeout(renameSaveTimeout.current);
      }
    };
  }, []);

  const saveBoard = async (nextBoard: BoardData) => {
    if (!activeBoardId) {
      return;
    }
    try {
      await updateBoard(token, activeBoardId, nextBoard);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al guardar el tablero");
    }
  };

  const handleCreateBoard = async (name: string) => {
    try {
      const created = await createBoard(token, name);
      setBoards((current) => [...current, { id: created.id, name: created.name, updated_at: created.updated_at }]);
      setActiveBoardId(created.id);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al crear el tablero");
    }
  };

  const handleRenameBoard = async (boardId: string, name: string) => {
    try {
      await renameBoard(token, boardId, name);
      setBoards((current) => current.map((b) => (b.id === boardId ? { ...b, name } : b)));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al renombrar el tablero");
    }
  };

  const handleDeleteBoard = async (boardId: string) => {
    try {
      await deleteBoard(token, boardId);
      setBoards((current) => {
        const next = current.filter((b) => b.id !== boardId);
        if (boardId === activeBoardId) {
          setActiveBoardId(next[0]?.id ?? null);
        }
        return next;
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error al eliminar el tablero");
    }
  };

  const updateBoardState = (nextBoard: BoardData) => {
    setBoard(nextBoard);
    void saveBoard(nextBoard);
  };

  const handleDragStart = (event: DragStartEvent) => {
    setActiveCardId(event.active.id as string);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveCardId(null);

    if (!over || active.id === over.id) {
      return;
    }

    updateBoardState({
      ...board,
      columns: moveCard(board.columns, active.id as string, over.id as string),
    });
  };

  const handleRenameColumn = (columnId: string, title: string) => {
    const nextBoard = {
      ...board,
      columns: board.columns.map((column) =>
        column.id === columnId ? { ...column, title } : column
      ),
    };
    setBoard(nextBoard);

    if (renameSaveTimeout.current) {
      clearTimeout(renameSaveTimeout.current);
    }
    renameSaveTimeout.current = setTimeout(() => {
      void saveBoard(nextBoard);
    }, RENAME_SAVE_DEBOUNCE_MS);
  };

  const handleAddCard = (columnId: string, title: string, details: string) => {
    const id = createId("card");
    updateBoardState({
      ...board,
      cards: {
        ...board.cards,
        [id]: { id, title, details: details || "Sin detalles todavía." },
      },
      columns: board.columns.map((column) =>
        column.id === columnId
          ? { ...column, cardIds: [...column.cardIds, id] }
          : column
      ),
    });
  };

  const handleDeleteCard = (columnId: string, cardId: string) => {
    updateBoardState({
      ...board,
      cards: Object.fromEntries(
        Object.entries(board.cards).filter(([id]) => id !== cardId)
      ),
      columns: board.columns.map((column) =>
        column.id === columnId
          ? {
              ...column,
              cardIds: column.cardIds.filter((id) => id !== cardId),
            }
          : column
      ),
    });
  };

  const activeCard = activeCardId ? board.cards[activeCardId] : null;

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center px-4">
        <div className="rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-8 shadow-[var(--shadow)] backdrop-blur-xl">
          <p className="text-center font-mono text-sm text-[var(--gray-text)]">Cargando tablero...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="relative overflow-hidden">
      <div className="pointer-events-none absolute left-0 top-0 h-[420px] w-[420px] -translate-x-1/3 -translate-y-1/3 rounded-full bg-[radial-gradient(circle,_rgba(32,157,215,0.2)_0%,_rgba(32,157,215,0.04)_55%,_transparent_70%)]" />
      <div className="pointer-events-none absolute bottom-0 right-0 h-[520px] w-[520px] translate-x-1/4 translate-y-1/4 rounded-full bg-[radial-gradient(circle,_rgba(117,57,145,0.16)_0%,_rgba(117,57,145,0.04)_55%,_transparent_75%)]" />

      <main className="relative mx-auto flex min-h-screen max-w-[1500px] flex-col gap-10 px-6 pb-16 pt-12">
        <header className="flex flex-col gap-6 rounded-2xl border border-[var(--stroke)] bg-[var(--panel)] p-8 shadow-[var(--shadow)] backdrop-blur-xl">
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.4em] text-[var(--accent-yellow)]">
                Frogames Labs · Tablero Individual
              </p>
              <h1 className="mt-3 font-display text-4xl font-semibold text-[var(--text)]">
                Kanban Studio
              </h1>
              <p className="mt-3 max-w-xl text-sm leading-6 text-[var(--gray-text)]">
                Mantén el impulso a la vista. Renombra columnas, arrastra tarjetas
                entre fases y anota ideas rápidas sin perderte en configuraciones.
              </p>
            </div>
            <div className="flex items-start gap-3">
              <div className="rounded-xl border border-[var(--stroke)] bg-[var(--bg-deep)] px-5 py-4">
                <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-[var(--gray-text)]">
                  Enfoque
                </p>
                <p className="mt-2 text-lg font-semibold text-[var(--primary-blue)]">
                  Tus tableros. Tus reglas.
                </p>
              </div>
              {role === "admin" ? (
                <button
                  type="button"
                  onClick={() => setIsManagingUsers(true)}
                  className="rounded-lg border border-[var(--stroke)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-[var(--text)] transition hover:border-[var(--primary-blue)] hover:shadow-[var(--glow-blue)]"
                >
                  Gestionar usuarios
                </button>
              ) : null}
            </div>
          </div>

          <BoardSwitcher
            boards={boards}
            activeBoardId={activeBoardId}
            onSelect={setActiveBoardId}
            onCreate={handleCreateBoard}
            onRename={handleRenameBoard}
            onDelete={handleDeleteBoard}
          />

          <div className="flex flex-wrap items-center gap-4">
            {board.columns.map((column) => (
              <div
                key={column.id}
                className="flex items-center gap-2 rounded-full border border-[var(--stroke)] bg-[var(--bg-deep)] px-4 py-2 font-mono text-xs uppercase tracking-[0.2em] text-[var(--text)]"
              >
                <span className="h-2 w-2 rounded-full bg-[var(--accent-yellow)] shadow-[var(--glow-yellow)]" />
                {column.title}
              </div>
            ))}
          </div>
        </header>

        {error ? (
          <p className="rounded-lg border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-300">
            {error}
          </p>
        ) : null}

        <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
          <DndContext
            sensors={sensors}
            collisionDetection={closestCorners}
            onDragStart={handleDragStart}
            onDragEnd={handleDragEnd}
          >
            <section className="grid gap-6 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
              {board.columns.map((column, index) => (
                <KanbanColumn
                  key={column.id}
                  column={column}
                  accentIndex={index}
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

          {activeBoardId ? (
            <AiChatPanel
              board={board}
              boardId={activeBoardId}
              onBoardUpdate={setBoard}
              token={token}
            />
          ) : null}
        </div>
      </main>

      {isManagingUsers ? (
        <UserManagementPanel
          token={token}
          currentUserId={userId}
          onClose={() => setIsManagingUsers(false)}
        />
      ) : null}
    </div>
  );
};
