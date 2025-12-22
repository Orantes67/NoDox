#!/bin/bash
# Script de instalación para NoDox en Linux/Mac

set -e  # Exit on error

echo ""
echo "========================================"
echo "  NoDox - Setup Inicial (Linux/Mac)"
echo "========================================"
echo ""

# Paso 1: Verificar Python
echo "[1/4] Verificando Python..."
if ! command -v python &> /dev/null; then
    echo "ERROR: Python no está instalado"
    echo "Instala Python 3.12+:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-venv"
    echo "  macOS: brew install python"
    exit 1
fi
python --version
echo "OK"
echo ""

# Paso 2: Crear entorno virtual
echo "[2/4] Creando entorno virtual..."
if [ -d ".venv" ]; then
    echo "Entorno virtual ya existe, omitiendo..."
else
    python -m venv .venv
    echo "Entorno virtual creado"
fi
echo "OK"
echo ""

# Paso 3: Activar entorno virtual
echo "[3/4] Activando entorno virtual..."
source .venv/bin/activate
echo "OK"
echo ""

# Paso 4: Instalar dependencias
echo "[4/4] Instalando dependencias..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "OK"
echo ""

echo "========================================"
echo "  SETUP COMPLETADO!"
echo "========================================"
echo ""
echo "Próximos pasos:"
echo ""
echo "1. Activar entorno virtual (en una nueva terminal):"
echo "   source .venv/bin/activate"
echo ""
echo "2. Generar clave de cifrado:"
echo "   python generate_key.py"
echo ""
echo "3. Ejecutar NoDox (después de configurar NODOX_KEY):"
echo "   export NODOX_KEY='tu_clave_aqui'"
echo "   python nodox.py protect"
echo ""
echo ""
