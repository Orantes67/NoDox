#!/usr/bin/env pwsh
# Script de instalación para NoDox en Windows PowerShell
# Uso: .\setup.ps1

Write-Host ""
Write-Host "========================================"
Write-Host "  NoDox - Setup Inicial (Windows)"
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Paso 1: Verificar Python
Write-Host "[1/4] Verificando Python..." -ForegroundColor Cyan
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Host "ERROR: Python no está instalado o no está en el PATH" -ForegroundColor Red
    Write-Host "Descarga desde https://www.python.org/" -ForegroundColor Yellow
    Write-Host "Asegúrate de marcar 'Add Python to PATH'" -ForegroundColor Yellow
    Read-Host "Presiona Enter para continuar"
    exit 1
}
python --version
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Paso 2: Crear entorno virtual
Write-Host "[2/4] Creando entorno virtual..." -ForegroundColor Cyan
if (Test-Path ".venv") {
    Write-Host "Entorno virtual ya existe, omitiendo..."
} else {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: No se pudo crear el entorno virtual" -ForegroundColor Red
        Read-Host "Presiona Enter para continuar"
        exit 1
    }
    Write-Host "Entorno virtual creado"
}
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Paso 3: Activar entorno virtual
Write-Host "[3/4] Activando entorno virtual..." -ForegroundColor Cyan
& ".\.venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudo activar el entorno virtual" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}
Write-Host "OK" -ForegroundColor Green
Write-Host ""

# Paso 4: Instalar dependencias
Write-Host "[4/4] Instalando dependencias..." -ForegroundColor Cyan
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: No se pudieron instalar las dependencias" -ForegroundColor Red
    Read-Host "Presiona Enter para continuar"
    exit 1
}
Write-Host "OK" -ForegroundColor Green
Write-Host ""

Write-Host "========================================"
Write-Host "  SETUP COMPLETADO!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Próximos pasos:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Generar clave de cifrado:"
Write-Host "   python generate_key.py" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Ejecutar NoDox (después de configurar NODOX_KEY):"
Write-Host "   python nodox.py protect" -ForegroundColor Yellow
Write-Host ""
Write-Host ""

Read-Host "Presiona Enter para continuar"
