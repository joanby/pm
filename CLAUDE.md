# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A project management MVP: a single-user Kanban board with an AI chat sidebar that can create/edit/move cards via structured output. NextJS frontend, FastAPI backend serving the exported static frontend, SQLite persistence, OpenRouter for AI. Designed to run as one Docker container locally. Full requirements and decisions are in `docs/PLAN.md` and the root `AGENTS.md` (in Spanish) — read those before making product/architecture decisions.

## Commands

### Frontend (`frontend/`)
```bash
npm install
npm run dev          # http://localhost:3000, dev only (use backend for /api/* in this mode they are not proxied)
npm run build        # next build -> static export in frontend/out (output: "export")
npm run lint
npm run test:unit              # vitest run
npm run test:unit:watch        # vitest watch mode
npm run test:e2e               # playwright; baseURL is http://localhost:8000 (the backend), not the vite dev server
npm run test:all               # unit then e2e
```
Run a single unit test: `npx vitest run src/lib/kanban.test.ts -t "test name"`
Run a single e2e test: `npx playwright test tests/kanban.spec.ts -g "test name"`

E2E tests hit `localhost:8000`, i.e. the FastAPI backend (directly, or via the Docker container), not `next dev`. Build and run the backend (or the Docker container) before running `test:e2e`.

### Backend (`backend/`)
Uses `uv` as the package manager (also used inside the Docker build).
```bash
uv pip install -e .
uv run pytest                              # run all backend tests (backend/tests/)
uv run pytest tests/test_board.py::test_name   # run a single test
uv run uvicorn backend.main:app --reload --port 8000   # run from repo root
```
Backend tests live in `backend/tests/` (one file per router domain: `test_health.py`, `test_auth.py`, `test_board.py`, `test_ai.py`), with shared fixtures in `backend/tests/conftest.py` (`client`, `auth_headers`) that isolate the DB per test by pointing `KANBAN_DB_PATH` at a throwaway `test-kanban.db` and deleting it before/after each test. `conftest.py` also reads `OPENROUTER_API_KEY` from the root `.env` if present — the AI chat/validate tests make real OpenRouter calls, so they need a working key to pass (and can fail intermittently — see Architecture notes below).

### Docker (full stack)
```bash
scripts/start.sh   # docker build, then run container "pm-mvp" on :8000 (uses root .env if present)
scripts/stop.sh     # stop and remove the container
```
Equivalent: `docker compose up --build` (maps host `:80` -> container `:8000`, persists SQLite to a named volume, reads `.env`). Rebuild after any backend/frontend change — there is no hot reload in the container.

## Architecture

**Build/serve model**: Docker multi-stage build (`Dockerfile`) compiles the NextJS app to a static export (`output: "export"` in `next.config.ts`) and copies it into `backend/static/frontend`. FastAPI mounts that directory at `/` via `StaticFiles(html=True)` and exposes JSON APIs under `/api/*`. There is no API proxy in production — the same FastAPI process serves both. In local frontend dev (`npm run dev`), `/api/*` calls go nowhere unless the backend is also running and reachable; e2e tests therefore target the backend port directly.

**Backend package layout**: `backend/main.py` only assembles the app (lifespan calling `init_db`, `app.include_router(...)` for each router, static mount) — it has no route handlers or business logic of its own. Routes live in `backend/routers/` as one `APIRouter` per domain (`health.py`, `auth.py`, `board.py`, `ai.py`); persistence lives in `backend/db/` as one module per concern (`connection.py`, `seed.py`, `boards.py`, `users.py`), re-exported through `backend/db/__init__.py` so callers can keep doing `from backend.db import load_board, save_board, find_user, init_db, get_db_path`. AI chat orchestration (schema, prompt building, retry) stays in the top-level `backend/ai.py`, separate from the HTTP layer in `backend/routers/ai.py`. Tests mirror this in `backend/tests/` (one file per router domain, shared fixtures in `conftest.py`).

