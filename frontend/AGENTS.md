# Frontend AGENTS.md

## Resumen actual

El frontend está construido con NextJS 16 y React 19. Usa Tailwind CSS 4 y `@dnd-kit` para la interacción de arrastrar y soltar en el tablero Kanban. Se exporta como sitio estático (`output: "export"`) y lo sirve el backend FastAPI en `/`.

`src/app/page.tsx` muestra `LoginForm` si no hay sesión, o `KanbanBoard` si el usuario ya inició sesión.

## Arquitectura del frontend

- `src/app/page.tsx` — monta `LoginForm` o `KanbanBoard` según `useAuth()`.
- `src/app/layout.tsx` — layout global y fuentes de Google.

- `src/components/LoginForm.tsx` — formulario de usuario/contraseña.

- `src/components/KanbanBoard.tsx`
  - Componente principal autenticado. Recibe `userId`, `token` y `role`.
  - Carga la lista de tableros del usuario (`listBoards`); si no tiene ninguno, crea uno por defecto.
  - Carga y guarda el contenido del tablero activo vía `lib/boards.ts`.
  - Renderiza `BoardSwitcher` para cambiar/crear/renombrar/eliminar tableros.
  - Muestra el botón "Gestionar usuarios" (abre `UserManagementPanel`) solo si `role === "admin"`.
  - Usa `DndContext` para drag & drop de tarjetas entre columnas.

- `src/components/BoardSwitcher.tsx`
  - Pestañas con los tableros del usuario; doble click para renombrar, botón "✕" para eliminar (oculto si solo queda un tablero), botón "+" para crear uno nuevo.

- `src/components/UserManagementPanel.tsx`
  - Modal solo accesible para administradores: lista usuarios, crea usuarios (`member` por defecto), alterna rol admin/member, elimina usuarios. Usa `lib/users.ts`.

- `src/components/KanbanColumn.tsx` / `KanbanCard.tsx` / `KanbanCardPreview.tsx` / `NewCardForm.tsx`
  - Igual que antes: columna con título editable y formulario de tarjeta, tarjeta arrastrable, vista previa de arrastre.

- `src/components/AiChatPanel.tsx`
  - Chat lateral. Envía `message`, `board_id` (del tablero activo) y `board` a `/api/ai/chat`; aplica `boardUpdate` si la IA lo devuelve.

- `src/lib/kanban.ts` — modelo `BoardData`/`Column`/`Card`, `moveCard`, `createId`.
- `src/lib/auth.ts` — hook `useAuth` (login/logout, sesión en `localStorage` con `id`, `username`, `displayName`, `role`, `token`).
- `src/lib/boards.ts` — cliente API de tableros (`listBoards`, `createBoard`, `getBoard`, `updateBoard`, `renameBoard`, `deleteBoard`).
- `src/lib/users.ts` — cliente API de usuarios (`listUsers`, `createUser`, `updateUserRole`, `deleteUser`); solo lo usa `UserManagementPanel`.

## Pruebas actuales

- `src/test/mockBoardApi.ts` — helper compartido que mockea `fetch` para `/api/boards*` y `/api/ai/chat` en los tests de Vitest.
- `src/components/KanbanBoard.test.tsx` y `KanbanBoard.integration.test.tsx` — renderizado de columnas, renombrado, alta/baja de tarjetas, respuestas del chat IA, visibilidad condicional de "Gestionar usuarios" según rol.
- `src/lib/kanban.test.ts` — lógica `moveCard`.
- `frontend/tests/*.spec.ts` (Playwright, contra el backend real en Docker en `localhost:8000`):
  - `auth.spec.ts` — login/logout.
  - `kanban.spec.ts` — carga de tablero, alta de tarjeta, mover tarjeta entre columnas.
  - `boards.spec.ts` — crear, cambiar y eliminar tableros.
  - `users.spec.ts` — un admin crea y elimina un usuario desde el panel de gestión.
  - `ai-chat.spec.ts` — el chat aplica una actualización real de OpenRouter (puede fallar de forma intermitente por el modelo gratuito).
