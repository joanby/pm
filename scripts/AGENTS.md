# Scripts de arranque/parada

## Propósito

Este directorio contiene scripts para iniciar y detener el entorno Docker del MVP en diferentes sistemas operativos.

## Scripts disponibles

- Linux/macOS:
  - `start.sh`
  - `stop.sh`
- Windows PowerShell:
  - `start.ps1`
  - `stop.ps1`
- Windows CMD:
  - `start.bat`
  - `stop.bat`

## Comportamiento

- Los scripts de inicio ejecutan `docker compose up --build -d`.
- Los scripts de parada ejecutan `docker compose down`.

## Notas Windows

- Si PowerShell bloquea `.ps1` por la política de ejecución, usar `start.bat` / `stop.bat`.
- Comandos documentados en el [README](../README.md) de la raíz.