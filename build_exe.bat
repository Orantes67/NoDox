@echo off
REM Script para generar ejecutable de NoDox con PyInstaller
REM Genera: dist\nodox\nodox.exe

setlocal enabledelayedexpansion

echo.
echo ========================================
echo  NoDox - Generador de Ejecutable
echo ========================================
echo.

REM Verificar entorno virtual
if not exist ".venv\" (
    echo ERROR: Entorno virtual no encontrado
    echo Ejecuta primero: setup.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar PyInstaller
pip show pyinstaller > nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo ERROR: No se pudo instalar PyInstaller
        pause
        exit /b 1
    )
)

echo.
echo Generando ejecutable...
echo.

REM Limpiar builds anteriores
if exist "build\" rmdir /s /q build
if exist "dist\" rmdir /s /q dist

REM Ejecutar PyInstaller
pyinstaller nodox.spec

if errorlevel 1 (
    echo.
    echo ERROR: Fallo al generar ejecutable
    pause
    exit /b 1
)

echo.
echo ========================================
echo  EJECUTABLE GENERADO EXITOSAMENTE
echo ========================================
echo.
echo Ubicacion: dist\nodox\nodox.exe
echo.
echo Para usar:
echo   1. Copia la carpeta dist\nodox a donde quieras
echo   2. Configura NODOX_KEY como variable de entorno
echo   3. Ejecuta: nodox.exe protect
echo.

pause
