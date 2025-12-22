# 🚀 SETUP RÁPIDO NoDox

## Requisitos
- Python 3.12+
- pip

## Instalación (5 minutos)

### 1. Clonar repositorio
```bash
git clone https://github.com/Orantes67/NoDox.git
cd NoDox
```

### 2. Instalación automática (RECOMENDADO)

**Windows - Doble clic:**
```
setup.bat
```

**Windows - PowerShell:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
bash setup.sh
```

**O instalación manual:**
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# Linux/Mac:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### 3. Generar clave de cifrado

**Windows - Doble clic:**
```
generate_key.bat
```

**Windows - PowerShell/CMD:**
```bash
python generate_key.py
```

**Linux/Mac:**
```bash
python generate_key.py
```

Copia la salida (ej: `ySViInfB1cQlMzs6TZu2PGTln8D2TKpP6WytM7l2xus=`)

### 5. Configurar clave

**Opción A: Variable de entorno (Recomendado)**

Linux/Mac:
```bash
export NODOX_KEY='tu_clave_aqui'
```

Windows CMD:
```cmd
set NODOX_KEY=tu_clave_aqui
```

Windows PowerShell:
```powershell
$env:NODOX_KEY='tu_clave_aqui'
```

**Opción B: Archivo `.env.local`**

```bash
cp .env.example .env.local
# Editar .env.local y agregar tu clave
```

## Primeras ejecuciones

### Prueba rápida (Escaneo)
```bash
python nodox.py scan -p .
```

### Modo completo (Recomendado)
```bash
python nodox.py protect
```

El programa se mantendrá corriendo monitoreando:
- 🐦 Canary files
- 📡 Exfiltración de datos

Presiona `Ctrl+C` para detener.

## Solución de problemas

### Error en PowerShell al generar clave
Si ves errores como "La palabra clave 'from' no se admite" o "El operador '<' está reservado":

```powershell
# Usa este comando en su lugar:
python generate_key.py
```

[Ver guía completa de Windows →](WINDOWS_TROUBLESHOOTING.md)

### Variable NODOX_KEY no funciona
Si la variable no persiste en PowerShell, usa `.env.local`:

```powershell
Copy-Item .env.example .env.local
notepad .env.local  # Agrega tu clave y guarda
```

### ModuleNotFoundError
```bash
# Asegúrate de estar en el entorno virtual
.venv\Scripts\activate

# Reinstala dependencias
pip install -r requirements.txt
```

## Próximos pasos

1. Revisa la documentación completa en `README.md`
2. Configura `nodox/config/nodox.yaml` según tus necesidades
3. Edita `nodox/config/exclusions.txt` con tus directorios a excluir

---

¿Problemas? Abre un issue en GitHub: https://github.com/Orantes67/NoDox/issues
