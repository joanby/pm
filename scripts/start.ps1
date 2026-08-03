$ErrorActionPreference = "Stop"

docker compose up --build -d
Write-Host "PM MVP started at http://localhost:8000"
