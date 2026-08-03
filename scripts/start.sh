#!/usr/bin/env bash
set -euo pipefail

docker compose up --build -d
echo "PM MVP started at http://localhost:8000"
