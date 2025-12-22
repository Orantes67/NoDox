import os
import re
from nodox.core.logger import setup_logger

logger = setup_logger()

# =========================
# Patrones de datos sensibles
# =========================

EMAIL_REGEX = re.compile(
    r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
)

# RFC persona física y moral (MX)
RFC_REGEX = re.compile(
    r"\b([A-ZÑ&]{3,4}\d{6}[A-Z0-9]{3})\b"
)

# CURP (MX)
CURP_REGEX = re.compile(
    r"\b([A-Z][AEIOUX][A-Z]{2}\d{2}"
    r"(0[1-9]|1[0-2])"
    r"(0[1-9]|[12]\d|3[01])"
    r"[HM]"
    r"(AS|BC|BS|CC|CS|CH|CL|CM|DF|DG|GT|GR|HG|JC|MC|MN|MS|NT|NL|OC|PL|QT|QR|SP|SL|SR|TC|TS|TL|VZ|YN|ZS)"
    r"[B-DF-HJ-NP-TV-Z]{3}"
    r"[0-9A-Z]\d)\b"
)

# Números largos (posibles tarjetas)
LONG_NUMBER_REGEX = re.compile(
    r"\b\d{13,19}\b"
)

SENSITIVE_PATTERNS = {
    "EMAIL": EMAIL_REGEX,
    "RFC": RFC_REGEX,
    "CURP": CURP_REGEX,
    "LONG_NUMBER": LONG_NUMBER_REGEX,
}

# Archivos a ignorar
IGNORED_EXTENSIONS = (
    ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".rar",
    ".exe", ".bin", ".iso", ".pyc", ".pyo"
)

MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB

# Directorios a excluir por defecto
DEFAULT_EXCLUSIONS = {
    ".git",
    ".venv",
    "venv",
    "__pycache__",
    ".vscode",
    ".idea",
    "logs",
    ".nodox_canary",
    "build",
    "dist",
    ".eggs",
}


def load_exclusions(exclusion_file="nodox/config/exclusions.txt"):
    """Cargar exclusiones desde archivo"""
    exclusions = set(DEFAULT_EXCLUSIONS)
    
    if os.path.exists(exclusion_file):
        try:
            with open(exclusion_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Ignorar líneas vacías y comentarios
                    if line and not line.startswith("#"):
                        exclusions.add(line.rstrip("/"))
        except Exception as e:
            logger.warning(f"No se pudo cargar archivo de exclusiones: {e}")
    
    return exclusions


def should_exclude_path(filepath, exclusions):
    """Verificar si un path debe ser excluido"""
    # Normalizar slashes
    filepath = filepath.replace("\\", "/")
    
    for exclusion in exclusions:
        # Coincidencia exacta o como directorio
        if f"/{exclusion}/" in filepath or filepath.endswith(f"/{exclusion}"):
            return True
        # Coincidencia al inicio
        if filepath.startswith(exclusion + "/") or filepath.startswith(f"./{exclusion}/"):
            return True
    
    return False


def is_text_file(filename):
    return not filename.lower().endswith(IGNORED_EXTENSIONS)


def scan_file(filepath):
    findings = []

    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            logger.debug(f"Archivo excede tamaño máximo: {filepath}")
            return findings

        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

            for label, pattern in SENSITIVE_PATTERNS.items():
                matches = pattern.findall(content)
                if matches:
                    findings.append((label, len(matches)))

    except Exception as e:
        logger.error(f"Error al escanear archivo {filepath}: {e}")

    return findings


def scan_files(base_path):
    logger.info(f"Iniciando escaneo en: {base_path}")

    total_files = 0
    sensitive_files = 0
    exclusions = load_exclusions()

    try:
        for root, dirs, files in os.walk(base_path):
            # Filtrar directorios excluidos in-place
            dirs[:] = [d for d in dirs if not should_exclude_path(
                os.path.join(root, d).replace("\\", "/"), exclusions
            )]
            
            for filename in files:
                filepath = os.path.join(root, filename)

                # Verificar exclusiones
                if should_exclude_path(filepath, exclusions):
                    continue

                if not is_text_file(filename):
                    continue

                total_files += 1
                results = scan_file(filepath)

                if results:
                    sensitive_files += 1
                    logger.warning(f"Archivo sensible detectado: {filepath}")

                    for label, count in results:
                        logger.debug(f"  {label}: {count}")

        logger.info(f"Escaneo completado. Archivos analizados: {total_files}, Archivos sensibles: {sensitive_files}")
    except Exception as e:
        logger.error(f"Error durante escaneo en {base_path}: {e}")

def scan_and_collect(base_path):
    logger.info(f"Iniciando escaneo y recolección en: {base_path}")

    sensitive_files = []
    total_files = 0
    exclusions = load_exclusions()

    try:
        for root, dirs, files in os.walk(base_path):
            # Filtrar directorios excluidos in-place
            dirs[:] = [d for d in dirs if not should_exclude_path(
                os.path.join(root, d).replace("\\", "/"), exclusions
            )]
            
            for filename in files:
                filepath = os.path.join(root, filename)

                # Verificar exclusiones
                if should_exclude_path(filepath, exclusions):
                    continue

                if not is_text_file(filename):
                    continue

                total_files += 1
                results = scan_file(filepath)

                if results:
                    sensitive_files.append(filepath)
                    logger.warning(f"Archivo sensible detectado: {filepath}")

                    for label, count in results:
                        logger.debug(f"  {label}: {count}")

        logger.info(f"Escaneo completado. Archivos analizados: {total_files}, Archivos sensibles: {len(sensitive_files)}")
    except Exception as e:
        logger.error(f"Error durante escaneo y recolección en {base_path}: {e}")

    return sensitive_files