**Request flow for AI chat** (`POST /api/ai/chat`, handled in `backend/routers/ai.py` -> `backend/ai.py`):
1. Frontend sends `{ message, board, history }` (current full board state + user prompt + chat history) — see `AiChatRequest` in `backend/ai.py`.
2. `build_ai_messages` wraps this into an OpenRouter chat payload with a system prompt instructing the model to return only JSON matching a strict schema (`AI_RESPONSE_SCHEMA`).
3. `openrouter.py` posts to OpenRouter using `OPENROUTER_API_KEY` (model: `openai/gpt-oss-120b:free`, hardcoded).
4. The raw JSON content is parsed and validated into `AiChatResponse { message, boardUpdate: BoardData | null }`. `BoardData` validation (`main_models.py`) enforces that every `cardIds` entry refers to an existing card and no card is referenced twice. `request_structured_ai_response` retries up to 3 times (`MAX_AI_ATTEMPTS` in `backend/ai.py`) if a response isn't valid JSON/schema before raising — the free OpenRouter model occasionally returns non-JSON content, and even with retries a single chat call can occasionally take well over a minute end-to-end (each attempt has its own 45s httpx timeout), so don't assume `/api/ai/chat` is fast.
5. If `boardUpdate` is non-null, the router persists it via `save_board` immediately — the AI response *is* the new source of truth for the board, there's no separate confirmation step.

**Persistence** (`backend/db/`): single SQLite file (default `backend/kanban.db`, override via `KANBAN_DB_PATH` env var — used by Docker to point at a mounted volume and by tests to point at a throwaway file). Schema has `boards`, `users`, `conversations` tables, but the MVP only ever reads/writes a single hardcoded row (`board-1`) — multi-user/multi-board support is schema-ready but not implemented. `init_db` (in `db/seed.py`) seeds a default board and the one hardcoded user (`usuario`/`contraseña`) on first run. `backend/kanban.db` is gitignored (not committed) — it's local dev/runtime state, regenerated automatically.

**Auth**: simulated but enforced. `backend/routers/auth.py` defines `sessions` (in-memory dict token→username) and the `require_auth` FastAPI dependency, applied via `Depends(require_auth)` to `GET/POST /api/board` and both `/api/ai/*` routes — they return 401 without a valid `Authorization: Bearer <token>` header. `login()` checks credentials against the real `users` table (via `db.find_user`, not a hardcoded dict) and `logout()` actually removes the token from `sessions`. The frontend propagates the token from `useAuth` (`frontend/src/lib/auth.ts`, persisted to `localStorage`) down through `page.tsx` → `KanbanBoard` → `AiChatPanel` as a required `token` prop, included as a Bearer header on every API call. There's still no password hashing and sessions never expire — acceptable for a local-only MVP, not for any real deployment.

**Frontend structure** (`frontend/src/`):
- `lib/kanban.ts` — `BoardData`/`Column`/`Card` types and pure board logic (`moveCard` for drag reordering, id generation). The backend `BoardData` model in `main_models.py` mirrors this shape; keep them in sync when changing the board schema.
- `lib/auth.ts` — `useAuth` hook, calls `/api/auth/login|logout`, persists session client-side only.
- `components/KanbanBoard.tsx` — top-level stateful component; owns `BoardData` state, loads/saves it via `/api/board`, wires up `DndContext` for drag-and-drop, and hosts `AiChatPanel`.
- `components/KanbanColumn.tsx`, `KanbanCard.tsx`, `KanbanCardPreview.tsx`, `NewCardForm.tsx` — board presentation pieces (`@dnd-kit/sortable` for drag).
- `components/AiChatPanel.tsx` — sidebar chat UI; posts to `/api/ai/chat` and applies the returned `boardUpdate` to board state when present.
- `components/LoginForm.tsx` — gates the board behind the simulated login.

**Schema reference**: `docs/db-schema.json` / `docs/db-schema-example.md` document the full intended DB schema (including the not-yet-wired multi-user/conversation persistence).

## Conventions (from `AGENTS.md`)

- Keep it simple — no over-engineering, no defensive programming for cases that can't happen.
- No emojis anywhere (docs or code).
- When debugging, find the root cause before changing code — don't guess-and-check.
- Project documentation lives in `docs/`; check `docs/PLAN.md` for current scope/status before starting new work.
- Color tokens are defined in `docs/PLAN.md` (`AGENTS.md`) if you touch styling: accent yellow `#ecad0a`, primary blue `#209dd7`, secondary purple `#753991`, dark navy `#032147`, gray text `#888888`.
