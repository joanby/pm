# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend ./
RUN npm run build

# Stage 2: Backend with static frontend
FROM python:3.12-slim
WORKDIR /app
RUN python -m pip install --no-cache-dir uv
COPY backend/pyproject.toml /app/backend/pyproject.toml
RUN uv pip install --system --no-cache /app/backend

COPY backend /app/backend
COPY --from=frontend-builder /frontend/out /app/backend/static/frontend

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
