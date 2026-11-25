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

## Parte 11: Multi-usuario y multi-tablero

- [x] Hashear contraseñas con bcrypt (antes se guardaban y comparaban en texto plano); migración automática de usuarios antiguos en `init_db`
- [x] Añadir rol (`admin`/`member`) a los usuarios
- [x] Gestión de usuarios: `/api/users` (crear/listar, solo admin), `/api/users/me` (perfil propio), `/api/users/{id}` (editar/eliminar, solo admin)
  - Un admin no puede eliminarse a sí mismo ni degradar al último admin a `member`
- [x] Sustituir el tablero único (`/api/board`) por tableros múltiples por usuario (`/api/boards`, `/api/boards/{id}`: crear, leer, actualizar, renombrar, eliminar)
  - Cada consulta filtra por `user_id`, así que un usuario no puede ver ni modificar tableros de otro
- [x] El chat IA (`/api/ai/chat`) ahora recibe `board_id` y verifica la propiedad del tablero antes de guardar
- [x] Frontend: `BoardSwitcher` para crear/cambiar/renombrar/eliminar tableros; panel `UserManagementPanel` (solo visible para admins) para gestionar usuarios
- [x] Backend: 41 tests, 97% de cobertura (`uv run pytest tests --cov=backend`)
- [x] Frontend: 12 tests unitarios/integración (Vitest) + 7 tests E2E (Playwright, contra el contenedor Docker real): login/logout, interacción de tablero, multi-tablero, gestión de usuarios, chat IA con OpenRouter real
- [x] Corregido `.dockerignore`: no excluía `backend/kanban.db`/`backend/test-kanban.db`, por lo que la base de datos de desarrollo local se horneaba dentro de la imagen Docker en vez de crearse limpia en cada arranque

## Parte 12: Autorregistro y cambio de contraseña

- [x] `POST /api/auth/register` (público, sin autenticación): crea un usuario con rol `member` e inicia sesión automáticamente, igual que el login
- [x] `POST /api/users/me/password`: cambio de contraseña propio, exige `current_password` correcto antes de aplicar `new_password`
  - `PATCH /api/users/me` ya no acepta `password` (se separó del cambio de contraseña para poder exigir la contraseña actual)
- [x] Frontend: `LoginForm` alterna entre modo "Iniciar sesión" y "Crear cuenta" (campo de nombre visible adicional en registro)
- [x] Eliminada la pista "Prueba con: usuario / contraseña" del login, que revelaba las credenciales del admin semilla
- [x] Nuevo `ChangePasswordPanel` (modal) accesible desde un botón "Cambiar contraseña" junto a "Cerrar sesión"
- [x] Backend: 46 tests, 97% de cobertura
- [x] Frontend: 17 tests Vitest + 9 tests E2E Playwright (incluye registro desde el login y cambio de contraseña con relogin), todos verificados contra el contenedor Docker real

## Parte 13: Rediseño visual (enterprise + edgy)

- [x] Tema oscuro por defecto: fondo casi negro con rejilla sutil, paneles de cristal (`var(--panel)`) con `backdrop-filter: blur`, bordes y sombras con resplandor (`--glow-yellow`, `--glow-blue`, `--glow-purple`) usando la paleta de marca existente
- [x] Tipografía añadida: `JetBrains Mono` (`--font-mono`) para etiquetas técnicas, contadores y prompts, junto a `Space Grotesk` (display) y `Manrope` (cuerpo) ya existentes
- [x] `LoginForm`: tarjeta de cristal sobre fondo con halos de color, marca "Frogames Labs"
- [x] `KanbanBoard`: cabecera de cristal, columnas con franja superior de color cíclico (amarillo/azul/púrpura) en vez de un único punto amarillo
- [x] `KanbanCard`, `NewCardForm`, `AiChatPanel`, `BoardSwitcher`, `UserManagementPanel`, `ChangePasswordPanel`: adaptados al tema oscuro manteniendo los mismos componentes y lógica
- [x] Verificado: 17 tests Vitest + 9 tests E2E Playwright siguen en verde contra el contenedor Docker real; build y lint limpios; revisión visual manual con capturas de pantalla

## Aseguramiento de calidad

- Backend: 46 tests con pytest, 97% de cobertura de líneas
- Frontend: 17 tests con Vitest (unitarios + integración) y 9 tests E2E con Playwright contra el backend real en Docker
  - `ai-chat.spec.ts` puede fallar de forma intermitente por la latencia del modelo gratuito de OpenRouter; no indica una regresión
- Pruebas de integración para los flujos críticos: login, registro, cambio de contraseña, multi-tablero, gestión de usuarios, IA
- Mantenimiento de la regla de no emojis en documentación y código
- Mantener el desarrollo simple y directo, evitando sobreingeniería
