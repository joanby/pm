# Aplicación de Gestión de Proyectos MVP

## Requisitos de Negocio

Este proyecto está construyendo una Aplicación de Gestión de Proyectos. Características principales:
- Un usuario puede iniciar sesión
- Cuando inicia sesión, el usuario ve un tablero Kanban que representa su proyecto
- El tablero Kanban tiene columnas fijas que se pueden renombrar
- Las tarjetas del tablero Kanban se pueden mover con arrastrar y soltar, y editar
- Hay una característica de chat con IA en la barra lateral; la IA puede crear / editar / mover una o más tarjetas

## Limitaciones

Para el MVP, solo habrá un inicio de sesión de usuario (codificado como 'user' y 'password'), pero la base de datos admitirá múltiples usuarios en el futuro.

Para el MVP, solo habrá 1 tablero Kanban por usuario que inicie sesión.

Para el MVP, esto se ejecutará localmente (en un contenedor docker)

## Decisiones Técnicas

- Frontend NextJS
- Backend Python FastAPI, incluyendo servir el sitio estático NextJS en /
- Todo empaquetado en un contenedor Docker
- Usar "uv" como gestor de paquetes para python en el contenedor Docker
- Usar OpenRouter para las llamadas de IA. Una OPENROUTER_API_KEY está en .env en la raíz del proyecto
- Usar `openai/gpt-oss-120b:free` como modelo
- Usar base de datos SQLLite local, creando una nueva bd si no existe
- Scripts de inicio y parada del servidor para Mac, PC, Linux en scripts/

## Punto de Partida

Un MVP funcional del frontend ya ha sido construido y está en frontend. Esto aún no está diseñado para la configuración de Docker. Es una demostración puramente frontend.

## Esquema de Color

- Amarillo Acentuado: `#ecad0a` - líneas acentuadas, destacados
- Azul Primario: `#209dd7` - enlaces, secciones clave
- Púrpura Secundario: `#753991` - botones de envío, acciones importantes
- Azul Marino Oscuro: `#032147` - títulos principales
- Texto Gris: `#888888` - texto de apoyo, etiquetas

## Estándares de Codificación

1. Usar las últimas versiones de librerías y enfoques idiomáticos a partir de hoy
2. Mantenerlo simple - NUNCA sobre-ingenierizar, SIEMPRE simplificar, NO hay programación defensiva innecesaria. Sin características extra - enfócate en la simplicidad.
3. Ser conciso. Mantener README mínimo. IMPORTANTE: nunca emojis
4. Cuando encuentres problemas, siempre identifica la causa raíz antes de intentar una solución. No adivines. Prueba con evidencia, luego corrige la causa raíz.

## Documentación de Trabajo

Todos los documentos para planificación y ejecución de este proyecto estarán en el directorio docs/.
Por favor revisa el documento docs/PLAN.md antes de continuar.