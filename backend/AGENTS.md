# Backend MVP (estado actual)

## Propósito

Este backend implementa la base de la API del proyecto con FastAPI y sirve el frontend Next.js compilado de forma estática en `/`.

## Estructura actual

- `app/main.py`
  - `GET /api/health`: endpoint de salud.
  - `GET /`: sirve `backend/static/frontend/index.html`.
  - `GET /{asset_path:path}`: sirve assets del frontend exportado (con fallback a `index.html`).
- `static/frontend/`
  - salida estática de `frontend` generada por `next build` con `output: "export"`.
- `requirements.txt`
  - dependencias mínimas del backend.

## Ejecución en contenedor (multi-stage)

- El `Dockerfile` compila primero el frontend en una etapa Node y copia `out/` al backend.
- La etapa final Python instala dependencias con `uv` y arranca `uvicorn`.
- `docker-compose.yml` expone el backend en `http://localhost:8000`.

## Próximos pasos (según plan)

- Añadir login simulado (Parte 4).
- Persistencia SQLite y rutas Kanban (Partes 5-7).
