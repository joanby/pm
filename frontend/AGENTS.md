# Frontend MVP (estado actual)

## Propósito de este directorio

Este frontend implementa un demo funcional de tablero Kanban en Next.js. Actualmente funciona de forma local y autónoma (sin backend real), y sirve como base para la integración progresiva definida en `docs/PLAN.md`.

## Stack técnico

- Next.js 16 (App Router)
- React 19
- TypeScript
- Tailwind CSS 4
- DnD con `@dnd-kit`

## Estructura principal

- `src/app/`
  - `page.tsx`: renderiza el tablero (`KanbanBoard`) en `/`.
  - `layout.tsx`: layout global y fuentes.
  - `globals.css`: estilos globales y variables de color.
- `src/components/`
  - `KanbanBoard.tsx`: estado del tablero y orquestación de drag and drop.
  - `KanbanColumn.tsx`: columna del tablero y operaciones locales.
  - `KanbanCard.tsx`: tarjeta individual sortable.
  - `KanbanCardPreview.tsx`: preview para `DragOverlay`.
  - `NewCardForm.tsx`: alta de nuevas tarjetas.
- `src/lib/kanban.ts`
  - tipos (`Card`, `Column`, `BoardData`)
  - datos iniciales `initialData`
  - lógica `moveCard` y `createId`
- `tests/`
  - pruebas E2E con Playwright.

## Estado funcional actual

- Implementado:
  - Visualización de tablero en `/`.
  - 5 columnas fijas renombrables.
  - Crear y eliminar tarjetas.
  - Mover tarjetas dentro de la misma columna y entre columnas (drag and drop).
- No implementado todavía:
  - Login.
  - Persistencia en backend/BD.
  - Chat lateral con IA.
  - Actualización de Kanban por IA.

## Brechas para integración (siguientes fases)

- Falta infraestructura de ejecución unificada con backend en Docker.
- Falta reemplazar `initialData` en memoria por lectura/escritura vía API.
- Falta modelo de sesión para login simulado con `user/password`.
- Falta endpoint backend para operaciones Kanban persistentes.
- Falta integración de chat IA y aplicación de salidas estructuradas al tablero.

## Estado de datos y persistencia

- El estado del board vive en memoria (`useState`) dentro de `KanbanBoard`.
- Los datos iniciales se cargan desde `initialData` en `src/lib/kanban.ts`.
- No hay llamadas API ni persistencia en SQLite en esta fase.

## Pruebas disponibles

- Unitarias/componentes (Vitest + Testing Library):
  - `src/lib/kanban.test.ts`
  - `src/components/KanbanBoard.test.tsx`
- Integración E2E (Playwright):
  - `tests/kanban.spec.ts`

## Comandos de trabajo

Desde `frontend/`:

- `npm run dev`: entorno local de desarrollo.
- `npm run build`: build de producción.
- `npm run start`: ejecutar build.
- `npm run test:unit`: pruebas unitarias.
- `npm run test:e2e`: pruebas de integración E2E.
- `npm run test:all`: suite completa (`unit + e2e`).

## Convenciones para agentes

- Mantener simplicidad; no introducir arquitectura extra sin necesidad.
- Preservar la UX visual del tablero actual durante la integración con backend.
- Toda nueva funcionalidad debe venir acompañada de pruebas unitarias e integración.
- Usar `user/password` como credenciales simuladas cuando se implemente login (Parte 4).
