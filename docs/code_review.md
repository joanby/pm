# Code Review: Project Management MVP

Revision completa del codigo realizada el 2026-06-19.

---

## Resumen

Proyecto MVP funcional con frontend NextJS (React 19), backend FastAPI, persistencia SQLite,
integración con OpenRouter para chat IA, y Docker multi-stage. La arquitectura general es
solida y bien organizada. A continuacion se detallan hallazgos por area.

---

## Backend (Python/FastAPI)

### Fortalezas

- **Buena separacion por responsabilidad**: `routers/` para endpoints, `db/` para persistencia,
  `main.py` solo ensambla. Coherente con `backend/AGENTS.md`.
- **Uso correcto de `lifespan`** para `init_db` en lugar del patron `@app.on_event` deprecado.
- **`model_validator` en `BoardData`** (`main_models.py:20-29`) valida que todas las tarjetas
  referenciadas existan y no haya duplicados. Excelente para integridad.
- **Dependencia `require_auth` via `Depends()`** correctamente implementada y reutilizada en
  `board.py` y `ai.py`.
- **Reintentos en llamadas IA** (`ai.py:129-138`) con `MAX_AI_ATTEMPTS=3` y manejo de errores
  JSON con `parse_ai_response`.
- **Aislamiento de BD en tests** (`conftest.py:19-27`) con fixture `_isolated_db` que crea y
  destruye `test-kanban.db` en cada test.

### Problemas

| Severidad | Archivo | Lineas | Problema |
|-----------|---------|--------|----------|
| **Alto** | `db/seed.py` | 58-64 | Contraseña almacenada en texto plano en campo `password_hash`. Usar `hashlib.sha256` o renombrar a `password` para evitar confusion. |
| **Medio** | `routers/auth.py` | 12 | `sessions` es un dict en memoria: no persiste tras reinicio, no expira, no escala a multi-worker. Documentar como limitacion conocida. |
| **Medio** | `db/boards.py` | 1-6 | `save_board` importa `DEFAULT_USER` de `seed.py` (linea 5). Mejor mover constantes a `connection.py` o `config.py`. |
| **Bajo** | `board.py` | 16 | `POST /api/board` reemplaza todo el tablero. OK para MVP monousuario, pero no soporta actualizaciones parciales ni concurrencia. |
| **Bajo** | `ai.py` | 26-85 | `AI_RESPONSE_SCHEMA` es un dict manual que duplica la definicion de `BoardData`. Podria derivarse con `BoardData.model_json_schema()`. |
| **Bajo** | `routers/board.py` | 17 | `board.model_dump()` sin `by_alias=True` -- no hay alias definidos, pero consistencia. |
| **Info** | N/A | - | No hay limit de tamano de body en requests. FastAPI no lo impone por defecto. |

---

## Frontend (NextJS/React/TypeScript)

### Fortalezas

- **Componentes bien desacoplados**: `KanbanBoard`, `KanbanColumn`, `KanbanCard`, `NewCardForm`,
  `AiChatPanel`, `LoginForm`. Cada uno con responsabilidad unica.
- **Uso correcto de `@dnd-kit`**: `PointerSensor` con `activationConstraint.distance = 6` previene
  drags accidentales. `closestCorners` como collision detection.
- **Esquema de colores via CSS variables** en `globals.css:3-13`, consistente en toda la UI.
- **Debounce en rename de columna** (`KanbanBoard.tsx:23,114-129`) con `RENAME_SAVE_DEBOUNCE_MS=500`.
- **Manejo de `loading`/`error`/`empty` states** en `KanbanBoard`, `AiChatPanel`, `LoginForm`.
- **Test suite completa**: unit tests (vitest) + integration tests + E2E (Playwright).

### Problemas

| Severidad | Archivo | Lineas | Problema |
|-----------|---------|--------|----------|
| **Alto** | `package.json` | 17-19 | Versiones de `@dnd-kit` inconsistentes: `core@^6.3.1`, `sortable@^10.0.0`, `utilities@^3.2.2`. En el monorepo de dnd-kit, sortable requiere core en la misma version major. Verificar compatibilidad. |
| **Medio** | `components/KanbanCard.tsx` | - | No hay edicion de tarjetas desde la UI. AGENTS.md dice que las tarjetas "se pueden editar", pero solo IA puede editar via `boardUpdate`. Falta UI para editar title/details. |
| **Medio** | `lib/kanban.ts` | 164-168 | `createId` usa `Math.random().toString(36).slice(2, 8)`. No criptograficamente seguro (OK para MVP), pero posible colision en creacion rapida. |
| **Bajo** | `components/KanbanBoard.tsx` | 89 | `void saveBoard(nextBoard)` ignora el promise. El error se captura internamente pero estado UI/servidor puede desincronizarse. |
| **Bajo** | `components/AiChatPanel.tsx` | 74 | En catch, `setMessages(messages)` usa closure potencialmente stale. Funciona porque `handleSubmit` no se invoca concurrentemente, pero es fragil. |
| **Bajo** | `components/NewCardForm.tsx` | - | No hay indicador de carga al crear tarjeta. La operacion es sincrona en estado local pero asincrona en save. |
| **Bajo** | `components/KanbanBoard.tsx` | 28-29 | `error` global para todo el board. Operaciones individuales (add/delete card) no tienen feedback localizado de error. |

