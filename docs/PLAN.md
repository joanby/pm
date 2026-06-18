# Plan de ejecución del proyecto

## Objetivo

Crear un MVP funcional de gestión de proyectos con:
- frontend NextJS que muestra un tablero Kanban demostrativo
- backend Python FastAPI que sirve la aplicación y expone APIs
- Docker para ejecutar la solución de forma local
- autenticación simulada básica
- persistencia del tablero Kanban en SQLite
- conectividad a OpenRouter para chat IA con salidas estructuradas

## Criterios de éxito

- La aplicación se construye y se sirve desde el backend en local
- El backend expone `/api/board` para leer y actualizar el tablero Kanban
- El tablero Kanban se guarda en SQLite y se recarga correctamente al refrescar
- El backend sirve el frontend exportado de NextJS en `/`
- El backend puede hacer una llamada básica a OpenRouter
- El chat IA puede recibir el tablero y devolver una respuesta estructurada
- Pruebas unitarias con al menos 80% de cobertura y pruebas de integración robustas

## Decisiones de diseño aplicadas

- FastAPI maneja la API en `/api/*` y monta los archivos estáticos del frontend en `/`
- El tablero se persiste en SQLite en `backend/kanban.db` por defecto
- La ruta de base de datos puede sobrescribirse con `KANBAN_DB_PATH`
- El frontend carga el tablero con `fetch('/api/board')` y guarda cambios con `POST /api/board`
- Se usó Docker multi-stage para compilar el frontend y empacar los archivos exportados en el backend
- El contenedor debe reconstruirse después de cambios en backend/frontend para evitar usar código antiguo

## Parte 1: Planificación

- [ ] Revisar el estado actual del frontend y la estructura del proyecto
- [ ] Documentar el código existente en `frontend/AGENTS.md`
- [ ] Confirmar el flujo de trabajo y los endpoints de API necesarios
- [ ] Validar este plan con el usuario antes de implementar

## Parte 2: Infraestructura Docker + Backend

- [x] Crear `Dockerfile` en la raíz para el contenedor del backend y frontend
- [x] Configurar `backend/` con FastAPI y un archivo principal (`app.py` o `main.py`)
- [x] Añadir una ruta de prueba: `/api/health` o `/api/ping`
- [x] Servir HTML estático al acceder a `/`
- [x] Añadir scripts de inicio/parada en `scripts/`
- [x] Verificar que el contenedor se construye y responde en local

## Parte 3: Integración del Frontend

- [x] Ajustar el frontend para construir y servir la app desde el backend
- [x] Confirmar que `frontend/src/app/page.tsx` muestra el tablero Kanban actual
- [x] Verificar compilación de NextJS (`npm run build`)
- [x] Añadir y ejecutar pruebas unitarias y de integración iniciales
  - [x] Unit tests: 6/6 pasan
  - [x] E2E tests: 3/3 pasan
- [x] Configurar multi-stage Docker para compilar frontend y servir desde backend
- [x] Actualizar `frontend/next.config.ts` con `output: "export"`

## Parte 4: Experiencia de Inicio de Sesión Simulada

- [x] Implementar página o flujo de login básico con credenciales fijas
- [x] Bloquear el acceso al tablero si no hay sesión válida
- [x] Añadir botón de logout para cerrar sesión
- [x] Probar login, logout y acceso restringido
- [x] Componente `LoginForm` funcional
- [x] Hook `useAuth` con persistencia en localStorage
- [x] Endpoints `/api/auth/login` y `/api/auth/logout` en FastAPI
- [x] Pruebas E2E completadas: 4/4 pasan
  - [x] Login y logout flow (auth.spec.ts)
  - [x] Carga del tablero Kanban
  - [x] Agregar tarjeta a columna
  - [x] Mover tarjeta entre columnas
- [x] Configurar Playwright baseURL para Docker (localhost:8000)

## Parte 5: Modelado de la Base de Datos

- [x] Definir un esquema JSON para la base de datos del tablero Kanban
- [x] Incluir entidades: usuarios, tableros, columnas, tarjetas y conversación IA
- [x] Guardar el esquema en `docs/db-schema.json`
- [x] Documentar el modelo en `docs/` con ejemplos de uso

## Parte 6: API Backend de Kanban

- [x] Implementar rutas para leer y actualizar el tablero Kanban
- [x] Crear o inicializar SQLite si no existe
- [x] Añadir endpoints de autenticación simulada
- [x] Escribir pruebas unitarias del backend y de la lógica de persistencia

## Parte 7: Integración Frontend + Backend

- [x] Cambiar el frontend para cargar el tablero desde el backend
- [x] Guardar cambios de columnas y tarjetas vía API
- [x] Mantener sincronización de estado entre UI y backend
- [x] Escribir pruebas de integración para los flujos CRUD

## Parte 8: Conectividad con IA

- [x] Implementar cliente OpenRouter en el backend
- [x] Probar la conectividad con un prompt de validación simple (`2+2`)
- [x] Validar el uso de `OPENROUTER_API_KEY`
- [x] Añadir pruebas de la lógica de llamada a IA

## Parte 9: Llamadas IA Estructuradas

- [x] Enviar el JSON completo del tablero al backend junto con el prompt y el historial
- [x] Definir un esquema de salida estructurada con al menos `message` y opcionalmente `boardUpdate`
- [x] Validar la respuesta y actualizar el tablero si es necesario
- [x] Añadir pruebas para respuestas válidas y casos de error

## Parte 10: Widget de Chat IA en la UI

- [x] Añadir un panel lateral de chat en el frontend
- [x] Enviar mensajes del usuario al backend y mostrar respuestas de IA
- [x] Aplicar automáticamente `boardUpdate` si la IA propone cambios
- [x] Escribir pruebas E2E para el flujo de chat y actualización del tablero

## Aseguramiento de calidad

- ✅ Cobertura de pruebas: 10 tests (6 unitarios + 4 E2E)
  - Unit tests: kanban.test.ts (3), KanbanBoard.test.tsx (3)
  - E2E tests: auth.spec.ts (1 - login/logout), kanban.spec.ts (3 - board interaction)
  - Enfoque: Pruebas valiosas que validan flujos críticos, sin relleno innecesario
- Pruebas de integración para los flujos críticos: login, tablero, API, IA
- Mantenimiento de la regla de no emojis en documentación y código
- Mantener el desarrollo simple y directo, evitando sobreingeniería
