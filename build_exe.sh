#!/bin/bash
# Script para generar ejecutable de NoDox con PyInstaller
# Genera: dist/nodox/nodox

set -e

echo ""
echo "========================================"
echo "  NoDox - Generador de Ejecutable"
echo "========================================"
echo ""

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo "ERROR: Entorno virtual no encontrado"
    echo "Ejecuta primero: bash setup.sh"
    exit 1
fi

# Activar entorno virtual
source .venv/bin/activate

# Verificar PyInstaller
if ! pip show pyinstaller > /dev/null 2>&1; then
    echo "Instalando PyInstaller..."
    pip install pyinstaller
fi

echo ""
echo "Generando ejecutable..."
echo ""

# Limpiar builds anteriores
rm -rf build/ dist/

# Ejecutar PyInstaller
pyinstaller nodox.spec

echo ""
echo "========================================"
echo "  EJECUTABLE GENERADO EXITOSAMENTE"
echo "========================================"
echo ""
echo "Ubicación: dist/nodox/nodox"
echo ""
echo "Para usar:"
echo "  1. Copia la carpeta dist/nodox a donde quieras"
echo "  2. Configura NODOX_KEY como variable de entorno"
echo "  3. Ejecuta: ./nodox protect"
echo ""
