# Code Review 1 — Revisión integral del MVP (Partes 2-10)

**Fecha:** 2026-08-10
**Alcance:** todo el repositorio, no solo un diff — backend (`backend/app/**` + `backend/tests/**`), frontend (`frontend/src/**` + `frontend/tests/**`), infraestructura (`Dockerfile`, `docker-compose.yml`, `scripts/**`, `.dockerignore`, configs) y documentación (`docs/**`, `AGENTS*`, `README.md`).
**Método:** lectura línea a línea de todo el código fuente y configuración; verificación empírica de 3 hallazgos (orden del historial de chat, constraint `check` omitido en el DDL, y plan de ejecución de SQLite); relectura del estado de los hallazgos pendientes de `docs/code_review.md`.

> Esta revisión complementa la anterior (`docs/code_review.md`, que cubría el *diff* de la rama de persistencia + chat IA). Aquí se audita además el *baseline* completo (login, BD, servido estático, infraestructura), se confirma el estado de los 7 hallazgos que quedaron pendientes y se añaden hallazgos nuevos no cubiertos por aquella.

---

## Resumen ejecutivo

El código está bien estructurado, coherente y con una calidad notable para un MVP: separación clara router/service/repository, validación de payloads, manejo de errores consistente, tests unitarios e integración por feature, y una base de datos con esquema machine-readable. No se detectan **bugs críticos que rompan la funcionalidad actual** en el flujo principal. Los problemas se concentran en **robustez ante casos extremos (concurrencia, malformación de salida IA), accesibilidad del drag-and-drop, y fricción de onboarding/tooling**.

