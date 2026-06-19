# Revisión de código — Proyecto PM Kanban MVP

Fecha: 2026-06-19
Alcance: todo el repositorio (`backend/`, `frontend/`, `docs/`, Docker, scripts). Revisión estática de código + verificación activa de algunos hallazgos (git, eslint).

## Resumen ejecutivo

El código es coherente con lo descrito en `docs/PLAN.md` y todas las pruebas existentes pasan (ver `Pruebas` más abajo). No se encontraron vulnerabilidades de inyección (SQL parametrizado en `db.py`, no hay `eval`/`exec`, React escapa el contenido por defecto). Los hallazgos más importantes eran:

1. Un fichero binario de base de datos (`backend/kanban.db`) está commiteado en git.
2. `npm run lint` falla actualmente (2 errores de ESLint) — el comando documentado no está en verde.
3. La autorización del backend es puramente decorativa: el token de login nunca se valida en ningún endpoint.

**Actualización (2026-06-19): todos los hallazgos de severidad Alta (H1-H3) y Media (M1-M3) han sido corregidos y verificados con la suite de pruebas completa (backend + frontend + E2E). Ver detalle de la corrección en cada hallazgo más abajo.** Los hallazgos de severidad Baja (L1-L7) siguen pendientes y no bloquean el uso del MVP.

**Actualización 2 (2026-06-19): el backend se reorganizó de ficheros monolíticos (`main.py`, `db.py`, `test_main.py`) a paquetes por responsabilidad (`backend/routers/`, `backend/db/`, `backend/tests/`).** Las referencias a número de línea en los hallazgos de abajo corresponden a la estructura *previa* a esa reorganización; el contenido y el estado de cada hallazgo siguen siendo válidos, pero la ubicación exacta puede haber cambiado de fichero. Ver `backend/AGENTS.md` y `CLAUDE.md` para la estructura actual. De camino, la reorganización de `db.py` eliminó el import sin usar `Any` mencionado en L1 (esa parte de L1 ya no aplica; `backend/ai.py` sigue teniéndolo).

## Hallazgos

### Alto

> **Estado: corregido.**

**H1. `backend/kanban.db` está versionado en git**
- Confirmado: `git ls-files | grep kanban.db` lo lista; commit `78a4b45` lo introdujo.
- Riesgo: cada ejecución local/test modifica el fichero binario, generando diffs ruidosos y conflictos de merge; además persiste en el historial cualquier dato de tablero guardado durante desarrollo o pruebas manuales.
- Acción: añadir `backend/kanban.db` y `backend/test-kanban.db` a `.gitignore`, ejecutar `git rm --cached backend/kanban.db`.
- ✅ Hecho: ambas rutas añadidas a `.gitignore`, fichero desindexado con `git rm --cached`. El fichero sigue existiendo en disco (la app funciona igual), solo deja de versionarse.

**H2. `npm run lint` falla en este momento**
- Verificado ejecutando el comando: 2 errores `@typescript-eslint/no-explicit-any`.
  - `frontend/src/components/KanbanBoard.test.tsx:26` — `global.fetch = vi.fn(...) as any`
  - `frontend/src/components/KanbanBoard.integration.test.tsx:43` — mismo patrón
- Riesgo: el comando de lint documentado (y previsiblemente cualquier CI futuro que lo use) no pasa hoy.
- Acción: tipar el mock como `as unknown as typeof fetch` en lugar de `any` en ambos ficheros.
- ✅ Hecho: `npm run lint` pasa sin errores.

**H3. Ningún endpoint del backend valida el token de sesión**
- `backend/main.py:74-82` genera un token y lo guarda en `sessions = {}` (línea 34), pero ningún endpoint (`/api/board` GET/POST, `/api/ai/chat`, `/api/ai/validate`) comprueba `Authorization` ni ese diccionario. El "login" sólo controla qué se muestra en el frontend (`useAuth` en `frontend/src/lib/auth.ts`); el backend está completamente abierto.
- Riesgo: aceptable mientras la app se ejecute sólo en `localhost`, pero `docker-compose.yml:6` publica el puerto `80:8000` sin restringir a `127.0.0.1` — si el contenedor se expone en una red no confiable, cualquiera puede leer/escribir el tablero y disparar llamadas a OpenRouter (coste/cuota) sin autenticarse.
- Acción: añadir una dependencia FastAPI que valide `Authorization: Bearer <token>` contra `sessions` en las rutas de tablero/IA, o documentar explícitamente que el despliegue debe quedar restringido a `127.0.0.1`/red local.
- ✅ Hecho: nueva dependencia `require_auth` en `backend/main.py` valida la cabecera `Authorization: Bearer <token>` contra `sessions`; aplicada a `GET/POST /api/board`, `GET /api/ai/validate` y `POST /api/ai/chat` (devuelven 401 sin token válido). El token se propaga desde `useAuth` → `page.tsx` → `KanbanBoard`/`AiChatPanel`, que ya lo incluyen en todas sus llamadas `fetch`. `/api/auth/logout` ahora también invalida el token recibido (cierra el hueco relacionado L3 de la lista de Bajos).

