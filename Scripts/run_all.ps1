
# scripts\run_all.ps1
param(
  [switch]$NoEnvFile  # si lo usas, omite --env-file y se usará vault_or_env_path()
)

$ErrorActionPreference = "Stop"
Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)

function Start-ServiceLocal {
  param(
    [string]$SvcDir,
    [int]$Port
  )
  $APPDIR = "services/$SvcDir"
  $EnvFile = "services/$SvcDir/.env"
  $PY = "$PWD\libs\shared;$PWD\$APPDIR"
  $cmd = "uvicorn app.main:app --host 0.0.0.0 --port $Port --reload --app-dir $APPDIR"
  if (-not $NoEnvFile -and (Test-Path $EnvFile)) { $cmd += " --env-file $EnvFile" }
  Write-Host ">>> $SvcDir on :$Port"
  Start-Process -NoNewWindow -PassThru powershell -ArgumentList "-NoProfile","-Command","`$env:PYTHONPATH='$PY'; $cmd"
}

Pop-Location

Start-ServiceLocal -SvcDir "iam-service" -Port 8010 | Out-Null
Start-ServiceLocal -SvcDir "catalogo-service" -Port 8020 | Out-Null
Start-ServiceLocal -SvcDir "proveedores-service" -Port 8030 | Out-Null
Start-ServiceLocal -SvcDir "contratacion-service" -Port 8040 | Out-Null
Write-Host "All services launched."