| # | Hallazgo | Severidad | Área | Estado |
|---|----------|-----------|------|--------|
| C2 | Update del tablero rechazado por la IA se descarta en silencio (previa #6) | 🟠 Alta | Backend IA | Pendiente |
| E1 | `npm run test:e2e` (dev, :3000) no puede funcionar: sin proxy/rewrites a la API | 🟠 Alta | Tooling | Pendiente |
| E2 | `docker compose up` falla en un clon limpio: `env_file: .env` no existe | 🟠 Alta | Onboarding | Pendiente |
| C5 | Pérdida de ediciones del usuario (lost update) si edita el tablero mientras la IA responde | 🟠 Alta | Backend IA | Pendiente |
| C4 | Fallback de salida IA muestra el JSON crudo como mensaje al usuario | 🟡 Media | Backend IA | Pendiente |
| D2 | Reintentar un chat fallido duplica la burbuja del usuario (previa #4) | 🟡 Media | Frontend | Pendiente |
| D3 | Errores de chat: mismo mensaje "reintentable" para fallos transitorios y permanentes (previa #10) | 🟡 Media | Frontend | Pendiente |
| C3 | Sin retry/backoff en `OpenRouterClient`; el E2E enmascara el 502 (previa #7) | 🟡 Media | Backend IA | Pendiente |
| C8 | Tests de integración con red real fallan (no `skip`) si falta `OPENROUTER_API_KEY` | 🟡 Media | Tests | Pendiente |
| B2 | `check` declarado en `db-schema.json` no se genera en el DDL | 🟡 Media | Backend BD | Pendiente |
| D4 | Posible hydration mismatch / flash de login al leer `localStorage` en inicializadores de `useState` | 🟡 Media | Frontend | Pendiente |
| D5 | Drag-and-drop solo con puntero: sin reordenación por teclado | 🟡 Media | Frontend | Pendiente |
| C1 | Historial de chat sin desempate de orden (previa #2) — latente | 🟡 Media | Backend IA | Pendiente |
| B1 | `get_board` N+1 y relecturas tras cada mutación (previa #8) | 🟢 Baja | Backend | Pendiente |
| D1 | Wrapper `request<T>` duplicado entre `kanban-api.ts` y `ai-api.ts` (previa #9) | 🟢 Baja | Frontend | Pendiente |
| B3 | `Card` sin validación de título; validadores duplicados; dead code en `schema.py` | 🟢 Baja | Backend | Pendiente |
| B4 | `replace_board` resetea `created_at`/`updated_at` de tarjetas y columnas | 🟢 Baja | Backend | Pendiente |
| B5 | `create_card` calcula posición con `MAX(position)+1` no atómico | 🟢 Baja | Backend | Pendiente |
| C6 | `ChatService.chat` abre 4 conexiones y repite lookups por request | 🟢 Baja | Backend IA | Pendiente |
| C7 | Board ya reemplazado si falla la persistencia del historial (no atómico) | 🟢 Baja | Backend IA | Pendiente |
| D6 | `replaceBoard` exportado y sin uso en la app | 🟢 Baja | Frontend | Pendiente |
| D7 | Debounce de rename no se limpia al hacer logout | 🟢 Baja | Frontend | Pendiente |
| D8 | Race entre movimientos optimistas simultáneos | 🟢 Baja | Frontend | Pendiente |
| E3 | Artefactos de build del frontend versionados en `backend/static/frontend` | 🟢 Baja | Tooling | Pendiente |
| E4 | `.dockerignore` no excluye `backend/data` ni `.env` | 🟢 Baja | Infra | Pendiente |
| E5 | Contenedor en ejecución como root y sin `healthcheck` | 🟢 Baja | Infra | Pendiente |
| E6 | Pequeños desfases entre docs (PLAN/AGENTS) y estado real | 🟢 Baja | Docs | Pendiente |

**Fortalezas a mantener:** la corrección del `UNIQUE(column_id, position)` con aparcamiento en rango negativo (`repository.py:_shift_positions`) es sólida y está bien comentada y testeada; los 3 bugs críticos de la revisión anterior están confirmados como corregidos; la validación estricta de `BoardData` (referencias cruzadas entre `columns[].cardIds` y `cards{}`) cierra bien el caso de tarjetas duplicadas; la capa de errores HTTP del backend es consistente; la cobertura de tests por feature es buena y el contrato de API está documentado.

---

## A. Seguridad y autenticación

### A1. Autenticación simulada por header (observación, aceptada en MVP)
`backend/app/auth.py` confía ciegamente en `X-MVP-Username` y `frontend/src/lib/auth.ts` valida las credenciales solo en cliente (`user/password` fijas). Cualquiera puede llamar a la API de otro usuario simplemente enviando otro username. Está **documentado y es una decisión consciente del MVP** (`docs/PLAN.md`, sección de decisiones). No se cuenta como defecto, pero conviene dejar constancia para la evolución: cuando se introduzca autenticación real (JWT/supabase), este es el primer punto a sustituir, y el flujo de historia/`seed` ya está preparado (tabla `users`, `boards.user_id`).

### A2. `docker compose up` falla en un clon limpio porque exige `.env`
`docker-compose.yml:7-8` usa `env_file: - .env`. `.env` está en `.gitignore` (correcto), por lo que un clon limpio **no tiene** ese archivo y `scripts/start.bat`/`start.sh`/`start.ps1` fallan al arranque. El propio backend tolera la ausencia de `.env` (`_load_root_env` lo ignora), pero Compose no.
**Sugerencia:** documentar en `README` el paso `cp .env.example .env` como requisito previo obligatorio, o usar `env_file` con `required: false` (Compose ≥ 2.24), o proporcionar un `.env` por defecto válido con la key vacía.

### A3. `.dockerignore` no excluye `backend/data` ni `.env`
`.dockerignore` ignora `.venv`, `__pycache__`, `frontend/.next`, etc., pero no `backend/data` ni `.env`. El contexto de build se envía al daemon y `COPY backend /app/backend` copiaría una BD local de desarrollo (si existe) dentro de la imagen. En el flujo actual el volumen `pm-data` lo enmascara en runtime, pero si alguien ejecuta la imagen sin volumen heredaría datos de la máquina del build.
**Sugerencia:** añadir `backend/data` (salvo `.gitkeep`) y `.env` a `.dockerignore`.

### A4. Contenedor como root y sin healthcheck
El `Dockerfile` no define usuario y `CMD` corre uvicorn como root. Para un MVP local es aceptable, pero añadir `HEALTHCHECK` (a `/api/health`) y un usuario sin privilegios es barato y mejora el arranque robusto en orquestadores.

---

## B. Backend — Kanban y base de datos

### B1. (previa #8, vigente) `get_board` es N+1 y se re-ejecuta tras cada mutación
`KanbanRepository.get_board` (`repository.py:38-76`) lanza 1 consulta por columna además de la de columnas (5 columnas → 6 round-trips) y `replace_board`, `update_column_title` y `move_card` vuelven a llamar a `get_board` para construir la respuesta, descartando datos que ya tenían (`repository.py:125`, `:148`, `:344`). En `replace_board` es especialmente redundante: re-lee el tablero que acaba de escribir desde el payload.
**Sugerencia:** un único `SELECT ... FROM cards JOIN columns` ordenado por posición reconstruye el tablero en un round-trip; los métodos de mutación pueden devolver el estado ya conocido.

### B2. El `check` declarado en `db-schema.json` no se refleja en el DDL generado
`chat_messages.role` declara `"check": ["user", "assistant"]` (`docs/db-schema.json:97`), pero `build_create_table_sql` (`schema.py:61-98`) no emite ningún `CHECK`. Verificado empíricamente: el DDL generado para `chat_messages` no contiene la restricción. La única defensa es de aplicación (`ChatRepository.add_message`, `chat_repository.py:44`). El esquema JSON es la "fuente única de verdad" declarada, así que el DDL debería reflejar lo que declara.
**Sugerencia:** soportar `check` en `build_create_table_sql` (o eliminar la clave del JSON si se considera over-engineering en MVP).

### B3. Validación y duplicación de código en modelos
- `Card` (`kanban/models.py:6-12`) no valida `title`: un update IA con `title` vacío pasa el modelo (las columnas sí validan). Recomendado aplicar el mismo `title_not_empty` a `Card` para que las tarjetas creadas por IA no puedan llegar vacías.
- El validador `title_not_empty` está duplicado en `Column`, `ColumnUpdate`, `CardCreate` y `CardUpdate` (`models.py:21-27`, `78-84`, `92-98`, `105-113`). Un validador/base compartida eliminaría 4 copias.
- `schema.py:53-54` tiene un `if` sin efecto con `pass` (dead code):
  ```python
  if column_def.get("required") and "default" not in column_def and not column_def.get("primaryKey"):
      pass  # required columns are valid without default
  ```
  No valida nada; se puede eliminar o convertir en un `raise` real.

### B4. `replace_board` resetea los timestamps de tarjetas y columnas
`repository.py:84-118` borra e inserta de nuevo con `created_at = now`. Cada `PUT /api/board` (cada sync IA o E2E) pierde el historial de creación de las tarjetas. No afecta a la funcionalidad actual (los timestamps no se exponen), pero si en el futuro se quiere auditar o mostrar "creado el...", se pierde. `UPDATE cards SET column_id, position` en el move (y en general la estrategia delete+insert) también afecta.
**Sugerencia:** al menos en `replace_board`, preservar `created_at` de las filas que ya existían (upsert), o documentar la pérdida como decisión.

### B5. `create_card` calcula la posición con `MAX(position)+1` no atómico
`repository.py:172-176`: `SELECT COALESCE(MAX(position), -1) + 1` dentro de una conexión por request. Dos creaciones concurrentes en la misma columna pueden obtener la misma posición y disparar `IntegrityError` (UNIQUE). No gestionado → 500. Improbable con un solo usuario en MVP, pero es un patrón a evitar (p.ej. `INSERT ... SELECT` con `LIMIT`/OFFSET, o `position = (SELECT COUNT(*)...)` dentro de la transacción).

### B6. Observación: transaccionalidad y modo SQLite
- Las operaciones de escritura dependen del "autocommit diferido" de Python (la transacción implícita se abre con el primer DML y se cierra en `commit()`), de modo que `replace_board`/`move_card` son de facto atómicas. Conviene que quede explícito (usar `with connection:` o `BEGIN IMMEDIATE`) para no romperlo por accidente al refactorizar.
- No se configura WAL ni `busy_timeout` explícito (`connection.py`). El default de `sqlite3.connect` (5 s) mitiga bloqueos, pero con uvicorn multi-thread y un volumen Docker la BD puede latar. Para MVP es suficiente; para el paso a multiusuario conviene WAL + `busy_timeout`.

---

## C. Backend — IA (OpenRouter, chat estructurado)

### C1. (previa #2, vigente pero latente) Orden del historial sin desempate
`ChatRepository.list_messages` ordena `ORDER BY created_at DESC` con timestamps a resolución de segundo (`chat_repository.py:13-15`, `21-31`) y sin desempate, y luego revierte en Python. `_persist_exchange` escribe user y assistant en el mismo segundo. He reproducido el flujo real contra SQLite: el orden **salió correcto** porque SQLite resolvió el empate por rowid/orden de inserción y el plan de ejecución actual es `SCAN + TEMP B-TREE FOR ORDER BY` (no usa índice). Es decir, hoy funciona **por accidente**, no por garantía del SQL: un cambio de plan, una tabla mayor o un merge sort distinto pueden mostrar el reply del assistant antes que el mensaje del usuario, corrompiendo tanto la UI (`GET /api/ai/history`) como el contexto que se reenvía al modelo (`build_chat_messages`).
**Sugerencia (barata):** `ORDER BY created_at, id` (o un `rowid`), y/o guardar sub-segundos. Corregirlo ahora evita un bug intermitente.

### C2. (previa #6, vigente — Alta) Un update del tablero rechazado por la IA se descarta en silencio
`chat_service.py:42-48`:
```python
if structured.board is not None:
    try:
        validate_board_column_ids(current_board, structured.board)
        board = self.kanban_service.replace_board(username, structured.board)
        board_updated = True
    except OpenRouterResponseError:
        pass
```
Cuando el modelo viola el contrato (renombra/reordena columnas fijas, etc.), se traga la excepción y se devuelve el mensaje natural del modelo ("He movido la tarjeta a Done") con `boardUpdated: false` y el tablero sin cambios: **el usuario ve una afirmación que no ocurrió**, sin indicador de error en la respuesta ni en la UI, y sin log para observabilidad. Es el hallazgo más relevante pendiente del flujo IA.
**Sugerencia:** propagar el rechazo — añadir un aviso al `message`, o una bandera/error explícito que el frontend pueda renderizar, además de loguear el board rechazado.

### C3. (previa #7, vigente) Sin retry/backoff en `OpenRouterClient`
`client.py:80-104` hace un único intento HTTP y convierte cualquier error en excepción. El E2E (`frontend/tests/kanban.spec.ts:139-162`) parchea la flakiness del modelo free (502 en llamadas en frío) reintentando desde la UI, en vez de arreglarlo donde se genera el problema: un usuario real recibe el fallo sin recuperación. Además el test pierde señal: un fallo real del endpoint se enmascara como "502 transitorio".
**Sugerencia:** retry con backoff para 502/503/timeout dentro de `OpenRouterClient` (beneficia a los usuarios reales) y simplificar después el E2E a una única espera.

### C4. Fallback muestra el JSON crudo al usuario
`_parse_or_fallback` (`chat_service.py:61-70`): si la salida estructurada es inválida (p.ej. board malformado), usa el **texto crudo completo** de la respuesta (que en `json_mode` es el JSON entero) como mensaje. El usuario vería algo como `{"message":"...","board":{...}}` en la burbuja del chat.
**Sugerencia:** intentar extraer al menos el campo `message` del JSON crudo antes de degradar a texto plano (reutilizar `extract_json_text` + parse parcial), o mostrar un mensaje genérico.

### C5. Lost update: la IA puede sobrescribir ediciones del usuario hechas mientras responde
`chat_service.chat` envía el board actual y espera hasta 30 s (`OPENROUTER_TIMEOUT_SECONDS`). Si el usuario arrastra/crea/borra una tarjeta durante esa ventana y el modelo responde con `board` (estado completo), `replace_board` pisa esos cambios sin ninguna detección de conflicto ni versionado. No es un fallo de código sino de diseño de concurrencia, pero es un escenario realista (drag rápido + IA lenta).
**Sugerencia:** aunque sea para MVP, comparar un `updated_at`/versión del board antes de aplicar, y rechazar (o re-aplicar sobre) el update si el usuario cambió algo mientras tanto.

### C6. El flujo de chat abre 4 conexiones y repite lookups
`ChatService.chat`: `get_board` (conexión 1) → `_load_history` (conexión 2, que re-resuelve user→board que `get_board` ya hizo) → `replace_board` (conexión 3) → `_persist_exchange` (conexión 4). Para un MVP no importa, pero la resolución `get_user_id`/`get_board_id_for_user` se duplica y el historial podría cargarse en la misma conexión que el board.
**Sugerencia:** resolver user/board una vez y compartirlo, o usar una sola conexión para todo el request.

### C7. No-atomicidad entre board y chat
Si `_persist_exchange` falla (p.ej. error de BD) tras haber aplicado `replace_board`, la petición devuelve 500 pero **el tablero ya quedó modificado**; el usuario reintentaría y obtendría un mensaje duplicado/estado inconsistente. Un `try` alrededor de la persistencia o envolver todo en una transacción común evitaría el estado intermedio.

### C8. Tests de integración con red real fallan (no se saltan) sin key
`tests/integration/test_ai_openrouter.py` y `test_ai_chat.py` lanzan `AssertionError` si falta `OPENROUTER_API_KEY`. Ejecutar la suite completa `python -m pytest backend/tests` en una máquina/CI sin key **falla** en vez de esquivar esos tests, contradiciendo en la práctica que "solo esos dos archivos necesitan la key" (`backend/AGENTS.md`). También dependen de la fiabilidad de un servicio externo de pago.
**Sugerencia:** `@pytest.mark.skipif(not key, ...)` (o un marcador `integration-ai`) para que la suite base sea verde sin red, y mantener el smoke real bajo una var de entorno explícita.

---

## D. Frontend

### D1. (previa #9, vigente) `request<T>` duplicado
`kanban-api.ts:19-43` y `ai-api.ts:28-48` son wrappers casi idénticos (header `X-MVP-Username`, error tipado). Cualquier cambio futuro en autenticación o errores hay que hacerlo dos veces.
**Sugerencia:** extraer un `request<T>(username, path, ErrorClass, init)` compartido.

### D2. (previa #4, vigente — Media) Retry duplica la burbuja del usuario
`AiChatSidebar.submitMessage` añade siempre una burbuja `user` al inicio (`AiChatSidebar.tsx:71`) y `handleRetry` (`:103-108`) la vuelve a llamar tras un fallo **sin quitar la burbuja anterior**. Resultado: el mismo mensaje aparece dos veces en el historial tras un reintento. El test `AiChatSidebar.test.tsx` no comprueba el conteo de burbujas, por lo que pasa inadvertido.
**Sugerencia:** no re-añadir la burbuja en retry (mantener el mensaje pendiente en estado y reusarlo), o eliminar/marcar la burbuja fallida antes de reintentar.

### D3. (previa #10, vigente) El error de chat no distingue transitorio de permanente
`submitMessage` descarta el error (`catch {` en `AiChatSidebar.tsx:85-88`) y siempre muestra "Unable to reach the AI assistant. Please try again." con botón Retry. Un 503 permanente (p.ej. falta de `OPENROUTER_API_KEY`) recibe la misma UX "reintenta" que un 502/504 transitorio. `AiApiError` ya transporta `status`.
**Sugerencia:** ramificar por `error instanceof AiApiError && error.status` y ofrecer Retry solo para 502/504/red.

### D4. Hydration mismatch / flash de login
`KanbanBoard.tsx:38-46` inicializa `isAuthenticated`/`sessionUsername` leyendo `localStorage` en los inicializadores de `useState`. Con `output: "export"` la página `/` se pre-renderiza como HTML estático (sin `window`), así que el HTML servido es siempre la pantalla de login. En el cliente, la hidratación re-ejecuta el inicializador con `localStorage` presente → estado distinto al HTML servido → mismatch de hidratación y parpadeo de login para sesiones activas. Funciona (React se re-renderiza en cliente), pero con warning en consola y flash. Los tests unitarios lo cubren con `localStorage` mockeado y el E2E no ejercita el flujo "sesión restaurada" en navegador real, así que no se detecta.
**Sugerencia:** leer la sesión en un `useEffect` y renderizar un estado neutro/loading inicialmente (patrón estándar), o hidratar solo en cliente.

### D5. Accesibilidad del drag-and-drop
Solo se registra `PointerSensor` (`KanbanBoard.tsx:55-59`); sin `KeyboardSensor`, las tarjetas no son reordenables con teclado. Además el input de título de columna usa `aria-label="Column title"` idéntico en las 5 columnas (`KanbanColumn.tsx:45`), y el botón de borrado depende del texto de la tarjeta. Para un MVP es aceptable, pero añadir `KeyboardSensor` y etiquetas distintivas es de bajo coste y alto valor.
**Sugerencia:** añadir `KeyboardSensor` (y `SortableKeyboardCoordinates`), `aria-label` con el nombre de la columna, y un `aria-describedby` si se desea.

### D6. `replaceBoard` exportado y sin uso en la app
`kanban-api.ts:89-96` exporta `replaceBoard`, pero ningún módulo de `src/` lo usa (solo el helper E2E usa `request.put` directo). Código muerto o pendiente de integración; si no se va a usar desde la UI, conviene quitarlo o conectar el caso de "sincronizar estado completo" que aún no existe.

### D7. El debounce de rename no se limpia al hacer logout
`handleRenameColumn` (`KanbanBoard.tsx:156-184`) programa un `setTimeout` de 400 ms. El efecto de limpieza solo corre al desmontar (`:103-109`), pero `KanbanBoard` nunca se desmonta: tras logout se re-renderiza a login y los `renameTimeouts` pendientes siguen disparando un `PATCH` (con el username capturado en el closure, así que no envía datos erróneos, pero es una petición tras logout y un caso de estado zombie).
**Sugerencia:** limpiar `renameTimeouts` dentro de `handleLogout`.

### D8. Race entre movimientos optimistas concurrentes
El drag no se bloquea durante `isSyncing` (`KanbanBoard.tsx:137-154`): dos drags rápidos encadenan dos `moveCardOnBoard`; si las respuestas llegan en orden distinto, el segundo `setBoard(syncedBoard)` puede clavar un estado que no refleja el último movimiento. Improbable por la UI, pero es un patrón clásico de actualización desordenada.

### D9. Observación: `createId` con `Math.random` + `Date.now`
`kanban.ts:164-168` genera IDs de cliente no criptográficos pero con colisión improbable; adecuado para claves React. No es defecto.

---

## E. Infraestructura, tooling y docs

### E1. `npm run test:e2e` (dev, :3000) no puede pasar
`playwright.config.ts` apunta a `http://127.0.0.1:3000` (dev server), pero `next.config.ts` solo tiene `output: "export"` y **no define ningún proxy/rewrite**: `fetch("/api/board")`, `/api/ai/*` desde el navegador a :3000 → 404 (no existe la ruta en Next). Los tests de `kanban.spec.ts` requieren la API para hacer login y ver 5 columnas, así que esta suite (documentada en `CLAUDE.md` y `frontend/AGENTS.md` como `npm run test:e2e`) no puede ser verde. Solo `test:e2e:docker` funciona realmente.
**Sugerencia:** o bien documentar que la suite dev requiere arrancar el backend en :3000 (proxy en `next.config.ts`), o bien retirar/renombrar la suite dev para que no induzca a error. Nótese que con `output: "export"` los rewrites no aplican en producción, pero en dev `next dev` sí los soporta (se podría añadir `rewrites()` condicional por entorno).

### E2. Build artifacts del frontend versionados
`backend/static/frontend/**` (el `out/` de Next) está commiteado en el repo. Ventaja: `test_home_page.py`/`test_static_assets.py` pasan sin rebuild local. Desventaja: churn en cada build, riesgo de drift con `frontend/src`, y ruido en PRs. Para un MVP de 1 persona es tolerable; si el repo crece, conviene generar en CI y añadir a `.gitignore` (el Dockerfile ya lo regenera).

### E3. (ver A2) Onboarding del clon limpio
Ya cubierto en A2: falta el `cp .env.example .env` documentado como paso obligatorio, o `required: false`.

### E4. `.dockerignore` incompleto
Ver A3.

### E5. Contenedor como root y sin healthcheck
Ver A4.

### E6. Desfases menores de documentación
- `docs/PLAN.md:365` (Parte 7) cita "6 escenarios" E2E Docker; hoy son 9. El `PLAN.md:29` sí está actualizado a 9/9.
- `frontend/AGENTS.md` describe estructura correcta, pero no menciona la suite E2E que hoy no corre contra :3000 (ver E1).
- `README.md` no documenta el paso obligatorio de `.env` (ver A2/E3).
- `docs/code_review.md` está etiquetado como revisión de diff; esta revisión cubre el resto (intencionadamente).

---

## Estado de los hallazgos de la revisión anterior (`docs/code_review.md`)

| Hallazgo previo | Severidad original | Estado en esta revisión |
|-----------------|--------------------|-------------------------|
| #1 `move_card` viola UNIQUE | Crítica | ✅ Corregido y verificado (staging en rango negativo). |
| #3 Backend no importa sin key | Crítica | ✅ Corregido (services construidos por request). |
| #5 Tarjeta duplicada → IntegrityError | Crítica | ✅ Corregido (`validate_card_references`). |
| #2 Orden historial sin desempate | Alta | ⏳ Pendiente (latente; funciona por rowid hoy, ver C1). |
| #6 Update IA rechazado en silencio | Alta | ⏳ Pendiente (ver C2). |
| #4 Retry duplica burbuja | Media | ⏳ Pendiente (ver D2). |
| #7 E2E enmascara 502 | Media | ⏳ Pendiente (ver C3). |
| #8 N+1 en `get_board` | Baja | ⏳ Pendiente (ver B1). |
| #9 `request<T>` duplicado | Baja | ⏳ Pendiente (ver D1). |
| #10 Error de chat genérico | Media | ⏳ Pendiente (ver D3). |

---

## Plan de acción sugerido (por prioridad)

**Primera tanda — robustez funcional (sin refactors grandes):**
1. **C2** — propalar el rechazo del update IA al mensaje/flag y loguearlo (Alta, UX correcta).
2. **C4** — no mostrar JSON crudo al usuario en el fallback (Media).
3. **C1** — añadir desempate `id` al `ORDER BY` del historial (Media, un commit trivial).
4. **D2 + D3** — retry sin duplicar burbuja y error por `status` (Media, UX).
5. **C3** — retry/backoff en `OpenRouterClient` y simplificar el E2E (Media).
6. **B2 + B3** — emitir `check` en DDL y validar `Card.title` (Media/Baja).

**Segunda tanda — concurrencia y datos:**
7. **C5** — detección de conflicto de board antes de aplicar updates IA (Alta conceptual, requiere diseño).
8. **B5, B4, C7** — atomicidad/posición en `create_card`, preservar timestamps en `replace_board`, transacción board+chat.

**Tercera tanda — tooling y accesibilidad:**
9. **A2/E1** — fix de onboarding (`.env`) y decisión sobre la suite dev E2E.
10. **D4** — eliminar el flash/mismatch de login; **D5** — `KeyboardSensor` y labels.
11. **A3/E4, E5, B1, D1, D6, D7** — higiene de Dockerignore, healthcheck, N+1, deduplicar wrapper, código muerto, cleanup de timers.

---

## Notas de ángulo que no produjeron hallazgos

- **Inyección SQL / sanitización:** todas las queries usan parámetros (`?`); no se encontró interpolación de entrada del usuario salvo las condiciones ya parametrizadas de `_shift_positions`.
- **Convenciones CLAUDE.md/AGENTS.md:** se respetan las decisiones documentadas (credenciales, fases, paleta de color); solo hay desfases menores de docs (E6).
- **Pruebas:** buena cobertura por feature y tests de regresión de los 3 bugs críticos. Los únicos huecos reseñables son la ausencia de test para el flujo "sesión restaurada" en navegador real (D4) y el conteo de burbujas en retry (D2).