### Medio

> **Estado: corregido.**

**M1. El login no usa la tabla `users` de SQLite**
- `main.py:33` define `VALID_CREDENTIALS = {"usuario": "contraseña"}` hardcodeado y lo usa en `login()` (línea 76). Mientras tanto, `db.py` crea y siembra una tabla `users` completa (`DEFAULT_USER`, línea 64) que **nunca se consulta**. Son dos fuentes de verdad independientes para el mismo usuario; cambiar una no afecta a la otra.
- Acción: decidir una sola fuente — o el login consulta `users`, o se elimina la tabla/seed hasta que se implemente multiusuario real (el esquema ya está descrito en `docs/db-schema.json` para cuando se implemente).
- ✅ Hecho: `db.py` añade `find_user(username, path)`; `login()` en `main.py` consulta esa función en lugar del diccionario hardcodeado (que se ha eliminado). Verificado con login correcto e incorrecto vía curl.

**M2. Guardado del tablero en cada pulsación de tecla, sin debounce**
- `frontend/src/components/KanbanColumn.tsx:44`: `onChange={(event) => onRename(column.id, event.target.value)}` dispara `updateBoardState` → `setBoard` + `POST /api/board` (fire-and-forget) por cada carácter al renombrar una columna.
- Combinado con `backend/db.py:81-86` (`get_connection`: abre una conexión SQLite nueva por request, sin WAL ni control de bloqueo), escribir rápido puede generar múltiples requests solapados contra el mismo fichero SQLite, con riesgo de `database is locked` o de que una respuesta más antigua llegue después y sobrescriba un título más reciente con uno desactualizado.
- Acción: debounce del guardado (p. ej. `onBlur` o un timer de ~500ms) en lugar de un POST por tecla.
- ✅ Hecho: `KanbanBoard.tsx` actualiza el estado local al instante pero retrasa el `POST /api/board` 500ms tras la última pulsación (con `clearTimeout` en cada cambio y al desmontar). Tests unitarios actualizados para esperar el guardado con `waitFor(..., { timeout: 1000 })`.

**M3. Fallo doble del chat IA requiere reintento manual del usuario**
- `frontend/src/components/AiChatPanel.tsx:62-68` ya reintenta una vez en cliente si `sendAiChat` falla. Si ambos intentos fallan (observado durante esta sesión: el modelo gratuito `openai/gpt-oss-120b:free` devolvió contenido no-JSON dos veces consecutivas), el usuario ve un error genérico y debe reescribir/reenviar. No hay reintento del lado del servidor en `backend/openrouter.py`.
- Acción: considerar un reintento adicional en `call_openrouter_messages` o, como mínimo, un botón "Reintentar" que reenvíe el último mensaje sin que el usuario tenga que reescribirlo.
- ✅ Hecho: el reintento se movió al backend. `request_structured_ai_response` en `ai.py` reintenta hasta 3 veces (constante `MAX_AI_ATTEMPTS`) si la respuesta no es JSON válido o no cumple el esquema, antes de propagar el error. Se eliminó el doble intento duplicado del lado del cliente en `AiChatPanel.tsx` (ya no es necesario y simplifica el componente). Cubierto por dos tests nuevos en `test_main.py` que simulan fallos transitorios sin llamar a la red real.

### Bajo

**L1. Imports sin usar (`Any`)**
- `backend/db.py:6` (`from typing import Any`) y `backend/ai.py:2` (`from typing import Any, Literal, Optional`) — `Any` no se usa en ningún sitio de ambos ficheros.
- No hay linter de Python configurado en `backend/pyproject.toml` (ni ruff, ni flake8, ni mypy) que detecte esto automáticamente.
- Acción: eliminar el import; opcionalmente añadir `ruff` como dependencia de desarrollo.

**L2. `datetime.utcnow()` obsoleto**
- Usado 3 veces en `backend/db.py` (líneas 69, 128, 173); genera `DeprecationWarning` en Python 3.12 (confirmado al ejecutar `pytest`).
- Acción: sustituir por `datetime.now(datetime.UTC)`.

