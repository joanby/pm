import clsx from "clsx";
import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import type { Card, Column } from "@/lib/kanban";
import { KanbanCard } from "@/components/KanbanCard";
import { NewCardForm } from "@/components/NewCardForm";

type KanbanColumnProps = {
  column: Column;
  cards: Card[];
  accentIndex: number;
  onRename: (columnId: string, title: string) => void;
  onAddCard: (columnId: string, title: string, details: string) => void;
  onDeleteCard: (columnId: string, cardId: string) => void;
};

const ACCENTS = ["var(--accent-yellow)", "var(--primary-blue)", "var(--secondary-purple)"];

export const KanbanColumn = ({
  column,
  cards,
  accentIndex,
  onRename,
  onAddCard,
  onDeleteCard,
}: KanbanColumnProps) => {
  const { setNodeRef, isOver } = useDroppable({ id: column.id });
  const accent = ACCENTS[accentIndex % ACCENTS.length];

  return (
    <section
      ref={setNodeRef}
      style={{ borderTopColor: accent }}
      className={clsx(
        "flex min-h-[520px] flex-col rounded-2xl border border-[var(--stroke)] border-t-2 bg-[var(--panel)] p-4 shadow-[var(--shadow)] backdrop-blur-xl transition",
        isOver && "border-[var(--accent-yellow)] shadow-[var(--glow-yellow)]"
      )}
      data-testid={`column-${column.id}`}
    >
      <div className="flex items-center justify-between gap-3">
        <div className="flex min-w-0 flex-1 items-center gap-2">
          <span
            className="h-2 w-2 shrink-0 rounded-full"
            style={{ backgroundColor: accent, boxShadow: `0 0 12px ${accent}` }}
          />
          <input
            value={column.title}
            onChange={(event) => onRename(column.id, event.target.value)}
            className="w-full min-w-0 bg-transparent font-display text-lg font-semibold text-[var(--text)] outline-none"
            aria-label="Título de la columna"
          />
        </div>
        <span className="shrink-0 rounded-full bg-[var(--bg-deep)] px-2.5 py-1 font-mono text-xs font-semibold text-[var(--gray-text)]">
          {cards.length}
        </span>
      </div>
      <div className="mt-4 flex flex-1 flex-col gap-3">
        <SortableContext items={column.cardIds} strategy={verticalListSortingStrategy}>
          {cards.map((card) => (
            <KanbanCard
              key={card.id}
              card={card}
              onDelete={(cardId) => onDeleteCard(column.id, cardId)}
            />
          ))}
        </SortableContext>
        {cards.length === 0 ? (
          <div className="flex flex-1 items-center justify-center rounded-xl border border-dashed border-[var(--stroke)] px-3 py-6 text-center font-mono text-xs uppercase tracking-[0.2em] text-[var(--gray-text)]">
            Suelta una tarjeta aquí
          </div>
        ) : null}
      </div>
      <NewCardForm
        onAdd={(title, details) => onAddCard(column.id, title, details)}
      />
    </section>
  );
};