---

## Pruebas

### Fortalezas

- **Backend**: Tests agrupados por dominio (`test_health.py`, `test_auth.py`, `test_board.py`,
  `test_ai.py`), fixture `_isolated_db` limpia BD entre tests.
- **Frontend**: `KanbanBoard.test.tsx` mockea `global.fetch` correctamente. Pruebas de integracion
  en `KanbanBoard.integration.test.tsx` para flujos API -> UI.
- **E2E**: `ai-chat.spec.ts` prueba el flujo completo de IA con OpenRouter real.

### Problemas

| Severidad | Archivo | Lineas | Problema |
|-----------|---------|--------|----------|
| **Medio** | `tests/test_ai.py` | 7-12, 23-37 | Tests que llaman a OpenRouter real son flaky por naturaleza (como reconoce AGENTS.md). Considerar mocking en CI y dejar tests reales como opcionales. |
| **Medio** | `playwright.config.ts` | 14-18 | `webServer` comando apunta a `npm run dev` en puerto 3000, pero `baseURL` es `http://localhost:8000`. Las E2E tests esperan el backend, no NextJS dev server. Inconsistente. |
| **Bajo** | `tests/test_ai.py` | 40-76 | Tests de validacion de respuesta usan `try/except/else/raise AssertionError` en vez de `pytest.raises(OpenRouterError)`. |
| **Bajo** | `kanban.test.ts` | - | Solo prueba `moveCard`. No hay tests para `createId`, ni para `BoardData` validation, ni para column rename logic. |

---

## Docker e Infraestructura

### Problemas

| Severidad | Archivo | Lineas | Problema |
|-----------|---------|--------|----------|
| **Alto** | `.env` | 1 | API key real de OpenRouter en el repositorio. Rotar inmediatamente si es secreto real. |
| **Medio** | `scripts/start.sh` | 14-16 | Usa `docker run` directo sin `docker-compose`, ignorando el volumen `pm-data` definido en `docker-compose.yml`. Los datos no persisten entre recreaciones. |
| **Medio** | `scripts/start.sh` | 6-16 | Puerto 8000. `docker-compose.yml` mapea puerto 80:8000. Inconsistencia que confunde. |
| **Bajo** | `Dockerfile` | - | Sin `HEALTHCHECK`. |
| **Bajo** | `Dockerfile` | 13-16 | `COPY pyproject.toml` luego `RUN uv pip install` luego `COPY backend`. Capas de Docker optimas. |

---

## Documentacion

| Severidad | Archivo | Problema |
|-----------|---------|----------|
| **Medio** | `docs/db-schema.json` | Describe estructura document-based (arrays con boards embedidos), pero la implementacion SQLite real usa tabla `boards` con columna `data` JSON. El schema describe el contenido de `data`, no la estructura de la BD. |
| **Medio** | `docs/db-schema-example.md` | Muestra `cards` como array dentro de `columns`, distinto a la implementacion real (`cards` es dict global por ID). Las tarjetas tienen timestamps que no existen en codigo real. |
| **Bajo** | `PLAN.md` | Checkboxes mayormente marcados como completados (correcto). QA coverage reporta 10 tests (desactualizado: hay mas de 20 tests entre backend + frontend). |

---

## Recomendaciones Prioritarias

1. **Rotar API key** si `sk-or-v1-...` en `.env` es real. Anadir `.env` a `.gitignore` ya esta pero el archivo ya esta commiteado.
2. **Corregir versiones de `@dnd-kit`** en `package.json` para que `core` y `sortable` coincidan en version major.
3. **Alinear scripts de inicio**: `start.sh` deberia usar `docker compose up -d` o al menos mismo puerto que `docker-compose.yml`.
4. **Corregir `password_hash`**: Usar hashing basico (sha256) o renombrar el campo.
5. **Actualizar docs/ de BD** para reflejar la estructura real (tabla `boards.data` como JSON blob).
6. **Corregir Playwright config**: `baseURL` debe coincidir con el servidor que `webServer` levanta.
7. **Agregar edicion de tarjetas en UI** para cumplir con `AGENTS.md` que dice que las tarjetas se pueden editar.

---

## Score General

| Aspecto | Puntuacion (1-10) | Notas |
|---------|-------------------|-------|
| Arquitectura | 8/10 | Buena separacion, modular, limpia |
| Backend | 7/10 | Solido, pass-hashing pendiente |
| Frontend | 7/10 | Buen dnd-kit, versiones inconsistentes, falta edit |
| Pruebas | 7/10 | Cobertura amplia, tests flaky, playwright config inconsistente |
| Docker | 6/10 | Multi-stage bien, scripts desalineados |
| Documentacion | 5/10 | DB schema desactualizado, PLAN.md no refleja cobertura actual |
| Seguridad | 5/10 | API key expuesta, pass en texto plano |
