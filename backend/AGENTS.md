# Backend FastAPI

Backend Python FastAPI para la app de gestión de proyectos, organizado como paquete con sub-paquetes por responsabilidad (no como módulos sueltos monolíticos).

- `main.py` solo ensambla la app: lifespan (`init_db`), registra los routers de `routers/` y monta el frontend estático. No contiene lógica de negocio ni endpoints directamente.
- `routers/` — un router FastAPI por dominio, cada uno con sus propios modelos Pydantic si los necesita:
  - `health.py` — `/api/health`, `/api/ping`.
  - `auth.py` — `/api/auth/login`, `/api/auth/register` (alta pública, rol `member`, inicia sesión automáticamente), `/api/auth/logout`; define `sessions` (dict token→user_id), y las dependencias `require_auth` (devuelve el usuario completo) y `require_admin` (exige rol `admin`) que usan el resto de routers vía `Depends`.
  - `users.py` — `/api/users` (gestión de usuarios, solo admin), `/api/users/me` (perfil propio: solo `display_name`), `/api/users/me/password` (cambio de contraseña propio, exige `current_password` correcto). Un admin no puede eliminarse a sí mismo ni degradar al último admin a `member`.
  - `boards.py` — `/api/boards` (listar/crear) y `/api/boards/{id}` (leer/actualizar/renombrar/eliminar). Cada usuario solo ve y modifica sus propios tableros (filtrado por `user_id` en cada consulta).
  - `ai.py` — `/api/ai/validate`, `/api/ai/chat` (rutas HTTP; la lógica de negocio con OpenRouter vive en el `ai.py` de nivel superior, ver abajo). El chat recibe `board_id` y verifica que el tablero pertenezca al usuario antes de guardar cambios.
- `db/` — paquete de persistencia SQLite, dividido por responsabilidad:
  - `connection.py` — `get_db_path()` (lee `KANBAN_DB_PATH`), apertura de conexión SQLite.
  - `seed.py` — datos por defecto (`DEFAULT_BOARD_DATA`, `DEFAULT_USER`) e `init_db()` (crea tablas `boards`/`users`/`conversations`, aplica migraciones de esquema con `ALTER TABLE` cuando faltan columnas, y siembra datos). Incluye una migración única que rehashea contraseñas antiguas en texto plano.
  - `boards.py` — CRUD multi-tablero: `list_boards_for_user`, `get_board`, `create_board`, `update_board_data`, `rename_board`, `delete_board`. Todas las consultas exigen `user_id` para aislar tableros entre usuarios.
  - `users.py` — `hash_password`/`verify_password` (bcrypt), `find_user`, `find_user_by_id`, `list_users`, `create_user`, `update_user`, `delete_user`, `count_admins`.
  - `db/__init__.py` re-exporta la API pública para que el resto del código siga haciendo `from backend.db import ...`.
- `main_models.py` define los modelos Pydantic compartidos: tablero (`BoardData`, `ColumnData`, `CardData`, `BoardSummary`, `BoardDetail`, `BoardCreateRequest`, `BoardRenameRequest`) y usuarios (`UserPublic`, `UserCreateRequest`, `UserUpdateRequest`, `RegisterRequest`, `ChangePasswordRequest`).
- `openrouter.py` contiene el cliente HTTP directo de OpenRouter (sin lógica de dominio).
- `ai.py` (nivel superior, junto a `main.py`) construye los mensajes para OpenRouter, define el esquema estructurado, valida `message`/`boardUpdate` y reintenta hasta 3 veces si la respuesta no es JSON válido (`request_structured_ai_response`). `AiChatRequest` incluye `board_id` para saber sobre qué tablero aplicar la actualización.
- `OPENROUTER_API_KEY` se lee desde el entorno. En Docker, `scripts/start.sh` pasa `.env` si existe.
- Dependencias de test (`pytest`, `pytest-cov`) están en `[dependency-groups].dev` de `pyproject.toml`; se ejecutan con `uv run pytest tests --cov=backend`.
- Las pruebas viven en `tests/` (paquete, no un único fichero): `conftest.py` define los fixtures `client`, `auth_headers` (usuario admin semilla), `member_headers` (crea y autentica un usuario `member`) y `default_board_id`, y aísla la base de datos de test por cada test. `test_health.py`, `test_auth.py`, `test_boards.py`, `test_users.py`, `test_ai.py` y `test_db_units.py` agrupan los tests por dominio. Los tests de IA contra endpoints reales llaman a OpenRouter de verdad (pueden fallar de forma intermitente por el modelo gratuito); los de reintento (`test_request_structured_ai_response_*`) usan `monkeypatch` y no tocan la red.
