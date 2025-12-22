@echo off
REM Script de instalación rápida para NoDox en Windows
REM Este script configura el entorno virtual e instala dependencias

setlocal enabledelayedexpansion

cls
echo.
echo ========================================
echo  NoDox - Setup Inicial (Windows)
echo ========================================
echo.

REM Paso 1: Verificar Python
echo [1/4] Verificando Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python no está instalado o no está en el PATH
    echo Descarga Python desde https://www.python.org/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    pause
    exit /b 1
)
python --version
echo OK
echo.

REM Paso 2: Crear entorno virtual
echo [2/4] Creando entorno virtual...
if exist ".venv\" (
    echo Entorno virtual ya existe, omitiendo...
) else (
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo Entorno virtual creado
)
echo OK
echo.

REM Paso 3: Activar entorno virtual
echo [3/4] Activando entorno virtual...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: No se pudo activar el entorno virtual
    pause
    exit /b 1
)
echo OK
echo.

REM Paso 4: Instalar dependencias
echo [4/4] Instalando dependencias...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)
echo OK
echo.

echo ========================================
echo  SETUP COMPLETADO!
echo ========================================
echo.
echo Próximos pasos:
echo.
echo 1. Generar clave de cifrado:
echo    .\generate_key.bat
echo.
echo 2. Ejecutar NoDox (después de configurar NODOX_KEY):
echo    python nodox.py protect
echo.
echo.

pause
