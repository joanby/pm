# Aplicación de Gestión de Proyectos MVP

Aplicación local de gestión de proyectos con tablero Kanban y chat con IA (MVP en desarrollo por fases).

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) instalado y en marcha
- Python 3.12+ (solo para ejecutar tests backend en local, opcional)

## Arranque rápido

Desde la raíz del proyecto:

### Windows (CMD, recomendado)

```bat
scripts\start.bat
```

### Windows (PowerShell)

Si PowerShell bloquea scripts, usa el `.bat` o ejecuta:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
.\scripts\start.ps1
```

### Linux / macOS

```bash
./scripts/start.sh
```

La aplicación queda disponible en **http://localhost:8000**.

## Parada

### Windows (CMD)

```bat
scripts\stop.bat
```

### Windows (PowerShell)

```powershell
.\scripts\stop.ps1
```

### Linux / macOS

```bash
./scripts/stop.sh
```

## Verificación manual (Partes 2 y 3)

Con el contenedor en marcha (`scripts\start.bat`):

| URL | Resultado esperado |
|-----|-------------------|
| http://localhost:8000/api/health | `200` con `{"status":"ok"}` |
| http://localhost:8000/ | `200` con pantalla de login "Kanban Studio" |
| http://localhost:8000/favicon.ico | `200` (icono) |

Tras iniciar sesión con `user` / `password`, debe aparecer el tablero Kanban con 5 columnas. Si las credenciales son incorrectas, se muestra un mensaje de error. **Log out** vuelve a la pantalla de login.

## Tests

### Backend (pytest)

Desde la raíz:

```bash
pip install -r backend/requirements.txt -r backend/requirements-dev.txt
python -m pytest backend/tests -v
```

> Para probar assets estáticos en integración, el build del frontend debe existir en `backend/static/frontend/`. Docker lo genera automáticamente; en local: `cd frontend && npm run build` y copiar `out/` a `backend/static/frontend/`.

### Frontend (Vitest)

Desde `frontend/`:

```bash
npm run test:unit
```

### Integración E2E contra backend Docker (Parte 3)

Con el contenedor en marcha en el puerto 8000:

```bash
cd frontend
npm run test:e2e:docker
```

### API Kanban (Parte 6)

Con el contenedor en marcha:

```bash
curl -H "X-MVP-Username: user" http://localhost:8000/api/board
```

Ver [docs/api-kanban.md](docs/api-kanban.md) para el contrato completo.

## Estructura del proyecto

```
pm/
├── backend/          # API FastAPI
├── frontend/         # Next.js (Kanban demo)
├── scripts/          # Arranque/parada Docker multiplataforma
├── docs/PLAN.md      # Plan por fases del MVP
├── Dockerfile        # Build multi-stage (frontend + backend)
└── docker-compose.yml
```

## Credenciales MVP

- Usuario: `user`
- Contraseña: `password`

## Documentación

- Plan de fases: [docs/PLAN.md](docs/PLAN.md)
- Guías por área: [AGENTS.md](AGENTS.md), [backend/AGENTS.md](backend/AGENTS.md), [frontend/AGENTS.md](frontend/AGENTS.md), [scripts/AGENTS.md](scripts/AGENTS.md)

## Estado actual

- **Parte 2 completada:** Docker, FastAPI, scripts multiplataforma, `/api/health` y servicio de estáticos en `/`.
- **Parte 3 completada:** frontend Next.js compilado e integrado en la imagen Docker; tablero Kanban servido por el backend en `/`.
- **Parte 4 completada:** login simulado en cliente con `user/password`, guard de acceso y logout.
- **Parte 5 completada:** esquema SQLite aprobado; BD inicializable vía `init_database()`.
- **Parte 6 completada:** API Kanban con persistencia SQLite (`/api/board`, columnas y tarjetas).
- **Parte 7 completada:** frontend conectado a la API; cambios persisten tras recarga.
- Documentación BD: [docs/db-design.md](docs/db-design.md) · API: [docs/api-kanban.md](docs/api-kanban.md)
- Siguiente fase: Parte 8 (OpenRouter) — ver [docs/PLAN.md](docs/PLAN.md).
