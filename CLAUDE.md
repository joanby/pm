# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Local MVP project-management app: a Kanban board with an AI sidebar chat, built in phases (see `docs/PLAN.md`), running via Docker. Simulated single-user login (`user` / `password`), but the data model is prepared for multiple users. Documentation and commit messages in this repo are in Spanish.

- Frontend: Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS 4, `@dnd-kit` for drag-and-drop.
- Backend: FastAPI (Python 3.12), served from `backend/app`, also serves the static-exported frontend at `/`.
- Persistence: SQLite (local file under `backend/data/`), auto-created on startup. Planned future migration to Supabase (see `.env.example`).
- AI: OpenRouter API (`OPENROUTER_API_KEY` in root `.env`), default model `openai/gpt-oss-120b:free`.
- Containerization: single multi-stage `Dockerfile` (Node stage builds the frontend export, copied into the FastAPI image) + `docker-compose.yml`, exposing everything on `http://localhost:8000`.

## Commands

### Run the full stack (Docker)

From repo root:
```bash
scripts\start.bat        # Windows CMD (recommended)
.\scripts\start.ps1       # Windows PowerShell (requires ExecutionPolicy RemoteSigned)
./scripts/start.sh        # Linux/macOS
```
Stop with the matching `stop.*` script. App is at http://localhost:8000.

### Backend (pytest)

From repo root (imports are rooted at repo root, e.g. `backend.app.main`):
```bash
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m pytest backend/tests -v
python -m pytest backend/tests/unit/test_kanban_repository.py -v   # single file
python -m pytest backend/tests/unit/test_kanban_repository.py::test_name -v  # single test
```
Static-asset integration tests require a built frontend at `backend/static/frontend/` (Docker builds this automatically; locally run `cd frontend && npm run build` and copy `out/` there).

### Frontend

From `frontend/`:
```bash
npm run dev              # local dev server (:3000)
npm run build             # production/static export build
npm run test:unit         # Vitest unit/component tests
npm run test:e2e          # Playwright E2E against dev server (:3000)
npm run test:e2e:docker   # Playwright E2E against Docker backend (:8000)
npm run test:all          # unit + e2e
npm run lint
```
Run a single Vitest file: `npx vitest run src/lib/kanban.test.ts`. Run a single Playwright spec: `npx playwright test tests/kanban.spec.ts`.

### Manual API checks (container running)

```bash
curl -H "X-MVP-Username: user" http://localhost:8000/api/board
curl -H "X-MVP-Username: user" http://localhost:8000/api/ai/ping
curl -X POST http://localhost:8000/api/ai/chat -H "Content-Type: application/json" -H "X-MVP-Username: user" -d '{"message":"..."}'
```
Contracts: `docs/api-kanban.md`, `docs/api-ai.md`.

## Architecture

### Request flow

The FastAPI app (`backend/app/main.py`) mounts `kanban_router` and `ai_router`, then falls back to serving the static Next.js export (`backend/static/frontend/`) for `/` and any non-`api/` path (SPA-style fallback to `index.html`). There is no separate frontend dev server in production — the frontend is exported (`output: "export"`) and baked into the backend image at build time.

### Backend modules (`backend/app/`)

- `db/`: `schema.py` (schema definition), `init_db.py` (idempotent SQLite creation, called from `main.py` lifespan), `connection.py`. Schema tables: `users`, `boards`, `columns`, `cards`, `chat_messages` — documented in `docs/db-design.md` / `docs/db-schema.json`.
- `kanban/`: `models.py`, `repository.py` (SQLite persistence), `service.py`, `router.py` (`/api/board`), `seed.py` (demo data seeded on startup). All board endpoints identify the user via the `X-MVP-Username` header (no real auth yet).
- `ai/`: `config.py`, `client.py` (OpenRouter HTTP client), `service.py`, `chat_service.py` (applies structured Kanban changes returned by the model), `chat_repository.py` (chat history persistence), `prompts.py`, `structured.py` (parses/validates structured AI output), `router.py` (`GET /api/ai/ping`, `POST /api/ai/chat`, `GET /api/ai/history`).
- The AI chat flow: backend sends board state + prompt + history to the model; the model returns text plus optional structured Kanban changes; `chat_service`/`structured` validate and apply those changes, which are persisted and then reflected in the frontend.

### Frontend modules (`frontend/src/`)

- `app/page.tsx` renders `KanbanBoard` at `/`; `app/layout.tsx` is the global layout.
- `components/KanbanBoard.tsx` owns board state and drag-and-drop orchestration (`KanbanColumn.tsx`, `KanbanCard.tsx`, `KanbanCardPreview.tsx` for the `DragOverlay`, `NewCardForm.tsx`); `components/AiChatSidebar.tsx` is the AI chat panel.
- `lib/auth.ts`: simulated credential check + `localStorage` session (access guard + logout live in the board page).
- `lib/kanban-api.ts` / `lib/ai-api.ts`: fetch clients for `/api/board` and `/api/ai/*`, sending `X-MVP-Username`.
- `lib/kanban.ts`: core types (`Card`, `Column`, `BoardData`), `initialData`, and pure logic (`moveCard`, `createId`).

### Testing conventions

Every new feature is expected to ship with both a unit/component test and an integration/E2E test (see `backend/AGENTS.md` and `frontend/AGENTS.md`). Backend unit tests avoid the network/DB where possible; integration tests exercise real endpoints (`test_ai_openrouter.py` and `test_ai_chat.py` make real OpenRouter calls and need `OPENROUTER_API_KEY`).

## Conventions

- Follow `docs/PLAN.md` phase ordering — don't add functionality outside the scope of the current phase.
- Keep the demo credentials `user` / `password` consistent across code and docs.
- Prefer small, verifiable changes with root-cause diagnosis over quick patches.
- UI color scheme: accent yellow `#ecad0a`, primary blue `#209dd7`, secondary purple `#753991`, dark navy `#032147`, auxiliary text gray `#888888`.
- Area-specific guidance lives in `AGENTS.md`, `backend/AGENTS.md`, `frontend/AGENTS.md`, `scripts/AGENTS.md` — check the relevant one before making changes in that area.
