# GameVault - Setup del ambiente (Windows / PowerShell)
# Crea .env si no existe, el venv, instala dependencias, crea la BD si no existe y aplica migraciones.
$ErrorActionPreference = 'Stop'

# Configuracion local: se lee de .env (nunca se sube al repositorio).
if (-not (Test-Path .\.env)) {
    Write-Host '==> Creando .env a partir de .env.example' -ForegroundColor Cyan
    $dbPass = Read-Host 'Contraseña del usuario postgres'
    $secret = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 50 | ForEach-Object { [char]$_ })
    (Get-Content .\.env.example) `
        -replace '^DJANGO_SECRET_KEY=.*', "DJANGO_SECRET_KEY=$secret" `
        -replace '^DB_PASSWORD=.*', "DB_PASSWORD=$dbPass" |
        Set-Content .\.env -Encoding UTF8
}

$cfg = @{}
foreach ($line in Get-Content .\.env) {
    if ($line -match '^\s*([A-Z_]+)\s*=\s*(.*)$') {
        $cfg[$Matches[1]] = $Matches[2].Trim()
    }
}
$DB_NAME = if ($cfg.DB_NAME) { $cfg.DB_NAME } else { 'gamevault' }
$DB_USER = if ($cfg.DB_USER) { $cfg.DB_USER } else { 'postgres' }
$DB_PASSWORD = $cfg.DB_PASSWORD
$DB_HOST = if ($cfg.DB_HOST) { $cfg.DB_HOST } else { 'localhost' }
$DB_PORT = if ($cfg.DB_PORT) { $cfg.DB_PORT } else { '5432' }

Write-Host '==> 1/4 Entorno virtual' -ForegroundColor Cyan
if (-not (Test-Path .\venv)) {
    python -m venv venv
}
& .\venv\Scripts\python.exe -m pip install --upgrade pip
& .\venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host '==> 2/4 Base de datos PostgreSQL' -ForegroundColor Cyan
$psql = Get-Command psql -ErrorAction SilentlyContinue
if (-not $psql) {
    Write-Host 'psql no encontrado en PATH. Crea la BD manualmente y salta al paso 3.' -ForegroundColor Yellow
} else {
    $env:PGPASSWORD = $DB_PASSWORD
    $exists = & psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -tAc `
        "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" 2>$null
    if ($exists -eq '1') {
        Write-Host "La base de datos '$DB_NAME' ya existe." -ForegroundColor Green
    } else {
        & psql -U $DB_USER -h $DB_HOST -p $DB_PORT -d postgres -c "CREATE DATABASE $DB_NAME;"
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Base de datos '$DB_NAME' creada." -ForegroundColor Green
        } else {
            Write-Host 'No se pudo crear la base de datos (revisa usuario/contraseña).' -ForegroundColor Yellow
        }
    }
    Remove-Item Env:PGPASSWORD
}

Write-Host '==> 3/4 Migraciones y datos demo' -ForegroundColor Cyan
& .\venv\Scripts\python.exe manage.py migrate
& .\venv\Scripts\python.exe manage.py seed_demo_data

Write-Host '==> 4/4 Listo' -ForegroundColor Cyan
Write-Host ''
Write-Host 'Superusuario (opcional):' -ForegroundColor Gray
Write-Host '  .\venv\Scripts\python.exe manage.py createsuperuser'
Write-Host 'Servidor de desarrollo:' -ForegroundColor Gray
Write-Host '  .\venv\Scripts\python.exe manage.py runserver'
