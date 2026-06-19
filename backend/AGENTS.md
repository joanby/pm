# Backend FastAPI

Backend Python FastAPI para el MVP de gestión de proyectos, organizado como paquete con sub-paquetes por responsabilidad (no como módulos sueltos monolíticos).

- `main.py` solo ensambla la app: lifespan (`init_db`), registra los routers de `routers/` y monta el frontend estático. No contiene lógica de negocio ni endpoints directamente.
- `routers/` — un router FastAPI por dominio, cada uno con sus propios modelos Pydantic si los necesita:
  - `health.py` — `/api/health`, `/api/ping`.
  - `auth.py` — `/api/auth/login`, `/api/auth/logout`; define `sessions` (dict token→username) y la dependencia `require_auth` que usan `board.py` y `ai.py` vía `Depends`.
  - `board.py` — `GET`/`POST /api/board`.
  - `ai.py` — `/api/ai/validate`, `/api/ai/chat` (rutas HTTP; la lógica de negoción con OpenRouter vive en el `ai.py` de nivel superior, ver abajo).
- `db/` — paquete de persistencia SQLite, dividido por responsabilidad:
  - `connection.py` — `get_db_path()` (lee `KANBAN_DB_PATH`), apertura de conexión SQLite.
  - `seed.py` — datos por defecto (`DEFAULT_BOARD`, `DEFAULT_USER`) y `init_db()` (crea tablas `boards`/`users`/`conversations` y siembra datos).
  - `boards.py` — `load_board`/`save_board`.
  - `users.py` — `find_user` (consulta la tabla `users`; usada por el login).
  - `db/__init__.py` re-exporta la API pública (`init_db`, `load_board`, `save_board`, `find_user`, `get_db_path`, `DB_PATH_ENV`) para que el resto del código siga haciendo `from backend.db import ...`.
- `main_models.py` define los modelos Pydantic compartidos del tablero (`BoardData`, `ColumnData`, `CardData`).
- `openrouter.py` contiene el cliente HTTP directo de OpenRouter (sin lógica de dominio).
- `ai.py` (nivel superior, junto a `main.py`) construye los mensajes para OpenRouter, define el esquema estructurado, valida `message`/`boardUpdate` y reintenta hasta 3 veces si la respuesta no es JSON válido (`request_structured_ai_response`).
- `OPENROUTER_API_KEY` se lee desde el entorno. En Docker, `scripts/start.sh` pasa `.env` si existe.
- Las pruebas viven en `tests/` (paquete, no un único fichero): `conftest.py` define los fixtures `client` y `auth_headers` y aísla la base de datos de test por cada test; `test_health.py`, `test_auth.py`, `test_board.py`, `test_ai.py` agrupan los tests por el mismo dominio que los routers. Los tests de IA contra endpoints reales llaman a OpenRouter de verdad (pueden fallar de forma intermitente por el modelo gratuito); los de reintento (`test_request_structured_ai_response_*`) usan `monkeypatch` y no tocan la red.
