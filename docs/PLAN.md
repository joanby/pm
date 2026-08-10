# Plan general del proyecto MVP

## Reglas globales de ejecución

- Credenciales oficiales del MVP: `user/password`.
- No cerrar ninguna parte funcional sin pruebas unitarias e integración.
- Cobertura objetivo orientativa: hasta ~80% solo cuando sea sensato y sin añadir pruebas de bajo valor para alcanzarlo.
- No es obligatorio alcanzar 80%; es preferible menos cobertura con pruebas útiles que muchas pruebas triviales.
- Priorizar simplicidad y evitar sobreingeniería.
- Validar siempre por evidencia observable (logs, respuestas API, comportamiento UI).

---

## Estado actual del proyecto

| Parte | Título | Estado |
|-------|--------|--------|
| 1 | Planificación | Completada |
| 2 | Docker + FastAPI + scripts | Completada |
| 3 | Frontend estático integrado | Completada |
| 4 | Login simulado | Completada |
| 5 | Modelado de base de datos | Completada (aprobada) |
| 6 | Backend Kanban | Completada |
| 7 | Frontend + Backend persistente | Completada |
| 8 | Conectividad IA (OpenRouter) | Completada |
| 9 | IA con salidas estructuradas | Completada |
| 10 | Widget lateral de chat IA | Completada |

**Verificación reciente (local):** 44 tests backend (pytest), 20 tests unitarios frontend (Vitest), 9/9 E2E Docker (`npm run test:e2e:docker` contra `http://localhost:8000`).

**Estado:** MVP Partes 2-10 completadas.

---

## Decisiones de diseño transversales (Partes 2-7)

Decisiones tomadas durante la implementación y no obvias desde el checklist de cada parte:

### Infraestructura y Docker

- **Gestión de paquetes Python en contenedor:** `uv pip install` (imagen `ghcr.io/astral-sh/uv:python3.12-bookworm-slim`), sin `pip` directo.
- **Build multi-stage:** etapa Node compila el frontend (`next build` con `output: "export"`) y copia `out/` a `backend/static/frontend/`.
- **Esquema BD en runtime:** la app lee `docs/db-schema.json` al arrancar (`backend/app/db/schema.py`). En Docker se copia explícitamente a `/app/docs/db-schema.json`; `.dockerignore` excluye `docs/*` excepto `docs/db-schema.json`.
- **Persistencia en Docker:** volumen nombrado `pm-data` montado en `/app/backend/data` (`docker-compose.yml`). La BD SQLite vive en `backend/data/pm.db`.
- **Scripts de arranque:** preferir `scripts/start.bat` en Windows si PowerShell bloquea `.ps1`.

### Autenticación MVP (Partes 4, 6 y 7)

- **Login simulado en frontend:** credenciales `user/password`; sesión en `localStorage` (`pm-mvp-auth`, `pm-mvp-username`).
- **Identificación en backend:** header HTTP `X-MVP-Username: user` en todas las rutas Kanban. No hay JWT ni cookies de sesión en el MVP.
- **Coherencia:** el username guardado en sesión cliente se reenvía en cada petición API.

### Persistencia y modelo de datos (Partes 5 y 6)

- **Motor MVP:** SQLite local; evolución futura prevista a **Supabase** sin cambiar el modelo relacional documentado.
- **Esquema machine-readable:** `docs/db-schema.json`; diseño y trade-offs en `docs/db-design.md`.
- **IDs como TEXT:** compatibles con IDs del frontend (`col-backlog`, `card-1`, IDs generados en cliente).
- **Seed demo idempotente:** al arrancar la app (`lifespan` en `main.py`), si no existe el usuario `user` se insertan tablero, 5 columnas y 8 tarjetas demo (`backend/app/kanban/seed.py`).
- **Un tablero por usuario:** regla de negocio en capa de aplicación, no UNIQUE en BD.
- **Password en texto plano:** coherente con login simulado; documentado como no apto para producción.

### API Kanban (Parte 6)

- **Contrato documentado:** `docs/api-kanban.md`.
- **Formato del tablero:** JSON con `columns[]` (cada una con `cardIds`) y `cards{}` (diccionario id → tarjeta), alineado con el tipo `BoardData` del frontend.
- **Arquitectura backend:** router → service → repository sobre SQLite.
- **Sincronización completa:** `PUT /api/board` reemplaza el estado entero del tablero (útil para tests y futura IA).
- **Movimiento de tarjetas:** `PUT /api/cards/{id}/move` devuelve el tablero completo actualizado.

