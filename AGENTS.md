# Aplicación de Gestión de Proyectos MVP

## Objetivo del producto

Construir una aplicación de gestión de proyectos con tablero Kanban y chat con IA, ejecutable en local mediante Docker, con una base sólida para evolucionar de MVP a versión multiusuario.

## Funcionalidades objetivo (MVP)

- Inicio de sesión simulado.
- Visualización de un tablero Kanban por usuario.
- Columnas fijas renombrables.
- Tarjetas editables y movibles con arrastrar y soltar.
- Chat lateral con IA capaz de crear, editar o mover tarjetas.

## Reglas de negocio del MVP

- Credenciales oficiales del MVP: `user/password`.
- Solo 1 tablero Kanban por usuario.
- Se ejecuta localmente en contenedor Docker.
- Aunque el login es simulado, el modelo de datos debe prepararse para múltiples usuarios.

## Arquitectura y decisiones técnicas

- Frontend: Next.js.
- Backend: FastAPI (Python), incluyendo servir frontend estático en `/`.
- Contenedorización: Docker para todo el sistema.
- Gestión de paquetes Python en contenedor: `uv`.
- IA: OpenRouter con API key en `.env` (raíz del proyecto).
- Modelo IA objetivo: `openai/gpt-oss-120b:free`.
- Persistencia: SQLite local; crear BD automáticamente si no existe.
- Automatización local: scripts de inicio/parada para Mac, Windows y Linux en `scripts/`.

## Estado actual del proyecto

- Existe un MVP funcional de frontend en `frontend/`.
- Ese frontend es actualmente una demo desacoplada de Docker/backend.
- La integración completa se planifica en las fases definidas en `docs/PLAN.md`.

## Flujo funcional esperado (alto nivel)

1. El usuario abre `/` y se autentica con `user/password`.
2. La app muestra su tablero Kanban.
3. El usuario puede operar el tablero manualmente (editar/mover tarjetas).
4. El usuario chatea con la IA en la barra lateral.
5. El backend envía a la IA el estado del Kanban + prompt + historial.
6. La IA responde texto y, opcionalmente, cambios estructurados de Kanban.
7. Si hay cambios de Kanban, se persisten y se reflejan en UI.

## Fases de trabajo

La ejecución por fases (planificación, estructura, integración frontend/backend, login, base de datos e IA) se define en `docs/PLAN.md`. Cualquier trabajo nuevo debe alinearse con ese plan y su orden lógico de dependencias.

## Criterios de calidad mínimos

- Simplicidad sobre complejidad: sin sobreingeniería ni features extra.
- Cambios pequeños, claros y verificables.
- Pruebas asociadas a cada fase antes de avanzar.
- Diagnóstico por causa raíz antes de corregir defectos.
- Documentación breve y actualizada (sin texto superfluo).

## Esquema de color UI

- Amarillo acento: `#ecad0a`.
- Azul primario: `#209dd7`.
- Púrpura secundario: `#753991`.
- Azul marino oscuro: `#032147`.
- Gris texto auxiliar: `#888888`.

## Convenciones para agentes

- Revisar `docs/PLAN.md` antes de ejecutar cambios.
- Mantener consistencia de credenciales (`user/password`) en código y docs.
- No introducir funcionalidades fuera del alcance de la fase actual.
- Priorizar cambios que mantengan la trazabilidad entre requisito, implementación y prueba.

## Documentación de referencia

- Plan principal: `docs/PLAN.md`.
- Guías específicas por área: `backend/AGENTS.md`, `scripts/AGENTS.md` y futuras guías en subdirectorios.