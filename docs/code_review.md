# Code Review — `cursor/part2-docker-fastapi-scripts` (Parte 4: persistencia + chat IA)

Scope: `git diff origin/default...HEAD` (Kanban persistence + AI chat feature branch) plus the small uncommitted change to `frontend/tests/kanban.spec.ts`. Generated build artifacts (`backend/static/frontend/**`) and lockfiles were excluded from review.

Method: 8 finder passes (line-by-line diff scan, removed-behavior audit, cross-file trace, reuse, simplification, efficiency, altitude, CLAUDE.md conventions) run independently, deduplicated, then verified by re-reading the actual source and, for the two most severe items, empirically reproducing the bug against SQLite in isolation.

> ⚠️ **Alcance real vs. lo solicitado:** esta pasada cubre el *diff* de esta rama (persistencia Kanban + chat IA), no la totalidad del código base preexistente (login simulado, esquema BD, servido estático, etc. de Partes 2-7). Si quieres cobertura de "todo el código del repositorio" en sentido literal, hace falta una pasada adicional sobre el baseline — ver nota al final.

---

## Resumen ejecutivo y plan de acción

| # | Hallazgo | Severidad | Acción recomendada | Estado |
|---|----------|-----------|---------------------|--------|
| 1 | `move_card` viola su propio índice `UNIQUE(column_id, position)` en casi cualquier reordenación real | 🔴 Crítica — 500 en producción | Corregir ya: aparcar posiciones (offset negativo) antes de escribir, igual que ya se hace para la columna origen | ✅ Corregido (`repository.py`, `_shift_positions`) + tests de regresión + verificado en Docker real |
| 5 | Tarjeta duplicada en dos columnas (update IA) provoca `IntegrityError` sin manejar | 🔴 Crítica — 500 en producción | Corregir ya: `validate_card_references` debe rechazar un id en más de una columna | ✅ Corregido (`models.py`) + test de regresión |
| 3 | El backend entero falla al importar si falta `OPENROUTER_API_KEY` | 🔴 Crítica — bloquea CI/tests/arranque | Corregir ya: construir `AiService`/`ChatService` de forma perezosa (por request o `Depends`) | ✅ Corregido (`router.py`) + test de regresión |
| 2 | Historial de chat se desordena en intercambios del mismo segundo | 🟠 Alta — corrompe UI e historial enviado al modelo | Corregir pronto: añadir desempate monótono (rowid) al `ORDER BY` |
| 6 | Un cambio de tablero rechazado por la IA se descarta en silencio | 🟠 Alta — respuesta engañosa al usuario | Corregir pronto: propagar el rechazo al mensaje/flag de respuesta y loguearlo |
| 4 | Reintentar un mensaje fallido duplica la burbuja del usuario | 🟡 Media — UX incorrecta, no pérdida de datos | Corregir: no reañadir burbuja en `handleRetry`, reusar el estado pendiente |
| 10 | Errores de chat siempre muestran el mismo mensaje "reintentable", aunque sea un 503 permanente | 🟡 Media — UX confusa | Corregir: distinguir por `error.status`, ocultar Retry en errores no transitorios |
| 7 | El test E2E enmascara el 502 real de OpenRouter con un reintento, en vez de arreglarlo en el cliente | 🟡 Media — debilita la señal de regresión real | Corregir: añadir retry/backoff en `OpenRouterClient`, simplificar el test después |
| 8 | `get_board` hace N+1 queries y se relanza tras cada mutación | 🟢 Baja — rendimiento, no correctitud | Mejora oportunista: un único `JOIN`, evitar releer lo que ya se tiene |
| 9 | `ai-api.ts` duplica el wrapper `fetch` de `kanban-api.ts` | 🟢 Baja — mantenibilidad | Mejora oportunista: extraer un `request<T>` compartido |

**Prioridad inmediata (✅ ya resuelta):** #1, #5 y #3 eran bugs de producción con reproducción confirmada (dos de ellos contra SQLite real) — cualquiera de los tres podía tumbar una petición real. Los tres están corregidos, con tests de regresión que fallan contra el código anterior y pasan con el fix, y re-verificados contra un contenedor Docker real (`docker compose up --build`) más la suite E2E completa (9/9). Detalle en cada sección numerada más abajo.