### Frontend conectado a API (Parte 7)

- **Cliente API:** `frontend/src/lib/kanban-api.ts` (fetch con header `X-MVP-Username`).
- **Carga inicial:** tras login o restauración de sesión, `GET /api/board`.
- **Renombrado de columnas:** debounce de 400 ms antes de `PATCH /api/columns/{id}`.
- **Alta de tarjetas:** espera respuesta `POST` antes de actualizar UI (no optimista).
- **Movimiento y borrado:** UI optimista con rollback si la API falla.
- **Estados UX:** loading, error con reintento, indicador “Saving…” durante sync.

### Pruebas E2E Docker (Partes 3 y 7)

- **Config dedicada:** `frontend/playwright.docker.config.ts` apunta a `http://127.0.0.1:8000`.
- **Aislamiento de estado:** antes de cada test E2E Docker se resetea el tablero vía `PUT /api/board` con el estado demo (`frontend/tests/e2e-helpers.ts`), porque la BD SQLite del volumen Docker persiste entre ejecuciones.
- **Global setup:** `frontend/tests/docker-global-setup.ts` espera `/api/health` y hace reset inicial.
- **Variable de entorno:** `PM_E2E_DOCKER=1` activa el reset en `beforeEach` de `kanban.spec.ts`; los E2E de desarrollo (`:3000`) no lo usan.

---

## Parte 1: Planificación

### Objetivo
Definir el plan detallado para Partes 2-10 y documentar el estado real del frontend actual.

### Dependencias
- Ninguna.

### Entregables
- `docs/PLAN.md` enriquecido con checklist, pruebas y criterios de éxito por parte.
- `frontend/AGENTS.md` con descripción técnica del frontend demo existente.

### Lista de verificación
- [x] Definir estructura repetible por parte (objetivo, checklist, pruebas, éxito).
- [x] Unificar credenciales del plan a `user/password`.
- [x] Añadir criterios de éxito verificables en todas las partes.
- [x] Documentar pruebas unitarias e integración requeridas por parte.
- [x] Crear `frontend/AGENTS.md` describiendo código actual del demo.

### Pruebas
- **Revisión documental:** validación manual de consistencia entre `AGENTS.md` y este plan.
- **Validación de alcance:** confirmación del usuario del plan final.

### Criterios de éxito
- [x] Cada parte (2-10) incluye checklist, pruebas y criterios de éxito.
- [x] Credenciales alineadas a `user/password` en todo el plan.
- [x] `frontend/AGENTS.md` creado y coherente con el código existente.

### Riesgos y mitigación
- Riesgo: plan demasiado genérico para ejecución real.
  - Mitigación: checklist accionable y criterios observables en cada parte.
- Riesgo: divergencia entre documentación y estado real del frontend.
  - Mitigación: mantener `frontend/AGENTS.md` actualizado antes de iniciar Parte 2.

---

## Parte 2: Estructura (Docker + FastAPI + scripts)

### Objetivo
Disponer de una base ejecutable local con Docker, backend FastAPI y scripts multiplataforma.

### Dependencias
- Parte 1 completada.

### Entregables
- Configuración Docker en raíz.
- Estructura inicial de backend en `backend/`.
- Scripts de inicio/parada en `scripts/` para Mac, Windows y Linux.
- Endpoint HTML estático y endpoint API de verificación.
- Imagen incluye esquema BD (`docs/db-schema.json`) necesario para el lifespan de la app.

### Decisiones tomadas
- Puerto único `8000` para frontend estático + API.
- Volumen Docker `pm-data` para persistir SQLite entre reinicios del contenedor.
- Ver detalle de build multi-stage y `uv` en la sección *Decisiones de diseño transversales* más arriba.

### Lista de verificación
- [x] Crear Dockerfile y configuración de ejecución local.
- [x] Inicializar backend FastAPI mínimo.
- [x] Implementar endpoint `/api/health` (o equivalente).
- [x] Servir página estática de prueba en `/`.
- [x] Crear scripts `start` y `stop` por plataforma.
- [x] Documentar comandos básicos en `README`/`docs` si aplica.

