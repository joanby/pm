"use client";

import { type FormEvent, useState } from "react";
import { type BoardSummary } from "@/lib/boards";

type BoardSwitcherProps = {
  boards: BoardSummary[];
  activeBoardId: string | null;
  onSelect: (boardId: string) => void;
  onCreate: (name: string) => void;
  onRename: (boardId: string, name: string) => void;
  onDelete: (boardId: string) => void;
};

export const BoardSwitcher = ({
  boards,
  activeBoardId,
  onSelect,
  onCreate,
  onRename,
  onDelete,
}: BoardSwitcherProps) => {
  const [isCreating, setIsCreating] = useState(false);
  const [newBoardName, setNewBoardName] = useState("");
  const [renamingId, setRenamingId] = useState<string | null>(null);
  const [renameValue, setRenameValue] = useState("");

  const handleCreateSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const name = newBoardName.trim();
    if (!name) {
      return;
    }
    onCreate(name);
    setNewBoardName("");
    setIsCreating(false);
  };

  const handleRenameSubmit = (event: FormEvent<HTMLFormElement>, boardId: string) => {
    event.preventDefault();
    const name = renameValue.trim();
    if (name) {
      onRename(boardId, name);
    }
    setRenamingId(null);
  };

  return (
    <div className="flex flex-wrap items-center gap-2" data-testid="board-switcher">
      {boards.map((board) =>
        renamingId === board.id ? (
          <form
            key={board.id}
            onSubmit={(event) => handleRenameSubmit(event, board.id)}
            className="flex items-center gap-1"
          >
            <input
              autoFocus
              value={renameValue}
              onChange={(event) => setRenameValue(event.target.value)}
              onBlur={() => setRenamingId(null)}
              className="rounded-full border border-[var(--primary-blue)] bg-[var(--bg-deep)] px-3 py-1.5 text-xs font-semibold text-[var(--text)] outline-none shadow-[var(--glow-blue)]"
            />
          </form>
        ) : (
          <div key={board.id} className="group flex items-center">
            <button
              type="button"
              onClick={() => onSelect(board.id)}
              onDoubleClick={() => {
                setRenamingId(board.id);
                setRenameValue(board.name);
              }}
              data-testid="board-tab"
              data-active={board.id === activeBoardId}
              className={
                board.id === activeBoardId
                  ? "rounded-full bg-[var(--primary-blue)] px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-white shadow-[var(--glow-blue)]"
                  : "rounded-full border border-[var(--stroke)] px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--text)]"
              }
            >
              {board.name}
            </button>
            {boards.length > 1 ? (
              <button
                type="button"
                aria-label={`Eliminar ${board.name}`}
                onClick={() => onDelete(board.id)}
                className="ml-1 text-xs text-[var(--gray-text)] opacity-0 transition group-hover:opacity-100 hover:text-red-400"
              >
                ✕
              </button>
            ) : null}
          </div>
        )
      )}

      {isCreating ? (
        <form onSubmit={handleCreateSubmit} className="flex items-center gap-1">
          <input
            autoFocus
            value={newBoardName}
            onChange={(event) => setNewBoardName(event.target.value)}
            onBlur={() => setIsCreating(false)}
            placeholder="Nombre del tablero"
            aria-label="Nombre del nuevo tablero"
            className="rounded-full border border-[var(--primary-blue)] bg-[var(--bg-deep)] px-3 py-1.5 text-xs font-semibold text-[var(--text)] outline-none shadow-[var(--glow-blue)]"
          />
        </form>
      ) : (
        <button
          type="button"
          onClick={() => setIsCreating(true)}
          className="rounded-full border border-dashed border-[var(--stroke)] px-4 py-1.5 text-xs font-semibold uppercase tracking-wide text-[var(--gray-text)] transition hover:border-[var(--primary-blue)] hover:text-[var(--primary-blue)]"
        >
          + Nuevo tablero
        </button>
      )}
    </div>
  );
};
