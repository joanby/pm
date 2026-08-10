# API IA (Partes 8-9)

Base URL local: `http://localhost:8000`

## Autenticación MVP

Todas las rutas IA requieren el header:

```http
X-MVP-Username: user
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/ai/ping` | Prueba de conectividad OpenRouter |
| `POST` | `/api/ai/chat` | Chat con contexto Kanban y salida estructurada |
| `GET` | `/api/ai/history` | Historial de conversación del tablero |

## POST /api/ai/chat

### Request

```json
{
  "message": "Add a card called Sprint planning to Backlog"
}
```

### Response

```json
{
  "message": "I added the card to Backlog.",
  "boardUpdated": true,
  "board": {
    "columns": [
      { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1", "card-new"] }
    ],
    "cards": {
      "card-new": {
        "id": "card-new",
        "title": "Sprint planning",
        "details": "No details yet."
      }
    }
  }
}
```

- `message`: respuesta textual de la IA para el usuario.
- `boardUpdated`: `true` si se aplicaron cambios al tablero.
- `board`: estado completo del tablero tras la operación (actualizado o sin cambios).

## Salida estructurada esperada del modelo

Internamente la IA responde con JSON:

```json
{
  "message": "texto para el usuario",
  "board": null
}
```

Cuando hay cambios Kanban, `board` contiene el estado completo del tablero (`columns` + `cards` con `cardIds`).

## Historial

Los mensajes `user` y `assistant` se persisten en `chat_messages` scoped al tablero del usuario. El backend envía el historial reciente en cada llamada.

## Errores

| Código | Cuándo |
|--------|--------|
| `401` | Falta header `X-MVP-Username` |
| `404` | Usuario o tablero inexistente |
| `422` | Mensaje vacío o inválido |
| `502` | Error de OpenRouter o respuesta inválida irrecuperable |
| `503` | Falta `OPENROUTER_API_KEY` |
| `504` | Timeout de OpenRouter |

## Ejemplo

```bash
curl -X POST http://localhost:8000/api/ai/chat \
  -H "Content-Type: application/json" \
  -H "X-MVP-Username: user" \
  -d "{\"message\":\"How many columns are on my board?\"}"
```