### Pruebas
- **Unitarias:** pruebas de funciones utilitarias/backend base (ejemplo: config y health logic).
- **Integración:** levantar contenedor y verificar:
  - `/` devuelve HTML de prueba.
  - endpoint de salud responde `200`.
  - scripts de arranque/parada funcionan en cada OS objetivo.

### Criterios de éxito
- [x] El sistema arranca en Docker sin pasos manuales ocultos.
- [x] `/` y API básica responden correctamente.
- [x] Scripts documentados y operativos en los tres sistemas.

### Riesgos y mitigación
- Riesgo: diferencias entre entornos de OS.
  - Mitigación: scripts específicos por plataforma y prueba de humo en cada uno.

---

## Parte 3: Integración del frontend estático

### Objetivo
Compilar y servir el frontend desde el backend para mostrar el tablero demo en `/`.

### Dependencias
- Parte 2 completada.

### Entregables
- Pipeline de build del frontend integrado en la imagen/flujo local.
- Backend sirviendo estáticos del frontend en `/`.
- Tests de integración de assets estáticos y fallback SPA.

### Decisiones tomadas
- Next.js con `output: "export"` (sin SSR en producción Docker).
- Rutas de assets en `/_next/*`; fallback a `index.html` para rutas SPA no encontradas.
- E2E Docker separado de E2E dev (`playwright.docker.config.ts` vs `playwright.config.ts`).

### Lista de verificación
- [x] Configurar build de frontend para despliegue estático.
- [x] Copiar/servir assets estáticos desde backend.
- [x] Verificar que `/` renderiza el tablero Kanban demo.
- [x] Ajustar rutas estáticas y fallback si es necesario.

### Pruebas
- **Unitarias:** tests de utilidades/frontend existentes y nuevos ajustes de build.
- **Integración:** contenedor levantado, navegación a `/`, carga correcta del board.

### Criterios de éxito
- [x] El tablero demo aparece en `/` servido por backend.
- [x] No hay errores de assets ni de rutas en ejecución local.

### Riesgos y mitigación
- Riesgo: rutas/paths de assets rotos en build estático.
  - Mitigación: validar carga de estáticos en contenedor con pruebas de integración.

---

## Parte 4: Login simulado

### Objetivo
Requerir autenticación inicial para ver el tablero y permitir cierre de sesión.

### Dependencias
- Parte 3 completada.

### Entregables
- Pantalla/flujo de login en `/` o ruta definida.
- Control de sesión local del MVP (`frontend/src/lib/auth.ts`).
- Flujo de logout.

### Decisiones tomadas
- Sesión en `localStorage` (no cookies ni token); claves `pm-mvp-auth` y `pm-mvp-username`.
- Validación de credenciales solo en cliente en esta fase; el backend confía en `X-MVP-Username` (Parte 6).

### Lista de verificación
- [x] Definir guard de acceso al tablero.
- [x] Implementar login con `user/password`.
- [x] Implementar cierre de sesión.
- [x] Mostrar mensajes de error para credenciales inválidas.
- [x] Mantener UX simple y consistente con la UI actual.

### Pruebas
- **Unitarias:** validación de credenciales, estado de sesión y guards.
- **Integración:** flujo completo:
  - usuario no autenticado no ve el board;
  - login válido muestra board;
  - logout devuelve a pantalla de login.
- **Cobertura:** no perseguir un porcentaje fijo. Añadir pruebas útiles sobre credenciales, sesión y guard; ~80% solo si se alcanza sin tests triviales.

### Criterios de éxito
- [x] El acceso al board queda protegido por login.
- [x] Solo `user/password` desbloquea sesión en MVP.
- [x] Logout invalida sesión en cliente.

### Riesgos y mitigación
- Riesgo: fuga de acceso sin autenticación en rutas UI.
  - Mitigación: guard centralizado y prueba de integración de acceso no autenticado.

---

## Parte 5: Modelado de base de datos

### Objetivo
Definir esquema de persistencia para Kanban con proyección multiusuario.

### Dependencias
- Parte 4 completada.

### Entregables
- `docs/db-schema.json` con esquema propuesto.
- Documento en `docs/` con explicación del modelo y decisiones (`docs/db-design.md`).
- Capa de inicialización SQLite en `backend/app/db/` (schema loader, `init_database()`).

