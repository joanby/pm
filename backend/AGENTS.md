# Backend FastAPI

Backend Python FastAPI para el MVP de gestión de proyectos.

- `main.py` define la API, autenticación simulada, endpoints del tablero y validación IA.
- `db.py` inicializa SQLite y persiste el tablero Kanban.
- `main_models.py` define los modelos Pydantic compartidos del tablero.
- `openrouter.py` contiene el cliente directo de OpenRouter.
- `ai.py` construye mensajes para OpenRouter, define el esquema estructurado y valida `message`/`boardUpdate`.
- `OPENROUTER_API_KEY` se lee desde el entorno. En Docker, `scripts/start.sh` pasa `.env` si existe.
- Las pruebas viven en `test_main.py`; la prueba de IA llama a OpenRouter de verdad.
