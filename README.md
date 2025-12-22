# 🛡️ NoDox

**Neutralizing Doxware & Modern Ransomware Extortion**

NoDox es una herramienta open-source enfocada en reducir el impacto real del ransomware moderno, especialmente el doxware (ransomware con robo y extorsión de datos).

En lugar de intentar "detener" el ransomware cuando ya es demasiado tarde, NoDox se enfoca en quitarle su poder:
👉 **hacer que los datos robados sean inútiles para extorsión, publicación o chantaje.**

---

## 🧠 ¿Por qué NoDox?

El ransomware moderno ya no solo cifra archivos:

- 📤 **Exfiltra información**
- 📢 **Amenaza con publicarla**
- ⚖️ **Extorsiona con daño reputacional y legal**

NoDox cambia el enfoque defensivo:

> Si los datos robados no sirven, la extorsión fracasa.

---

## 🎯 Objetivos del proyecto

- ✅ Reducir el daño del doxware y ransomware moderno
- ✅ Detectar comportamientos sospechosos antes del cifrado masivo
- ✅ Minimizar la exposición de datos sensibles
- ✅ Proveer una herramienta simple, extensible y comunitaria
- ✅ Servir como base para futuras integraciones (GUI, Chrome Extension, SIEM)

---

## 🚀 Características principales

### 🔍 Escaneo de datos sensibles

Detecta archivos que pueden contener:

- Información personal (PII)
- Datos críticos
- Archivos de alto valor para extorsión

### 🔐 Cifrado previo (Data-at-Rest)

- Cifra archivos sensibles antes de que un atacante pueda robarlos
- Incluso si son exfiltrados, resultan inutilizables
- Usa encriptación Fernet (simétrica)

### 🐦 Canary Files

- Archivos señuelo que nadie debería tocar
- Si son modificados → alerta inmediata
- Detección temprana de ransomware

### 📡 Detección de exfiltración

Monitorea comportamientos sospechosos como:

- Subidas masivas de datos
- Actividad anormal de salida
- Compresión sospechosa de archivos

### 🛡️ Modo protect

Pipeline automático:

```
scan → encrypt → canary → monitor
```

Diseñado para ser el modo recomendado de uso.

### 📜 Logging centralizado

- Logs unificados
- Evidencia forense
- Listo para integrarse con sistemas de monitoreo
- Rotación automática de logs

---

## 🧩 Arquitectura (CLI)

```
nodox/
├── core/
│   ├── scanner.py        # Detección de datos sensibles
│   ├── encryptor.py      # Cifrado de archivos
│   ├── decryptor.py      # Descifrado de archivos
│   ├── canary.py         # Archivos señuelo
│   ├── exfil.py          # Monitoreo de exfiltración
│   ├── protect.py        # Orquestación del modo protect
│   ├── config_loader.py  # Carga de configuración YAML
│   └── logger.py         # Sistema de logging
├── config/
│   └── nodox.yaml        # Configuración centralizada
├── logs/
│   └── nodox.log         # Logs rotatorios
└── nodox.py              # Punto de entrada CLI
```

---

## 🖥️ Uso básico

### ⚙️ Configuración inicial

Antes de usar NoDox, debes configurar la clave de cifrado:

#### 1. Generar clave Fernet

**Recomendado: Usar script helper (funciona en todos los SO)**

Windows (doble clic):
```
generate_key.bat
```

Windows (PowerShell/CMD):
```bash
python generate_key.py
```

Linux/Mac:
```bash
python generate_key.py
# o el comando directo:
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

⚠️ **Si estás en Windows PowerShell y los comandos dan errores**, consulta la [Guía de troubleshooting Windows](WINDOWS_TROUBLESHOOTING.md)

#### 2. Configurar variable de entorno

**Windows PowerShell:**
```powershell
$env:NODOX_KEY='tu_clave_generada_aqui'
python nodox.py protect
```

**Windows CMD:**
```cmd
set NODOX_KEY=tu_clave_generada_aqui
python nodox.py protect
```

**Linux/Mac:**
```bash
export NODOX_KEY='tu_clave_generada_aqui'
python nodox.py protect
```

**Alternativa: Crear archivo `.env.local`**
```bash
cp .env.example .env.local
# Editar .env.local y agregar tu clave
nano .env.local  # o tu editor favorito
```

### Escanear archivos
```bash
python nodox.py scan -p /ruta
```

### Cifrado manual
```bash
python nodox.py encrypt -p /ruta
```

### Crear canary files
```bash
python nodox.py canary -p /ruta
```

### Monitorear exfiltración
```bash
python nodox.py monitor
```

### 🔥 Modo recomendado
```bash
python nodox.py protect
```

⚠️ **Nota**: El modo protect requiere NODOX_KEY configurado

---

## 🐳 Docker

### Requisitos previos

1. Generar una clave de cifrado Fernet:

```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Construir imagen

