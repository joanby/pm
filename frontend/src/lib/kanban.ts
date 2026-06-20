export type Card = {
  id: string;
  title: string;
  details: string;
};

export type Column = {
  id: string;
  title: string;
  cardIds: string[];
};

export type BoardData = {
  columns: Column[];
  cards: Record<string, Card>;
};

export const initialData: BoardData = {
  columns: [
    { id: "col-backlog", title: "Pendientes", cardIds: ["card-1", "card-2"] },
    { id: "col-discovery", title: "Descubrimiento", cardIds: ["card-3"] },
    {
      id: "col-progress",
      title: "En Progreso",
      cardIds: ["card-4", "card-5"],
    },
    { id: "col-review", title: "Revisión", cardIds: ["card-6"] },
    { id: "col-done", title: "Hecho", cardIds: ["card-7", "card-8"] },
  ],
  cards: {
    "card-1": {
      id: "card-1",
      title: "Alinear temas del roadmap",
      details: "Redactar temas trimestrales con metas de impacto y métricas.",
    },
    "card-2": {
      id: "card-2",
      title: "Recopilar señales de clientes",
      details: "Revisar etiquetas de soporte, notas de ventas y bajas.",
    },
    "card-3": {
      id: "card-3",
      title: "Prototipar vista de analítica",
      details: "Bocetar el diseño inicial del panel y sus desgloses clave.",
    },
    "card-4": {
      id: "card-4",
      title: "Refinar el lenguaje de los estados",
      details: "Estandarizar las etiquetas de columna y el tono del tablero.",
    },
    "card-5": {
      id: "card-5",
      title: "Diseñar el formato de tarjeta",
      details: "Añadir jerarquía y espaciado para listas densas.",
    },
    "card-6": {
      id: "card-6",
      title: "Revisar microinteracciones",
      details: "Verificar estados de hover, foco y carga.",
    },
    "card-7": {
      id: "card-7",
      title: "Publicar página de marketing",
      details: "Copy final aprobado y paquete de recursos entregado.",
    },
    "card-8": {
      id: "card-8",
      title: "Cerrar sprint de onboarding",
      details: "Documentar notas de versión y compartir internamente.",
    },
  },
};

const isColumnId = (columns: Column[], id: string) =>
  columns.some((column) => column.id === id);

const findColumnId = (columns: Column[], id: string) => {
  if (isColumnId(columns, id)) {
    return id;
  }
  return columns.find((column) => column.cardIds.includes(id))?.id;
};

export const moveCard = (
  columns: Column[],
  activeId: string,
  overId: string
): Column[] => {
  const activeColumnId = findColumnId(columns, activeId);
  const overColumnId = findColumnId(columns, overId);

  if (!activeColumnId || !overColumnId) {
    return columns;
  }

  const activeColumn = columns.find((column) => column.id === activeColumnId);
  const overColumn = columns.find((column) => column.id === overColumnId);

  if (!activeColumn || !overColumn) {
    return columns;
  }

  const isOverColumn = isColumnId(columns, overId);

  if (activeColumnId === overColumnId) {
    if (isOverColumn) {
      const nextCardIds = activeColumn.cardIds.filter(
        (cardId) => cardId !== activeId
      );
      nextCardIds.push(activeId);
      return columns.map((column) =>
        column.id === activeColumnId
          ? { ...column, cardIds: nextCardIds }
          : column
      );
    }

    const oldIndex = activeColumn.cardIds.indexOf(activeId);
    const newIndex = activeColumn.cardIds.indexOf(overId);

    if (oldIndex === -1 || newIndex === -1 || oldIndex === newIndex) {
      return columns;
    }

    const nextCardIds = [...activeColumn.cardIds];
    nextCardIds.splice(oldIndex, 1);
    nextCardIds.splice(newIndex, 0, activeId);

    return columns.map((column) =>
      column.id === activeColumnId
        ? { ...column, cardIds: nextCardIds }
        : column
    );
  }

  const activeIndex = activeColumn.cardIds.indexOf(activeId);
  if (activeIndex === -1) {
    return columns;
  }

  const nextActiveCardIds = [...activeColumn.cardIds];
  nextActiveCardIds.splice(activeIndex, 1);

  const nextOverCardIds = [...overColumn.cardIds];
  if (isOverColumn) {
    nextOverCardIds.push(activeId);
  } else {
    const overIndex = overColumn.cardIds.indexOf(overId);
    const insertIndex = overIndex === -1 ? nextOverCardIds.length : overIndex;
    nextOverCardIds.splice(insertIndex, 0, activeId);
  }

  return columns.map((column) => {
    if (column.id === activeColumnId) {
      return { ...column, cardIds: nextActiveCardIds };
    }
    if (column.id === overColumnId) {
      return { ...column, cardIds: nextOverCardIds };
    }
    return column;
  });
};

export const createId = (prefix: string) => {
  const randomPart = Math.random().toString(36).slice(2, 8);
  const timePart = Date.now().toString(36);
  return `${prefix}-${randomPart}${timePart}`;
};
