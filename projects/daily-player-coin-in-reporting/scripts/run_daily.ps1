# Configure Task Scheduler's working directory via this script.
# A fresh, complete input extract must exist before each scheduled run.
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
docker compose run --rm report --input data/demo_sessions.csv
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
