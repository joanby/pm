# Pasos generales del proyecto

Parte 1: Planificación

Enriquezca este documento para planificar cada una de estas partes en detalle, con subpasos enumerados en una lista de verificación que el agente deberá marcar, e incluyendo pruebas y criterios de éxito para cada uno. Cree también un archivo AGENTS.md dentro del directorio frontend que describa el código existente. Asegúrese de que el usuario revise y apruebe el plan.

Parte 2: Estructura

Configure la infraestructura de Docker, el backend en backend/ con FastAPI y escriba los scripts de inicio y parada en el directorio scripts/. Esto debería servir un ejemplo de HTML estático para confirmar que un ejemplo de "hola mundo" funciona correctamente en local y también realizar una llamada a la API.

Parte 3: Integración del frontend

Actualice el código para que el frontend se compile y sirva de forma estática, de modo que la aplicación muestre el tablero Kanban de demostración en /. Realice pruebas unitarias y de integración exhaustivas.

Parte 4: Añadir una experiencia de inicio de sesión simulada

Actualiza la aplicación para que, al acceder a / por primera vez, se requiera iniciar sesión con credenciales ficticias ("usuario", "contraseña") para ver el tablero Kanban y poder cerrar sesión. Realiza pruebas exhaustivas.

Parte 5: Modelado de la base de datos

Propón un esquema de base de datos para el tablero Kanban y guárdalo en formato JSON. Documenta el enfoque de la base de datos en la carpeta docs/ y obtén la aprobación del usuario.

Parte 6: Backend

Añade rutas API para que el backend pueda leer y modificar el tablero Kanban de un usuario determinado; realiza pruebas exhaustivas con pruebas unitarias del backend. Si la base de datos no existe, se debe crear.

Parte 7: Frontend + Backend

Haz que el frontend utilice la API del backend para que la aplicación funcione como un tablero Kanban persistente. Realiza pruebas exhaustivas.

Parte 8: Conectividad con IA

Permite que el backend realice una llamada a la IA mediante OpenRouter. Prueba la conectividad con una prueba simple de "2+2" y asegúrate de que la llamada a la IA funcione correctamente.

Parte 9: Ahora, amplía la llamada al backend para que siempre llame a la IA con el JSON del tablero Kanban, además de la pregunta del usuario (y el historial de la conversación). La IA debe responder con Salidas Estructuradas que incluyan la respuesta al usuario y, opcionalmente, una actualización del Kanban. Realiza pruebas exhaustivas.

Parte 10: Ahora, añade un atractivo widget lateral a la interfaz de usuario que admita el chat completo con la IA y permita que el LLM (según lo determine) actualice el Kanban en función de sus Salidas Estructuradas. Si la IA actualiza el Kanban, la interfaz de usuario se actualizará automáticamente.