```bash
docker build -t nodox:latest .
```

### Ejecutar contenedor

```bash
docker run -e NODOX_KEY="tu_clave_aqui" --rm nodox:latest
```

Reemplaza `tu_clave_aqui` con la clave generada.

### Ejecutar comandos específicos

```bash
# Escanear
docker run -e NODOX_KEY="tu_clave" --rm nodox:latest python nodox.py scan

# Descifrar
docker run -e NODOX_KEY="tu_clave" --rm nodox:latest python nodox.py decrypt
```

---

## ⚙️ Configuración

NoDox usa `nodox/config/nodox.yaml` para configuración centralizada:

```yaml
nodox:
  version: "0.1"

paths:
  scan_path: "."
  canary_path: "."
  encrypt_path: "."
  decrypt_path: "."

scanner:
  max_file_size_mb: 2
  ignored_extensions:
    - ".png"
    - ".jpg"
    - ".pdf"
    - ".zip"
    - ".exe"

encryptor:
  encrypted_extension: ".nodox"
  use_env_key: true
  env_key_name: "NODOX_KEY"

canary:
  directory: ".nodox_canary"
  check_interval_seconds: 5
  files:
    - "clientes_2025_CONFIDENCIAL.xlsx"
    - "passwords_admin.txt"
    - "contratos_privados.docx"
    - "backup_db.sql"

exfiltration:
  check_interval_seconds: 5
  threshold_mb: 50

logging:
  enabled: true
  level: "INFO"
  file: "logs/nodox.log"
```

---

## 📋 Requisitos

- Python 3.12+
- `cryptography` – Cifrado Fernet
- `pyyaml` – Configuración
- `psutil` – Monitoreo de red

### Instalación automática (RECOMENDADO)

**Windows CMD (doble clic):**
```
setup.bat
```

**Windows PowerShell:**
```powershell
.\setup.ps1
```

**Linux/Mac:**
```bash
bash setup.sh
```

### Instalación manual

```bash
# Crear entorno virtual
python -m venv .venv

# Activar (Linux/Mac)
source .venv/bin/activate
# Activar (Windows)
.venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🧑‍💻 Público objetivo

- 🎓 Estudiantes y juniors de ciberseguridad
- 👨‍💼 Sysadmins y DevOps
- 🏢 Pequeñas empresas
- 🔬 Investigadores de seguridad
- 🌐 Comunidad open-source

---

## 🧪 Estado del proyecto

- 🚧 **Versión**: 0.1.0
- 🚧 **Estado**: MVP funcional (CLI)
- 🚧 **Lenguaje**: Python

### Próximos objetivos

- ✨ Alertas en tiempo real
- 📊 Dashboard visual
- 🔌 Extensión de navegador (Chrome)
- 📧 Notificaciones por email
- 🔗 Integración con SIEM
- 📱 Aplicación móvil

---

## 📊 Patrones de detección

### Scanner detecta

- **EMAIL**: Correos electrónicos
- **RFC**: Identificadores fiscales mexicanos
- **CURP**: Claves personales de identidad (MX)
- **LONG_NUMBER**: Números largos (posibles tarjetas)

Fácilmente extensible para otros patrones.

---

## 🔒 Seguridad

- ✅ Encriptación Fernet (estándar de seguridad)
- ✅ Configuración centralizada
- ✅ Logs auditables
- ✅ No almacena claves en el código
- ✅ Soporta variables de entorno

**IMPORTANTE**: La clave debe estar protegida en sistemas de producción (vaults, secrets manager, etc.)

---

## ⚠️ Disclaimer

**NoDox NO es:**
- ❌ Un antivirus
- ❌ Un reemplazo de un EDR
- ❌ Una solución completa de seguridad

**NoDox ES:**
- ✅ Una capa defensiva adicional
- ✅ Enfocada en minimizar el impacto de la extorsión de datos
- ✅ Parte de una estrategia de seguridad en capas

Úsalo como complemento a otras medidas de seguridad.

---

## 🤝 Contribuciones

Las contribuciones son bienvenidas:

- 💡 Ideas y sugerencias
- 💻 Código y mejoras
- 🐛 Reporte de bugs
- 📚 Documentación
- ✅ Pruebas

Este proyecto busca **educar, proteger y fortalecer** a la comunidad.

---

## 📄 Licencia

**MIT License** – libre para uso personal y comercial.

Consulta el archivo `LICENSE` para más detalles.

---

## ✨ Filosofía NoDox

> **No se elimina el ransomware.**
> 
> **Se elimina su poder.**

---

## 📞 Soporte

- 📖 **Wiki**: Documentación técnica
- 🐛 **Issues**: Reporte de bugs
- 💬 **Discussions**: Preguntas y ideas

---

## 👨‍🔬 Autor

Desarrollado por la comunidad de ciberseguridad.

---

**NoDox v0.1.0** © 2025 | MIT License
