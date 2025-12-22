@echo off
REM Script para generar clave Fernet en Windows CMD
REM Este evita problemas con comillas en PowerShell

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  Generador de Clave NoDox
echo ========================================
echo.

REM Verificar si el entorno virtual existe
if not exist ".venv\" (
    echo ERROR: Entorno virtual no encontrado
    echo.
    echo Ejecuta primero:
    echo   python -m venv .venv
    echo   .venv\Scripts\activate
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar si cryptography está instalado
pip show cryptography > nul 2>&1
if errorlevel 1 (
    echo ERROR: cryptography no está instalado
    echo.
    echo Instalando dependencias...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ERROR: No se pudieron instalar las dependencias
        pause
        exit /b 1
    )
)

echo Generando clave...
echo.

python generate_key.py

echo.
echo Instrucciones para Windows CMD:
echo.
echo 1. Copiar la clave mostrada arriba
echo.
echo 2. En la misma terminal ejecuta:
echo    set NODOX_KEY=tu_clave_aqui
echo.
echo 3. Luego ejecuta NoDox:
echo    python nodox.py protect
echo.
echo.

pause