### Decisiones tomadas
- SQLite ahora; Supabase después (modelo portable, conexión abstracta en Parte 6).
- Tabla `chat_messages` incluida desde el diseño para Partes 9-10.
- Esquema JSON como fuente única para generar DDL en runtime (no migraciones separadas en MVP).
- Aprobación explícita del usuario obtenida antes de Parte 6.

### Lista de verificación
- [x] Definir entidades: usuarios, tableros, columnas, tarjetas.
- [x] Definir relaciones y claves.
- [x] Definir campos mínimos para historial/conversación IA.
- [x] Guardar propuesta en JSON.
- [x] Documentar razonamiento y trade-offs en `docs/`.
- [x] Solicitar aprobación del usuario.

### Pruebas
- **Unitarias:** validación del esquema JSON (estructura y campos requeridos).
- **Integración:** creación inicial de SQLite desde esquema/migración base.

### Criterios de éxito
- [x] Esquema JSON claro, consistente y extensible.
- [x] Documento de diseño aprobado por el usuario.
- [x] BD puede inicializarse si no existe.

### Riesgos y mitigación
- Riesgo: esquema insuficiente para evolución multiusuario.
  - Mitigación: separar entidades por usuario/board y documentar decisiones.

---

## Parte 6: Backend Kanban

### Objetivo
Exponer API para leer y modificar el tablero Kanban por usuario.

### Dependencias
- Parte 5 completada y aprobada.

### Entregables
- Endpoints backend para tablero, columnas y tarjetas.
- Capa de acceso a datos SQLite (`backend/app/kanban/`).
- Creación automática de BD al arrancar si no existe.
- Seed demo idempotente al arrancar.
- Contrato API documentado en `docs/api-kanban.md`.

### Decisiones tomadas
- Autenticación por header `X-MVP-Username` (sin sesión server-side).
- Respuestas y payloads alineados con `BoardData` del frontend (`cardIds` en columnas).
- Errores HTTP: `401` (sin header), `404` (recurso), `400` (negocio), `422` (validación).
- Tests de integración con BD temporal vía `PM_DATABASE_PATH` en fixtures pytest.

### Lista de verificación
- [x] Implementar modelo y repositorio de persistencia.
- [x] Implementar rutas GET/PUT/POST/PATCH/DELETE necesarias.
- [x] Implementar validación de payloads.
- [x] Manejar errores de forma consistente.
- [x] Documentar contrato API mínimo.

### Pruebas
- **Unitarias:** servicios de negocio, validaciones, repositorios.
- **Integración:** llamadas reales a API con DB temporal y verificación de persistencia.

### Criterios de éxito
- [x] API permite operaciones Kanban por usuario.
- [x] Persistencia funciona tras reinicio.
- [x] BD se crea automáticamente cuando no existe.

### Riesgos y mitigación
- Riesgo: incoherencias entre modelo de datos y contratos API.
  - Mitigación: validación estricta de payloads y pruebas integradas con DB temporal.

---

## Parte 7: Frontend + Backend persistente

### Objetivo
Conectar el frontend a la API para que el tablero deje de ser solo en memoria.

### Dependencias
- Parte 6 completada.

### Entregables
- Cliente frontend para consumir API Kanban (`frontend/src/lib/kanban-api.ts`).
- Estado UI sincronizado con backend (`KanbanBoard.tsx` con carga, sync y errores).
- Operaciones de tablero persistidas (rename, create, delete, move).
- E2E Docker con verificación de persistencia tras recarga (`persists a card after reload`).

### Decisiones tomadas
- Sesión cliente (`localStorage`) + header API: el username autenticado se usa en todas las peticiones.
- Estrategia mixta de sync: optimista en drag/delete; persistencia explícita en create y rename debounced.
- Mock de API solo en tests unitarios Vitest; E2E Docker usa API real en contenedor.
- Reset del tablero demo en E2E Docker para evitar estado sucio del volumen SQLite persistente.

### Lista de verificación
- [x] Sustituir mock inicial por carga desde API.
- [x] Persistir renombrado de columnas.
- [x] Persistir alta/borrado/movimiento de tarjetas.
- [x] Gestionar estados de carga/error.

### Pruebas
- **Unitarias:** cliente API, transformaciones de datos, reducers/estado local.
- **Integración:** operación completa UI -> API -> DB -> recarga UI.
- **E2E Docker:** `npm run test:e2e:docker` (6 escenarios, incl. persistencia tras reload).

