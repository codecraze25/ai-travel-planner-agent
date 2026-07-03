# Start API (8000) + Web (3000) on the host — no Docker required.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$WebDir = Join-Path $Root "apps\web"

Write-Host "Installing API deps (if needed)..." -ForegroundColor Cyan
Push-Location $ApiDir
if (-not (Test-Path ".venv\Scripts\python.exe")) {
  python -m venv .venv
}
.\.venv\Scripts\python.exe -m pip install -q -e ".[dev]"
Pop-Location

Write-Host "Installing Web deps (if needed)..." -ForegroundColor Cyan
Push-Location $WebDir
if (-not (Test-Path "node_modules")) {
  npm install
}
Pop-Location

# Ensure data dirs exist
New-Item -ItemType Directory -Force -Path (Join-Path $ApiDir "data\uploads") | Out-Null

# Default API port 8010 — avoids common conflicts on 8000 (other local APIs).
$ApiPort = if ($env:API_PORT) { $env:API_PORT } else { "8010" }

Write-Host "Starting API on http://localhost:$ApiPort ..." -ForegroundColor Green
$api = Start-Process -PassThru -NoNewWindow -WorkingDirectory $ApiDir -FilePath "$ApiDir\.venv\Scripts\python.exe" -ArgumentList @(
  "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", $ApiPort, "--reload"
)

Write-Host "Starting Web on http://localhost:3000 ..." -ForegroundColor Green
$web = Start-Process -PassThru -NoNewWindow -WorkingDirectory $WebDir -FilePath "npm" -ArgumentList @("run", "dev", "--", "-H", "0.0.0.0", "-p", "3000")

Write-Host ""
Write-Host "Open http://localhost:3000" -ForegroundColor Yellow
Write-Host "API docs: http://localhost:$ApiPort/docs" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop both processes." -ForegroundColor Yellow

try {
  Wait-Process -Id $api.Id, $web.Id
} finally {
  if (-not $api.HasExited) { Stop-Process -Id $api.Id -Force -ErrorAction SilentlyContinue }
  if (-not $web.HasExited) { Stop-Process -Id $web.Id -Force -ErrorAction SilentlyContinue }
}
