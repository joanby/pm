# Frontend MVP (estado actual)

## Propósito de este directorio

Este frontend implementa un demo funcional de tablero Kanban en Next.js. Se compila con `output: "export"` y se sirve de forma estática desde el backend FastAPI en `/` (Parte 3).

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
  - `AiChatSidebar.tsx`: chat lateral con IA (Parte 10).
- `src/lib/auth.ts`
  - credenciales MVP, validación y sesión en `localStorage`
- `src/lib/kanban-api.ts`
  - cliente fetch para la API Kanban (`X-MVP-Username`)
- `src/lib/ai-api.ts`
  - cliente fetch para chat IA (`/api/ai/chat`, `/api/ai/history`)
- `src/lib/kanban.ts`
  - tipos (`Card`, `Column`, `BoardData`)
  - datos iniciales `initialData`
  - lógica `moveCard` y `createId`
- `tests/`
  - pruebas E2E con Playwright.

## Estado funcional actual

- Implementado:
  - Visualización de tablero en `/` (servido por backend vía Docker).
  - Login simulado en cliente con `user/password` (`src/lib/auth.ts`).
  - Carga y persistencia del tablero vía API (`src/lib/kanban-api.ts`).
  - Guard de acceso: el tablero solo se muestra con sesión activa.
  - Logout que invalida la sesión en cliente.
  - 5 columnas fijas renombrables.
  - Crear y eliminar tarjetas.
  - Mover tarjetas dentro de la misma columna y entre columnas (drag and drop).
  - Chat lateral con IA (`AiChatSidebar`) con historial, envío y estados de carga/error.
  - Actualización automática del tablero tras respuestas IA con cambios Kanban.

## Estado de datos y persistencia

- El tablero se carga desde `GET /api/board` al iniciar sesión.
- Las operaciones (renombrar, crear, borrar, mover) se sincronizan con la API backend.
- Header `X-MVP-Username` identifica al usuario demo en el backend.

## Pruebas disponibles

- Unitarias/componentes (Vitest + Testing Library):
  - `src/lib/auth.test.ts`
  - `src/lib/kanban.test.ts`
  - `src/lib/ai-api.test.ts`
  - `src/components/KanbanBoard.test.tsx`
  - `src/components/AiChatSidebar.test.tsx`
- Integración E2E (Playwright):
  - `tests/kanban.spec.ts` (dev server en `:3000`)
  - `npm run test:e2e:docker` (backend Docker en `:8000`, Parte 3)

## Comandos de trabajo

Desde `frontend/`:

- `npm run dev`: entorno local de desarrollo.
- `npm run build`: build de producción.
- `npm run start`: ejecutar build.
- `npm run test:unit`: pruebas unitarias.
- `npm run test:e2e`: pruebas E2E contra dev server (`:3000`).
- `npm run test:e2e:docker`: pruebas E2E contra backend Docker (`:8000`).
- `npm run test:all`: suite completa (`unit + e2e`).

## Convenciones para agentes

- Mantener simplicidad; no introducir arquitectura extra sin necesidad.
- Preservar la UX visual del tablero actual durante la integración con backend.
- Toda nueva funcionalidad debe venir acompañada de pruebas unitarias e integración.
- Usar `user/password` como credenciales simuladas cuando se implemente login (Parte 4).
