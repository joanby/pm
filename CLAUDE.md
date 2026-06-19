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
uv run pytest                          # run all backend tests (test_main.py)
uv run pytest test_main.py::test_name  # run a single test
uv run uvicorn backend.main:app --reload --port 8000   # run from repo root
```
Backend tests redirect `KANBAN_DB_PATH` to a throwaway `test-kanban.db` and read `OPENROUTER_API_KEY` from the root `.env` if present — the AI chat/validate tests make real OpenRouter calls, so they need a working key to pass.

### Docker (full stack)
```bash
scripts/start.sh   # docker build, then run container "pm-mvp" on :8000 (uses root .env if present)
scripts/stop.sh     # stop and remove the container
```
Equivalent: `docker compose up --build` (maps host `:80` -> container `:8000`, persists SQLite to a named volume, reads `.env`). Rebuild after any backend/frontend change — there is no hot reload in the container.

## Architecture

**Build/serve model**: Docker multi-stage build (`Dockerfile`) compiles the NextJS app to a static export (`output: "export"` in `next.config.ts`) and copies it into `backend/static/frontend`. FastAPI mounts that directory at `/` via `StaticFiles(html=True)` and exposes JSON APIs under `/api/*`. There is no API proxy in production — the same FastAPI process serves both. In local frontend dev (`npm run dev`), `/api/*` calls go nowhere unless the backend is also running and reachable; e2e tests therefore target the backend port directly.

**Request flow for AI chat** (`POST /api/ai/chat`, handled in `backend/main.py` -> `backend/ai.py`):
1. Frontend sends `{ message, board, history }` (current full board state + user prompt + chat history) — see `AiChatRequest` in `ai.py`.
2. `build_ai_messages` wraps this into an OpenRouter chat payload with a system prompt instructing the model to return only JSON matching a strict schema (`AI_RESPONSE_SCHEMA`).
3. `openrouter.py` posts to OpenRouter using `OPENROUTER_API_KEY` (model: `openai/gpt-oss-120b:free`, hardcoded).
4. The raw JSON content is parsed and validated into `AiChatResponse { message, boardUpdate: BoardData | null }`. `BoardData` validation (`main_models.py`) enforces that every `cardIds` entry refers to an existing card and no card is referenced twice.
5. If `boardUpdate` is non-null, `main.py` persists it via `db.save_board` immediately — the AI response *is* the new source of truth for the board, there's no separate confirmation step.

**Persistence** (`backend/db.py`): single SQLite file (default `backend/kanban.db`, override via `KANBAN_DB_PATH` env var — used by Docker to point at a mounted volume and by tests to point at a throwaway file). Schema has `boards`, `users`, `conversations` tables, but the MVP only ever reads/writes a single hardcoded row (`board-1`) — multi-user/multi-board support is schema-ready but not implemented. `init_db` seeds a default board and the one hardcoded user (`usuario`/`contraseña`) on first run.

**Auth**: fully simulated. One hardcoded credential pair in `main.py` (`VALID_CREDENTIALS`), tokens are random and stored in an in-memory `sessions` dict that nothing ever checks (no endpoint currently enforces the token) — login is for the frontend UX gate (`frontend/src/lib/auth.ts` persists the session to `localStorage` and `useAuth` exposes `login`/`logout`), not real authorization.

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
