# 🪟 Guía de troubleshooting para Windows

## Problema 1: Error al generar clave en PowerShell

### Síntoma
```
Get-Process : No se encuentra ningún parámetro de posición...
El operador '<' está reservado para uso futuro...
La palabra clave 'from' no se admite...
```

### Causa
PowerShell está interpretando los caracteres especiales del comando Python (comillas, paréntesis, etc.)

### Solución
**Usa el script helper en su lugar:**
```powershell
python generate_key.py
```

Esto genera la clave sin problemas de sintaxis de PowerShell.

---

## Problema 2: Variable de entorno no funciona en PowerShell

### Síntoma
```
NODOX_KEY no reconocida en el próximo comando
```

### Causa
Las variables de entorno en PowerShell solo persisten en la sesión actual

### Solución

**Opción A: Establecer en cada sesión**
```powershell
$env:NODOX_KEY = 'tu_clave_aqui'
python nodox.py protect
```

**Opción B: Persistente (recomendado) - Crear archivo .env.local**
```powershell
# Copiar el archivo de ejemplo
Copy-Item .env.example .env.local

# Editar con Notepad
notepad .env.local
```

Luego agregar:
```
NODOX_KEY=tu_clave_aqui
```

Guardar y listo. NoDox lo cargará automáticamente.

**Opción C: Variable de entorno permanente en el sistema**
```powershell
# Ejecutar como Administrador
[Environment]::SetEnvironmentVariable("NODOX_KEY", "tu_clave_aqui", "User")
```

Luego reinicia la terminal.

---

## Problema 3: "ModuleNotFoundError: No module named 'cryptography'"

### Síntoma
```
ModuleNotFoundError: No module named 'cryptography'
```

### Causa
Las dependencias no están instaladas o el entorno virtual no está activado

### Solución

**Opción A: Usar script automático (RECOMENDADO)**
```powershell
# Ejecuta esto primero
.\setup.bat

# Luego
.\generate_key.bat
```

**Opción B: Manual**
```powershell
# 1. Crear entorno virtual
python -m venv .venv

# 2. Activar
.venv\Scripts\activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Generar clave
python generate_key.py
```

---

## Problema 4: ".venv not found" o no puedo activar

### Causa
El entorno virtual no existe o está en la ruta equivocada

### Solución
```powershell
# Crear el entorno virtual
python -m venv .venv

# Activar
.venv\Scripts\activate

# Deberías ver (.venv) al inicio de tu terminal
```

---

## Problema 5: "No se encontró Python"

### Causa
Python no está en el PATH del sistema

### Solución
**Opción A: Usar ruta completa de Python**
```powershell
C:\Users\HECTOR ROMAN\AppData\Local\Programs\Python\Python312\python.exe generate_key.py
```

**Opción B: Agregar Python al PATH**
1. Abre "Variables de entorno" (busca en Windows)
2. Edita variables de entorno
3. Agrega la ruta de Python a PATH
4. Reinicia la terminal

**Opción C: Reinstalar Python**
- Descargar desde python.org
- Asegúrate de marcar "Add Python to PATH"

---

## Problema 6: Espacios en la ruta (path con espacios)

### Síntoma
```
No se encuentra ningún archivo especificado.
```

### Causa
Tienes espacios en tu ruta (ej: "HECTOR ROMAN")

### Solución
Usar comillas cuando sea necesario:
```powershell
python "C:\Users\HECTOR ROMAN\OneDrive\Escritorio\NoDox\generate_key.py"
```

O navegar a la carpeta primero:
```powershell
cd "C:\Users\HECTOR ROMAN\OneDrive\Escritorio\NoDox"
python generate_key.py
```

---

## Problema 7: Permisos de ejecución

### Síntoma
```
No está permitido ejecutar scripts en este sistema
```

### Causa
Política de ejecución de PowerShell restrictiva

### Solución
```powershell
# En una terminal como Administrador:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Verdificación rápida

```powershell
# 1. ¿Python está instalado?
python --version

# 2. ¿Estoy en el entorno virtual?
# Debería haber (.venv) al inicio de la línea

# 3. ¿Están las dependencias?
pip list | findstr cryptography

# 4. ¿Puedo generar clave?
python generate_key.py

# 5. ¿Puedo ejecutar NoDox?
python nodox.py --help
```

---

## ¿Aún tienes problemas?

1. Revisa los logs en `logs/nodox.log`
2. Abre un issue en GitHub con:
   - Tu versión de Windows
   - Tu versión de Python (`python --version`)
   - El error completo
   - Los pasos que seguiste

---

**💡 Tip:** Si sigues teniendo problemas con PowerShell, prueba con **CMD (Símbolo del sistema)** - a veces funciona mejor:
```cmd
python generate_key.py
set NODOX_KEY=tu_clave_aqui
python nodox.py protect
```
