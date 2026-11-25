# Frontend AGENTS.md

## Resumen actual

El frontend está construido con NextJS 16 y React 19. Usa Tailwind CSS 4 y `@dnd-kit` para la interacción de arrastrar y soltar en el tablero Kanban. Se exporta como sitio estático (`output: "export"`) y lo sirve el backend FastAPI en `/`.

Tema visual oscuro ("enterprise + edgy"): fondo con rejilla sutil, paneles de cristal (`var(--panel)` + `backdrop-blur`), bordes y sombras con resplandor (`var(--glow-yellow)`, `var(--glow-blue)`, `var(--glow-purple)`) usando la paleta de marca de `globals.css`. Fuentes: `Space Grotesk` (display), `Manrope` (cuerpo), `JetBrains Mono` (etiquetas técnicas, vía `.font-mono` / `--font-mono`).

`src/app/page.tsx` muestra `LoginForm` si no hay sesión, o `KanbanBoard` si el usuario ya inició sesión.

## Arquitectura del frontend

- `src/app/page.tsx` — monta `LoginForm` o `KanbanBoard` según `useAuth()`.
- `src/app/layout.tsx` — layout global y fuentes de Google.

- `src/components/LoginForm.tsx` — alterna entre "Iniciar sesión" y "Crear cuenta" (autorregistro pide también nombre visible). No muestra ninguna pista de credenciales.

- `src/components/ChangePasswordPanel.tsx` — modal accesible para cualquier usuario autenticado (botón "Cambiar contraseña" junto a "Cerrar sesión" en `page.tsx`); pide contraseña actual + nueva + confirmación.

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
- `src/lib/auth.ts` — hook `useAuth` (login, register, logout; sesión en `localStorage` con `id`, `username`, `displayName`, `role`, `token`). `register` crea la cuenta y autentica en el mismo paso, igual que `login`.
- `src/lib/boards.ts` — cliente API de tableros (`listBoards`, `createBoard`, `getBoard`, `updateBoard`, `renameBoard`, `deleteBoard`).
- `src/lib/users.ts` — cliente API de usuarios (`listUsers`, `createUser`, `updateUserRole`, `deleteUser`, `changePassword`). `changePassword` la usa `ChangePasswordPanel`; el resto solo `UserManagementPanel`.

## Pruebas actuales

- `src/test/mockBoardApi.ts` — helper compartido que mockea `fetch` para `/api/boards*` y `/api/ai/chat` en los tests de Vitest.
- `src/components/KanbanBoard.test.tsx` y `KanbanBoard.integration.test.tsx` — renderizado de columnas, renombrado, alta/baja de tarjetas, respuestas del chat IA, visibilidad condicional de "Gestionar usuarios" según rol.
- `src/components/LoginForm.test.tsx` — no revela credenciales, envía login, alterna a registro y envía datos de alta.
- `src/components/ChangePasswordPanel.test.tsx` — rechaza confirmación que no coincide sin llamar a la API; envía el cambio y muestra éxito.
- `src/lib/kanban.test.ts` — lógica `moveCard`.
- `frontend/tests/*.spec.ts` (Playwright, contra el backend real en Docker en `localhost:8000`):
  - `auth.spec.ts` — login/logout, ausencia de la pista de credenciales, autorregistro desde el login.
  - `kanban.spec.ts` — carga de tablero, alta de tarjeta, mover tarjeta entre columnas.
  - `boards.spec.ts` — crear, cambiar y eliminar tableros.
  - `users.spec.ts` — un admin crea y elimina un usuario desde el panel de gestión.
  - `password.spec.ts` — un usuario recién registrado cambia su contraseña y vuelve a iniciar sesión con la nueva.
  - `ai-chat.spec.ts` — el chat aplica una actualización real de OpenRouter (puede fallar de forma intermitente por el modelo gratuito).
