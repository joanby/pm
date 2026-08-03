# Backend MVP (estado actual)

## Propósito

Este backend implementa la base de la API del proyecto con FastAPI y sirve el frontend Next.js compilado de forma estática en `/`.

## Estructura actual

- `app/main.py`
  - `GET /api/health`: endpoint de salud.
  - `GET /`: sirve `backend/static/frontend/index.html`.
  - `GET /{asset_path:path}`: sirve assets del frontend exportado (con fallback a `index.html`).
- `app/db/`
  - `schema.py`, `init_db.py`, `connection.py`
- `app/kanban/`
  - `models.py`, `repository.py`, `service.py`, `router.py`, `seed.py`
  - API Kanban en `/api/board` (Parte 6)
- `static/frontend/`
  - salida estática de `frontend` generada por `next build` con `output: "export"`.
- `requirements.txt`
  - dependencias mínimas del backend.

## Modelo de datos (Parte 5)

- Esquema: `docs/db-schema.json`
- Diseño: `docs/db-design.md`
- Tablas: `users`, `boards`, `columns`, `cards`, `chat_messages`
- SQLite local; evolución futura prevista a Supabase.

## Ejecución en contenedor (multi-stage)

- El `Dockerfile` compila primero el frontend en una etapa Node y copia `out/` al backend.
- La etapa final usa la imagen `ghcr.io/astral-sh/uv:python3.12-bookworm-slim` (sin `pip`) e instala dependencias con `uv pip install`.
- `docker-compose.yml` expone el backend en `http://localhost:8000`.

## Próximos pasos (según plan)

- Conectar frontend a la API Kanban (Parte 7).
- Partes 8-10: IA.

## Pruebas de integración estática (Parte 3)

- `tests/integration/test_home_page.py`: `/` sirve el HTML del Kanban.
- `tests/integration/test_static_assets.py`: assets `/_next/*`, favicon y fallback SPA.

## Pruebas de base de datos y API Kanban

- `tests/unit/test_db_schema.py`: validación de `docs/db-schema.json`.
- `tests/integration/test_db_init.py`: creación idempotente de SQLite.
- `tests/unit/test_kanban_models.py`: validación de payloads del tablero.
- `tests/unit/test_kanban_repository.py`: persistencia en repositorio.
- `tests/integration/test_kanban_api.py`: flujo API Kanban completo.
