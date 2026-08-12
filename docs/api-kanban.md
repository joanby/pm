# API Kanban (Parte 6)

Base URL local: `http://localhost:8000`

## Autenticación MVP

Todas las rutas Kanban requieren el header:

```http
X-MVP-Username: user
```

En el MVP el login es simulado en frontend; el backend identifica al usuario por este header. Solo existe el usuario demo `user`.

## Formato del tablero

```json
{
  "columns": [
    { "id": "col-backlog", "title": "Backlog", "cardIds": ["card-1"] }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Example",
      "details": "Details"
    }
  }
}
```

## Endpoints

| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/board` | Obtiene el tablero completo del usuario |
| `PUT` | `/api/board` | Reemplaza el estado completo del tablero |
| `PATCH` | `/api/columns/{column_id}` | Renombra una columna (`{ "title": "..." }`) |
| `POST` | `/api/columns/{column_id}/cards` | Crea una tarjeta (`{ "title", "details?", "id?" }`) |
| `PATCH` | `/api/cards/{card_id}` | Actualiza título y/o detalles |
| `DELETE` | `/api/cards/{card_id}` | Elimina una tarjeta |
| `PUT` | `/api/cards/{card_id}/move` | Mueve tarjeta (`{ "column_id", "position" }`) |

## Errores

| Código | Cuándo |
|--------|--------|
| `401` | Falta header `X-MVP-Username` |
| `404` | Usuario, tablero, columna o tarjeta inexistente |
| `400` | Regla de negocio incumplida |
| `422` | Payload inválido |

## Ejemplo rápido

```bash
curl -H "X-MVP-Username: user" http://localhost:8000/api/board
```

## Persistencia

- SQLite en `backend/data/pm.db` (configurable con `PM_DATABASE_PATH`).
- La BD y el usuario demo se crean al arrancar la aplicación.