### Criterios de éxito
- [x] Cambios Kanban sobreviven recarga de página.
- [x] UI refleja correctamente estado persistido.
- [x] Manejo básico de errores sin romper UX.

### Riesgos y mitigación
- Riesgo: regresión funcional al sustituir estado local por API.
  - Mitigación: migración incremental y cobertura de pruebas de interacción clave.

---

## Parte 8: Conectividad con IA (OpenRouter)

### Objetivo
Verificar comunicación backend con OpenRouter.

### Dependencias
- Parte 7 completada.

### Entregables
- Cliente/servicio IA en backend.
- Endpoint de prueba de conectividad IA.

### Lista de verificación
- [x] Leer `OPENROUTER_API_KEY` desde `.env`.
- [x] Configurar llamada con modelo `openai/gpt-oss-120b:free` (override opcional vía `OPENROUTER_MODEL`).
- [x] Implementar prueba funcional simple ("2+2").
- [x] Manejar errores y timeouts básicos.

### Pruebas
- **Unitarias:** construcción de requests y parse de respuesta.
- **Integración:** llamada real a OpenRouter en entorno local configurado.

### Criterios de éxito
- [x] El backend obtiene respuesta válida de IA.
- [x] Fallos de red/API quedan reportados con errores claros.

### Riesgos y mitigación
- Riesgo: latencia/fallos externos de OpenRouter.
  - Mitigación: manejo de timeouts, errores y mensajes claros para diagnóstico.

---

## Parte 9: IA con salidas estructuradas

### Objetivo
Enviar contexto completo de Kanban + conversación y recibir respuesta estructurada con actualización opcional.

### Dependencias
- Parte 8 completada.

### Entregables
- Contrato de salida estructurada IA.
- Lógica backend para aplicar actualización opcional de Kanban.
- Persistencia de historial de conversación según alcance MVP.

### Lista de verificación
- [x] Definir schema de respuesta IA (mensaje + cambios opcionales).
- [x] Enviar a IA: board JSON + prompt usuario + historial.
- [x] Validar respuesta estructurada.
- [x] Aplicar cambios al tablero cuando existan.
- [x] Devolver al frontend respuesta y estado actualizado.

### Pruebas
- **Unitarias:** validación/parsing de salida estructurada y aplicación de cambios.
- **Integración:** flujo chat completo con casos:
  - solo respuesta textual;
  - respuesta con cambios de Kanban válidos.

### Criterios de éxito
- [x] El backend procesa respuestas estructuradas de forma fiable.
- [x] Los cambios IA válidos se reflejan y persisten en tablero.
- [x] Respuestas inválidas no rompen la aplicación.

### Riesgos y mitigación
- Riesgo: respuesta IA malformada o inconsistente.
  - Mitigación: parser con validación estricta y ruta segura cuando falle el formato.

---

## Parte 10: Widget lateral de chat IA

### Objetivo
Incorporar chat lateral completo en la UI con actualización automática del Kanban.

### Dependencias
- Parte 9 completada.

### Entregables
- Componente de sidebar de chat en frontend.
- Integración frontend con endpoint de chat backend.
- Actualización reactiva del tablero tras respuesta IA.

### Lista de verificación
- [x] Diseñar e implementar widget lateral con historial.
- [x] Añadir input, envío y estados de carga/error.
- [x] Consumir endpoint backend de chat.
- [x] Aplicar en UI los cambios Kanban devueltos por IA.
- [x] Mantener coherencia visual con paleta del proyecto.

### Pruebas
- **Unitarias:** componentes de chat, manejo de estado y adaptadores de respuesta.
- **Integración:** flujo end-to-end:
  - usuario envía mensaje;
  - backend consulta IA;
  - frontend muestra respuesta;
  - si hay cambios Kanban, board se actualiza automáticamente.

### Criterios de éxito
- [x] Chat lateral usable y estable.
- [x] Respuesta IA visible en tiempo razonable.
- [x] Actualizaciones Kanban vía IA aplicadas sin recargar manualmente.

### Riesgos y mitigación
- Riesgo: desincronización entre chat, board y estado persistido.
  - Mitigación: aplicar updates desde una única fuente de verdad y refresco de estado post-respuesta.

---

## Cierre del MVP

El MVP se considera completado cuando Partes 2-10 están cerradas con:
- checklist de cada parte completo,
- pruebas unitarias e integración en verde,
- comportamiento funcional validado en entorno local Docker.
