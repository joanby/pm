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
- El acceso a `/` requiere un inicio de sesión simulado con `usuario` / `contraseña`
- El tablero Kanban se guarda y se carga desde el backend
- El backend puede hacer una llamada básica a OpenRouter
- El chat IA puede recibir el tablero y devolver una respuesta estructurada
- Pruebas unitarias con al menos 80% de cobertura y pruebas de integración robustas

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

- [ ] Definir un esquema JSON para la base de datos del tablero Kanban
- [ ] Incluir entidades: usuarios, tableros, columnas, tarjetas y conversación IA
- [ ] Guardar el esquema en `docs/db-schema.json`
- [ ] Documentar el modelo en `docs/` con ejemplos de uso

## Parte 6: API Backend de Kanban

- [ ] Implementar rutas para leer y actualizar el tablero Kanban
- [ ] Crear o inicializar SQLite si no existe
- [ ] Añadir endpoints de autenticación simulada
- [ ] Escribir pruebas unitarias del backend y de la lógica de persistencia

## Parte 7: Integración Frontend + Backend

- [ ] Cambiar el frontend para cargar el tablero desde el backend
- [ ] Guardar cambios de columnas y tarjetas vía API
- [ ] Mantener sincronización de estado entre UI y backend
- [ ] Escribir pruebas de integración para los flujos CRUD

## Parte 8: Conectividad con IA

- [ ] Implementar cliente OpenRouter en el backend
- [ ] Probar la conectividad con un prompt de validación simple (`2+2`)
- [ ] Validar el uso de `OPENROUTER_API_KEY`
- [ ] Añadir pruebas de la lógica de llamada a IA

## Parte 9: Llamadas IA Estructuradas

- [ ] Enviar el JSON completo del tablero al backend junto con el prompt y el historial
- [ ] Definir un esquema de salida estructurada con al menos `message` y opcionalmente `boardUpdate`
- [ ] Validar la respuesta y actualizar el tablero si es necesario
- [ ] Añadir pruebas para respuestas válidas y casos de error

## Parte 10: Widget de Chat IA en la UI

- [ ] Añadir un panel lateral de chat en el frontend
- [ ] Enviar mensajes del usuario al backend y mostrar respuestas de IA
- [ ] Aplicar automáticamente `boardUpdate` si la IA propone cambios
- [ ] Escribir pruebas E2E para el flujo de chat y actualización del tablero

## Aseguramiento de calidad

- ✅ Cobertura de pruebas: 10 tests (6 unitarios + 4 E2E)
  - Unit tests: kanban.test.ts (3), KanbanBoard.test.tsx (3)
  - E2E tests: auth.spec.ts (1 - login/logout), kanban.spec.ts (3 - board interaction)
  - Enfoque: Pruebas valiosas que validan flujos críticos, sin relleno innecesario
- Pruebas de integración para los flujos críticos: login, tablero, API, IA
- Mantenimiento de la regla de no emojis en documentación y código
- Mantener el desarrollo simple y directo, evitando sobreingeniería
