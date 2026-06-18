#!/usr/bin/env bash
set -euo pipefail
cd "$(cd "$(dirname "$0")" && pwd)/.."

echo "Construyendo la imagen Docker..."
docker build -t pm-mvp .

echo "Deteniendo contenedor existente si existe..."
docker stop pm-mvp 2>/dev/null || true
docker rm pm-mvp 2>/dev/null || true

echo "Iniciando contenedor pm-mvp en el puerto 8000..."
if [ -f .env ]; then
  docker run -d --name pm-mvp --env-file .env -p 8000:8000 pm-mvp
else
  docker run -d --name pm-mvp -p 8000:8000 pm-mvp
fi

echo "Contenedor iniciado. Accede a http://localhost:8000"