**L3. `/api/auth/logout` es un no-op**
- `backend/main.py:85-87` no recibe el token ni lo elimina de `sessions`. Sumado a H3, el diccionario `sessions` sólo crece (hasta reiniciar el proceso).
- Acción: aceptar el token en el body/cabecera y hacer `sessions.pop(token, None)`.

**L4. `frontend/AGENTS.md` desactualizado**
- La sección "Estado actual" (líneas 57-62) afirma que no hay backend, ni Docker, ni login, ni persistencia — todo eso ya está implementado según `docs/PLAN.md` (partes 2-10 completas).
- Riesgo: puede inducir a error a futuras instancias de Claude/colaboradores que lean ese fichero como fuente de verdad.
- Acción: actualizar o eliminar esa sección; `CLAUDE.md` (raíz) ya refleja el estado real.

**L5. Configuración de Playwright inconsistente con los tests**
- `frontend/playwright.config.ts` arranca un `webServer` con `next dev` en el puerto 3000 y espera a que responda, pero `baseURL` y la navegación explícita en los tests (p. ej. `tests/auth.spec.ts:6`, `page.goto("http://localhost:8000/")`) apuntan al backend FastAPI en el puerto 8000. El `webServer` configurado nunca se usa realmente.
- Riesgo: confunde a quien lee la config; además `npm run test:e2e` no levanta el backend, así que sin un paso manual previo los tests fallan por conexión rechazada (así ocurrió en esta sesión hasta levantar el backend a mano).
- Acción: o bien apuntar `webServer.command` al backend real (build frontend + `uvicorn`), o eliminar el bloque `webServer` y documentar el paso manual directamente en `playwright.config.ts` con un comentario.

**L6. Sin soporte de teclado para drag & drop**
- `KanbanBoard.tsx:25-29` sólo registra `PointerSensor`. `@dnd-kit` soporta `KeyboardSensor` para accesibilidad; sin él, el tablero no es operable sin ratón/táctil.
- Acción (opcional, mejora de accesibilidad): añadir `KeyboardSensor` con `sortableKeyboardCoordinates`.

**L7. Datos semilla duplicados entre frontend y backend**
- `frontend/src/lib/kanban.ts:18-72` (`initialData`) y `backend/db.py:12-62` (`DEFAULT_BOARD`) son el mismo tablero de ejemplo mantenido manualmente en dos lenguajes/ficheros. Hoy están sincronizados, pero es un riesgo de divergencia si se edita uno sin el otro.
- Acción: bajo impacto ahora; si se reorganiza el modelo de datos, considerar una única fuente (p. ej. generar el seed de frontend a partir del JSON que ya sirve `/api/board`, o documentar explícitamente que deben mantenerse en sync).

## Pruebas (referencia)

Ejecutadas en esta sesión antes de la revisión de código:
- Backend (`pytest`, 8 tests): 8/8 tras un reintento — un fallo inicial fue causado por el modelo gratuito de OpenRouter devolviendo contenido no-JSON (ver M3), no un bug de código.
- Frontend unitarias (`vitest`, 10 tests): 10/10.
- Frontend E2E (`playwright`, 5 tests): 5/5 tras un reintento, misma causa que el fallo de backend.

## Plan de acción priorizado

1. ~~Quitar `backend/kanban.db` de git y añadirlo a `.gitignore` (H1).~~ ✅
2. ~~Arreglar los 2 errores de ESLint para que `npm run lint` pase limpio (H2).~~ ✅
3. ~~Decidir y documentar el modelo de autorización del backend (H3).~~ ✅ Implementado con `require_auth` + propagación del token.
4. ~~Unificar el login con la tabla `users` (M1).~~ ✅
5. ~~Debounce del guardado de título de columna (M2).~~ ✅
6. ~~Reintento del chat IA ante fallos del modelo (M3).~~ ✅
7. Resto de hallazgos bajos (L1-L7): limpieza incremental, sin urgencia.

## Verificación tras la corrección (2026-06-19)

- Backend (`pytest`): 11/11 (se añadieron 3 tests: rechazo sin auth, y dos para el reintento de IA).
- Frontend unitarias (`vitest`): 10/10.
- Frontend lint (`eslint`): 0 errores.
- Frontend E2E (`playwright`): 5/5, primera pasada sin necesitar reintento.
- Verificación manual vía `curl`: `/api/board` sin token → 401; login con contraseña incorrecta → 401; tras `logout`, el token deja de ser válido → 401.
