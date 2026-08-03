# Plan general del proyecto MVP

## Reglas globales de ejecución

- Credenciales oficiales del MVP: `user/password`.
- No cerrar ninguna parte funcional sin pruebas unitarias e integración.
- Cobertura objetivo orientativa: hasta ~80% cuando sea sensato; priorizar pruebas valiosas sobre perseguir un porcentaje.
- No es obligatorio alcanzar 80% si el coste obliga a añadir pruebas de bajo valor.
- Priorizar simplicidad y evitar sobreingeniería.
- Validar siempre por evidencia observable (logs, respuestas API, comportamiento UI).

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
- Endpoint HTML estático "hola mundo" y endpoint API de verificación.

### Lista de verificación
- [ ] Crear Dockerfile y configuración de ejecución local.
- [ ] Inicializar backend FastAPI mínimo.
- [ ] Implementar endpoint `/api/health` (o equivalente).
- [ ] Servir página estática de prueba en `/`.
- [ ] Crear scripts `start` y `stop` por plataforma.
- [ ] Documentar comandos básicos en `README`/`docs` si aplica.

### Pruebas
- **Unitarias:** pruebas de funciones utilitarias/backend base (ejemplo: config y health logic).
- **Integración:** levantar contenedor y verificar:
  - `/` devuelve HTML de prueba.
  - endpoint de salud responde `200`.
  - scripts de arranque/parada funcionan en cada OS objetivo.

### Criterios de éxito
- [ ] El sistema arranca en Docker sin pasos manuales ocultos.
- [ ] `/` y API básica responden correctamente.
- [ ] Scripts documentados y operativos en los tres sistemas.

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

### Lista de verificación
- [ ] Configurar build de frontend para despliegue estático.
- [ ] Copiar/servir assets estáticos desde backend.
- [ ] Verificar que `/` renderiza el tablero Kanban demo.
- [ ] Ajustar rutas estáticas y fallback si es necesario.

### Pruebas
- **Unitarias:** tests de utilidades/frontend existentes y nuevos ajustes de build.
- **Integración:** contenedor levantado, navegación a `/`, carga correcta del board.

### Criterios de éxito
- [ ] El tablero demo aparece en `/` servido por backend.
- [ ] No hay errores de assets ni de rutas en ejecución local.

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
- Control de sesión local del MVP.
- Flujo de logout.

### Lista de verificación
- [ ] Definir guard de acceso al tablero.
- [ ] Implementar login con `user/password`.
- [ ] Implementar cierre de sesión.
- [ ] Mostrar mensajes de error para credenciales inválidas.
- [ ] Mantener UX simple y consistente con la UI actual.

### Pruebas
- **Unitarias:** validación de credenciales, estado de sesión y guards.
- **Integración:** flujo completo:
  - usuario no autenticado no ve el board;
  - login válido muestra board;
  - logout devuelve a pantalla de login.
- **Cobertura:** objetivo aproximado de 80% en el módulo de login solo si se logra con pruebas útiles.

### Criterios de éxito
- [ ] El acceso al board queda protegido por login.
- [ ] Solo `user/password` desbloquea sesión en MVP.
- [ ] Logout invalida sesión en cliente.

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
- Documento en `docs/` con explicación del modelo y decisiones.

### Lista de verificación
- [ ] Definir entidades: usuarios, tableros, columnas, tarjetas.
- [ ] Definir relaciones y claves.
- [ ] Definir campos mínimos para historial/conversación IA.
- [ ] Guardar propuesta en JSON.
- [ ] Documentar razonamiento y trade-offs en `docs/`.
- [ ] Solicitar aprobación del usuario.

### Pruebas
- **Unitarias:** validación del esquema JSON (estructura y campos requeridos).
- **Integración:** creación inicial de SQLite desde esquema/migración base.

### Criterios de éxito
- [ ] Esquema JSON claro, consistente y extensible.
- [ ] Documento de diseño aprobado por el usuario.
- [ ] BD puede inicializarse si no existe.

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
- Capa de acceso a datos SQLite.
- Creación automática de BD al arrancar si no existe.