**Pendiente:** #2, #4, #6, #7, #8, #9, #10 siguen sin tocar, tal como se decidió al alcance de esta ronda de arreglos.

---

## 1. `move_card` violates its own UNIQUE(column_id, position) index on almost any real reorder

> ✅ **Fixed.** Moving card parked to `-1` before any sibling shift; sibling shifts staged through a disjoint negative range (`_shift_positions`) so a multi-row `UPDATE` can never collide regardless of SQLite's row-processing order. Repro'd against real SQLite before and after (all three cases now produce the correct final order); regression tests added in `test_kanban_repository.py`; also re-verified against a live Docker container (`PUT /api/cards/{id}/move`, 200 OK) and the full 9-test Playwright E2E suite (drag-and-drop tests).

**File:** `backend/app/kanban/repository.py:289-339`

`move_card` shifts sibling rows' `position` with sequential `UPDATE` statements before writing the moved card's final position. SQLite checks the `UNIQUE(column_id, position)` index (`idx_cards_column_position`, see `docs/db-schema.json`) immediately per row, not deferred, so any shift that makes two rows momentarily collide raises `sqlite3.IntegrityError`, which is unhandled and surfaces as a 500.

Reproduced directly against a fresh in-memory SQLite table with the same schema and the same statements this method issues:
- Same-column reorder, moving position 0 → 1 in a 3-card column: **fails**.
- Same-column reorder, moving position 2 → 0 in a 3-card column: **fails**.
- Cross-column move into position 0 of a column that already has 2 cards: **fails**.

Only the trivial cases (moving into a column with 0-1 existing cards, or to the exact same position) succeed — which is exactly what the one existing integration test (`test_move_card_updates_board`, moving `card-1` into `col-review`, which starts with a single card) exercises, so the bug ships undetected. Any real drag-and-drop reorder within a column, or into a column with 2+ cards, will 500 in production.

**Fix direction:** park all affected rows at negative/offset positions first (or do the shift in a single `CASE`-based UPDATE), matching the two-phase approach already used for the *cross-column* source-column shift (line 315), but apply the same parking trick to the target-column shift and to the same-column reorder branch.

---

## 2. Chat history ordering breaks for same-second exchanges

**File:** `backend/app/ai/chat_repository.py:21-41`

`list_messages` orders by `created_at DESC` (second-resolution ISO timestamp, `_now_iso()` strips microseconds) with no tiebreaker, then reverses in Python. `_persist_exchange` in `chat_service.py` writes the user message and the assistant message back-to-back, which routinely lands in the same second.

Reproduced empirically: inserting `user@10:00:00`, `assistant@10:00:00`, `user@10:00:01`, `assistant@10:00:01` and running the exact query/`reversed()` pipeline yields final order `assistant(10:00:00), user(10:00:00), assistant(10:00:01), user(10:00:01)` — the assistant reply is shown *before* the user turn that produced it. This corrupts both `GET /api/ai/history` (visible to the user) and `build_chat_messages`, which feeds this same history back to the model as conversation context.

**Fix direction:** add a monotonic tiebreaker (autoincrement rowid, or a sequence column) to `ORDER BY`, or store sub-second timestamps.

---

## 3. AI router crashes the whole backend at import time when `OPENROUTER_API_KEY` is unset

> ✅ **Fixed.** `AiService()`/`ChatService()` are now constructed inside each endpoint function (already inside the existing `try/except` that maps `OpenRouterConfigError` → 503), not at module scope. Verified `backend.app.main` imports cleanly with the key unset; regression test added in `test_ai_router.py` (reloads `router` with `OpenRouterClient.__init__` patched to raise — fails on the pre-fix code, passes now).

**File:** `backend/app/ai/router.py:12-14`, `backend/app/ai/client.py:73`

```python
router = APIRouter(prefix="/api/ai", tags=["ai"])
ping_service = AiService()
chat_service = ChatService()
```

