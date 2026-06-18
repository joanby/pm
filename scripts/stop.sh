#!/usr/bin/env bash
set -euo pipefail

echo "Deteniendo contenedor pm-mvp..."
docker stop pm-mvp 2>/dev/null || true
docker rm pm-mvp 2>/dev/null || true

echo "Contenedor detenido y eliminado."