### Lista de verificación
- [ ] Implementar modelo y repositorio de persistencia.
- [ ] Implementar rutas GET/PUT/POST/PATCH/DELETE necesarias.
- [ ] Implementar validación de payloads.
- [ ] Manejar errores de forma consistente.
- [ ] Documentar contrato API mínimo.

### Pruebas
- **Unitarias:** servicios de negocio, validaciones, repositorios.
- **Integración:** llamadas reales a API con DB temporal y verificación de persistencia.

### Criterios de éxito
- [ ] API permite operaciones Kanban por usuario.
- [ ] Persistencia funciona tras reinicio.
- [ ] BD se crea automáticamente cuando no existe.

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
- Cliente frontend para consumir API Kanban.
- Estado UI sincronizado con backend.
- Operaciones de tablero persistidas.

### Lista de verificación
- [ ] Sustituir mock inicial por carga desde API.
- [ ] Persistir renombrado de columnas.
- [ ] Persistir alta/borrado/movimiento de tarjetas.
- [ ] Gestionar estados de carga/error.

### Pruebas
- **Unitarias:** cliente API, transformaciones de datos, reducers/estado local.
- **Integración:** operación completa UI -> API -> DB -> recarga UI.

### Criterios de éxito
- [ ] Cambios Kanban sobreviven recarga de página.
- [ ] UI refleja correctamente estado persistido.
- [ ] Manejo básico de errores sin romper UX.

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
- [ ] Leer `OPENROUTER_API_KEY` desde `.env`.
- [ ] Configurar llamada con modelo `openai/gpt-oss-120b:free`.
- [ ] Implementar prueba funcional simple ("2+2").
- [ ] Manejar errores y timeouts básicos.

### Pruebas
- **Unitarias:** construcción de requests y parse de respuesta.
- **Integración:** llamada real a OpenRouter en entorno local configurado.

### Criterios de éxito
- [ ] El backend obtiene respuesta válida de IA.
- [ ] Fallos de red/API quedan reportados con errores claros.

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
- [ ] Definir schema de respuesta IA (mensaje + cambios opcionales).
- [ ] Enviar a IA: board JSON + prompt usuario + historial.
- [ ] Validar respuesta estructurada.
- [ ] Aplicar cambios al tablero cuando existan.
- [ ] Devolver al frontend respuesta y estado actualizado.

### Pruebas
- **Unitarias:** validación/parsing de salida estructurada y aplicación de cambios.
- **Integración:** flujo chat completo con casos:
  - solo respuesta textual;
  - respuesta con cambios de Kanban válidos.

### Criterios de éxito
- [ ] El backend procesa respuestas estructuradas de forma fiable.
- [ ] Los cambios IA válidos se reflejan y persisten en tablero.
- [ ] Respuestas inválidas no rompen la aplicación.

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
- [ ] Diseñar e implementar widget lateral con historial.
- [ ] Añadir input, envío y estados de carga/error.
- [ ] Consumir endpoint backend de chat.
- [ ] Aplicar en UI los cambios Kanban devueltos por IA.
- [ ] Mantener coherencia visual con paleta del proyecto.

### Pruebas
- **Unitarias:** componentes de chat, manejo de estado y adaptadores de respuesta.
- **Integración:** flujo end-to-end:
  - usuario envía mensaje;
  - backend consulta IA;
  - frontend muestra respuesta;
  - si hay cambios Kanban, board se actualiza automáticamente.

### Criterios de éxito
- [ ] Chat lateral usable y estable.
- [ ] Respuesta IA visible en tiempo razonable.
- [ ] Actualizaciones Kanban vía IA aplicadas sin recargar manualmente.

### Riesgos y mitigación
- Riesgo: desincronización entre chat, board y estado persistido.
  - Mitigación: aplicar updates desde una única fuente de verdad y refresco de estado post-respuesta.

---

## Cierre del MVP

El MVP se considera completado cuando Partes 2-10 están cerradas con:
- checklist de cada parte completo,
- pruebas unitarias e integración en verde,
- comportamiento funcional validado en entorno local Docker.