`AiService()`/`ChatService()` default-construct `OpenRouterClient()`, whose `__init__` calls `get_openrouter_api_key()` eagerly, raising `OpenRouterConfigError` if no key is configured (env var or root `.env`). Because `backend/app/main.py` does `from backend.app.ai.router import router as ai_router` unconditionally, **importing `backend.app.main` itself fails** without a configured key — not just AI requests. Every test that uses the `client`/`seeded_db` fixtures (including pure Kanban CRUD tests in `test_kanban_api.py`, `test_home_page.py`, `test_static_assets.py`) fails to even start on a machine/CI without `OPENROUTER_API_KEY`, contradicting `backend/AGENTS.md`'s framing that only `test_ai_openrouter.py`/`test_ai_chat.py` need the key.

**Fix direction:** construct `AiService`/`ChatService` lazily per-request (or via FastAPI `Depends`), so config errors surface only when an AI endpoint is actually hit — which is exactly what `_handle_openrouter_error` already exists to do.

---

## 4. Retrying a failed chat message duplicates the user's bubble

**File:** `frontend/src/components/AiChatSidebar.tsx:70-108`

`submitMessage` unconditionally appends a new user-role bubble (line 71) every time it runs, and `handleRetry` (line 103-108) calls `submitMessage(lastFailedMessage)` again after a failure — but the bubble from the original failed attempt was never removed. Sequence: user sends "Hello" → request fails → error banner + Retry shown, "Hello" bubble still present → user clicks Retry → a second identical "Hello" bubble is appended before the (now successful) response arrives. The transcript permanently shows the message twice for one logical send. `AiChatSidebar.test.tsx`'s retry test only asserts the reply text appears, not bubble count, so this ships unnoticed.

**Fix direction:** either don't add a new bubble on retry (reuse the existing one, e.g. by tracking pending message state instead of eagerly appending), or remove/mark the failed bubble before retrying.

---

## 5. A duplicated card reference in an AI-provided board update crashes with an unhandled `IntegrityError`

> ✅ **Fixed.** `validate_card_references` now rejects any card id referenced by more than one column, so `BoardData.model_validate` raises a normal `ValidationError` — caught at `structured.py:54`/`chat_service.py`'s existing `except OpenRouterResponseError` path — instead of reaching `replace_board` and hitting `IntegrityError`. Regression test added in `test_kanban_models.py`. Note: this still lands in the silent-swallow path described in finding #6 below, which is intentionally left as-is (not one of the three criticals).

**File:** `backend/app/kanban/models.py:43-61` (validation gap), `backend/app/kanban/repository.py:94-118` (where it explodes)

