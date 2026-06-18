# Ejemplo del esquema de datos Kanban

Este documento describe cómo se estructura el almacenamiento local del tablero y las conversaciones de IA.

## Estructura principal

- `users`: usuarios que pueden iniciar sesión
- `boards`: tableros con columnas y tarjetas
- `conversations`: historial de mensajes de IA relacionados con un tablero

## Ejemplo JSON

```json
{
  "users": [
    {
      "id": "user-1",
      "username": "usuario",
      "passwordHash": "hashed-password-simulado",
      "displayName": "Usuario MVP",
      "createdAt": "2026-06-18T12:00:00Z"
    }
  ],
  "boards": [
    {
      "id": "board-1",
      "userId": "user-1",
      "title": "Tablero principal",
      "columns": [
        {
          "id": "column-1",
          "title": "Pendientes",
          "position": 0,
          "cards": [
            {
              "id": "card-1",
              "title": "Diseñar MVP",
              "details": "Definir las funcionalidades mínimas para el primer release.",
              "status": "pending",
              "createdAt": "2026-06-18T12:30:00Z",
              "updatedAt": "2026-06-18T12:30:00Z"
            }
          ]
        },
        {
          "id": "column-2",
          "title": "En progreso",
          "position": 1,
          "cards": []
        },
        {
          "id": "column-3",
          "title": "Hecho",
          "position": 2,
          "cards": []
        }
      ]
    }
  ],
  "conversations": [
    {
      "id": "conv-1",
      "userId": "user-1",
      "boardId": "board-1",
      "messages": [
        {
          "role": "user",
          "text": "Organiza las tarjetas según prioridad.",
          "createdAt": "2026-06-18T12:45:00Z"
        },
        {
          "role": "assistant",
          "text": "He movido la tarjeta de diseño a En progreso.",
          "createdAt": "2026-06-18T12:46:00Z"
        }
      ],
      "lastUpdatedAt": "2026-06-18T12:46:00Z"
    }
  ]
}
```

## Notas

- El campo `passwordHash` puede ser simulado mientras el proyecto use autenticación básica.
- `boards` mantiene el estado completo de columnas y tarjetas, lo que permite restaurar la UI desde el backend.
- `conversations` captura el historial de chat IA y se puede utilizar para contexto de nuevos prompts.
