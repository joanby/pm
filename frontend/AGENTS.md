# Frontend AGENTS.md

## Resumen actual

El frontend está construido con NextJS 16 y React 19. Usa Tailwind CSS 4 y `@dnd-kit` para la interacción de arrastrar y soltar en el tablero Kanban.

El proyecto actual renderiza un componente principal `KanbanBoard` desde `src/app/page.tsx`.

## Arquitectura del frontend

- `src/app/page.tsx`
  - Exporta la página principal y monta `KanbanBoard`.

- `src/app/layout.tsx`
  - Define el layout global y carga las fuentes de Google.

- `src/components/KanbanBoard.tsx`
  - Componente del tablero principal.
  - Maneja el estado del tablero (`BoardData`) con columnas, tarjetas y operaciones de arrastre.
  - Controla la adición, eliminación y renombrado de tarjetas y columnas.
  - Usa `DndContext` para habilitar drag & drop.

- `src/components/KanbanColumn.tsx`
  - Representa una columna del tablero.
  - Tiene un campo de título editable, una lista de tarjetas y un formulario para crear nuevas tarjetas.
  - Usa `useDroppable` y `SortableContext`.

- `src/components/KanbanCard.tsx`
  - Representa una tarjeta individual.
  - Usa `useSortable` para drag & drop y permite eliminar la tarjeta.

- `src/components/NewCardForm.tsx`
  - Formulario de creación de tarjeta que puede abrirse y cerrarse.
  - Valida título obligatorio.

- `src/components/KanbanCardPreview.tsx`
  - Vista previa de la tarjeta mientras se arrastra.

- `src/lib/kanban.ts`
  - Modelo de datos `BoardData`, `Column`, `Card`.
  - Datos iniciales del tablero.
  - Lógica de ordenación y movimiento de tarjetas (`moveCard`).
  - Generador de IDs (`createId`).

## Pruebas actuales

- `src/components/KanbanBoard.test.tsx`
  - Verifica renderizado de columnas.
  - Comprueba renombrado de columna.
  - Comprueba creación y eliminación de tarjetas.

- `src/lib/kanban.test.ts`
  - Verifica la lógica `moveCard` para reordenar dentro de la misma columna.
  - Verifica mover tarjetas a otra columna.
  - Verifica soltar una tarjeta al final de otra columna.

## Estado actual

- El frontend funciona como demo estática del tablero Kanban.
- No hay backend implementado en `backend/` más allá de un placeholder.
- No existe aún integración con Docker ni con OpenRouter.
- No hay experiencia de login ni persistencia del tablero vía backend.

## Próximos pasos recomendados

1. Agregar backend FastAPI para servir la página y API.
2. Añadir login simulado y persistencia de tablero.
3. Conectar la UI con el backend y mover el estado del tablero al servidor.
4. Implementar llamadas de IA estructuradas a OpenRouter.
5. Añadir chat lateral y aplicar actualizaciones del tablero desde la IA.