`BoardData.validate_card_references` checks for cards referenced-but-undefined ("missing") and defined-but-unreferenced ("unused"), but never checks that a card id appears in **at most one** column's `cardIds`. If the model's structured board update lists the same card id under two columns (a very plausible LLM slip when "moving" a card), `BoardData.model_validate` in `structured.py:54` accepts it, `validate_board_column_ids` in `chat_service.py` doesn't catch it either (it only checks column ID order), and `KanbanRepository.replace_board` issues two `INSERT INTO cards` with the same primary key — raising `sqlite3.IntegrityError`. `chat_service.chat()`'s `except OpenRouterResponseError: pass` (line 47) doesn't match this exception type, so it propagates through `ai/router.py`'s catch-all (`_handle_openrouter_error` re-raises anything it doesn't recognize), producing an unhandled 500 instead of the graceful "board update rejected" path the code clearly intends for malformed AI output.

**Fix direction:** extend `validate_card_references` to reject a card id appearing under more than one column, so this is caught as a normal validation error like the others.

---

## 6. A rejected AI board update is silently discarded, leaving the reply text and the actual result inconsistent

**File:** `backend/app/ai/chat_service.py:42-48`

```python
if structured.board is not None:
    try:
        validate_board_column_ids(current_board, structured.board)
        board = self.kanban_service.replace_board(username, structured.board)
        board_updated = True
    except OpenRouterResponseError:
        pass
```

When the model's structured board fails validation (e.g. it renamed/reordered a fixed column id), the exception is swallowed and the response still returns the model's original natural-language message (e.g. "I moved the card to Done") together with `board_updated: false` and the unchanged board. The user sees a message describing a change that silently never happened, with no error indicator anywhere in the API response or UI, and no log line recording that the model violated its contract.

**Fix direction:** surface the rejection — append a caveat to `message`, or return an explicit error/flag the frontend can render — and log the raw rejected board for observability.

---

## 7. AI-chat flakiness is patched over in the E2E test instead of in the backend/client

**Files:** `frontend/tests/kanban.spec.ts:139-162` (uncommitted change), `backend/app/ai/client.py:80-104`

The E2E helper now catches a failed chat send, checks for a visible error banner, and clicks the sidebar's own Retry button once, justified by a comment that OpenRouter's free-tier model "occasionally 502s on a cold call." `OpenRouterClient.complete_messages` makes exactly one HTTP attempt and turns any `HTTPStatusError`/`TimeoutException`/`HTTPError` straight into a raised error with no retry/backoff. The fix lives in the test layer, not the thing it's testing: real users hit the same acknowledged flakiness with no recovery path, and the test itself is now weaker — if `/api/ai/chat` starts reliably failing (a real regression), the test masks it as "expected 502 flakiness" and only fails if the retry also fails.

**Fix direction:** add retry-with-backoff for transient upstream statuses (502/503/timeout) inside `OpenRouterClient`/`ChatService`, which benefits real users and lets the E2E test go back to a single wait with no special-casing.

---

## 8. `KanbanRepository.get_board` is N+1 and gets re-run twice per mutation

**File:** `backend/app/kanban/repository.py:38-76`, and its call sites at `125`, `148`, `344`

`get_board` issues one query for columns plus one additional query per column for its cards (5 columns → 6 round trips for the seeded board). `replace_board`, `update_column_title`, and `move_card` each perform their write and then call `get_board` again just to return the result, discarding data they already had (in `replace_board`'s case, literally re-reading the board it just wrote from the payload it was given).

**Fix direction:** a single `cards JOIN columns WHERE board_id = ? ORDER BY columns.position, cards.position` fetches the whole board in one round trip; mutating methods can construct the return value from already-known state instead of re-querying.

---

## 9. `ai-api.ts` duplicates `kanban-api.ts`'s fetch wrapper

**File:** `frontend/src/lib/ai-api.ts:28-48` vs `frontend/src/lib/kanban-api.ts:19-43`

Both files define a near-identical `request<T>(username, path, init)` that injects `Content-Type`/`X-MVP-Username` headers and throws a typed error (`AiApiError` / `KanbanApiError`) on a non-OK response. Any future change to auth-header construction or error handling (e.g. adding a retry, changing the header name) has to be made in both places.

**Fix direction:** extract a shared `request<T>(username, path, ErrorClass, init)` helper (or a small fetch-client factory) used by both `ai-api.ts` and `kanban-api.ts`.

---

## 10. Chat send failures always show a generic, always-retryable message regardless of the actual error

**File:** `frontend/src/components/AiChatSidebar.tsx:76-91`

`sendChatMessage` throws `AiApiError` with a real HTTP `status` (`ai-api.ts:3-11`), but `submitMessage`'s `catch` discards the error entirely (`catch {`) and always sets the same "Unable to reach the AI assistant. Please try again." message with a Retry button. A permanent failure (e.g. 503 because `OPENROUTER_API_KEY` isn't configured server-side, per finding #3) gets the exact same "click Retry" UX as a transient 502/504, inviting the user to retry something that cannot succeed until an admin fixes the server configuration.

**Fix direction:** branch on `error instanceof AiApiError && error.status` and only offer Retry for genuinely transient statuses (502/504/network), showing a distinct non-retryable message for 4xx/503-config errors.

---

### Notes on angles that did not surface findings

- **Conventions (CLAUDE.md/AGENTS.md):** no clear, quotable rule violations found in the diff.

---

## Nota sobre alcance

Esta revisión se dirigió al *diff* de la rama actual (`git diff origin/default...HEAD`), que es el modo estándar de la herramienta de revisión: cubre la persistencia Kanban y el chat IA (el trabajo activo de esta sesión), pero **no** re-audita el código base que ya existía antes de este diff (login simulado, capa de BD/esquema, servido estático del frontend, scripts de arranque de Partes 2-7). Si el objetivo es una auditoría literal de "todo el código del repositorio", hace falta una pasada adicional apuntando explícitamente a esos directorios/commits base.
