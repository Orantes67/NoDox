import os
import re
from nodox.core.logger import setup_logger
from nodox.core.config_loader import get_scanner_config

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

# Números largos (posibles tarjetas) - 13-19 dígitos
CREDIT_CARD_REGEX = re.compile(
    r"\b(?:4[0-9]{12}(?:[0-9]{3})?|"           # Visa
    r"5[1-5][0-9]{14}|"                         # MasterCard
    r"3[47][0-9]{13}|"                          # American Express
    r"6(?:011|5[0-9]{2})[0-9]{12}|"            # Discover
    r"(?:2131|1800|35\d{3})\d{11})\b"          # JCB
)

# SSN (Social Security Number - USA)
SSN_REGEX = re.compile(
    r"\b(?!000|666|9\d{2})\d{3}[-\s]?(?!00)\d{2}[-\s]?(?!0000)\d{4}\b"
)

# IBAN (International Bank Account Number)
IBAN_REGEX = re.compile(
    r"\b[A-Z]{2}\d{2}[A-Z0-9]{4,30}\b"
)

# =============================
# Patrones de API Keys y Tokens
# =============================

# AWS Access Key ID
AWS_KEY_REGEX = re.compile(
    r"\b(AKIA|ABIA|ACCA|ASIA)[0-9A-Z]{16}\b"
)

# AWS Secret Access Key
AWS_SECRET_REGEX = re.compile(
    r"(?i)aws[_\-]?secret[_\-]?access[_\-]?key['\"]?\s*[:=]\s*['\"]?([A-Za-z0-9/+=]{40})['\"]?"
)

# GitHub Token
GITHUB_TOKEN_REGEX = re.compile(
    r"\b(ghp_[a-zA-Z0-9]{36}|"                  # Personal access token
    r"gho_[a-zA-Z0-9]{36}|"                     # OAuth access token
    r"ghu_[a-zA-Z0-9]{36}|"                     # User-to-server token
    r"ghs_[a-zA-Z0-9]{36}|"                     # Server-to-server token
    r"ghr_[a-zA-Z0-9]{36})\b"                   # Refresh token
)

# Google API Key
GOOGLE_API_REGEX = re.compile(
    r"\bAIza[0-9A-Za-z\-_]{35}\b"
)

# Slack Token
SLACK_TOKEN_REGEX = re.compile(
    r"\b(xox[baprs]-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*)\b"
)

# Generic API Key patterns
GENERIC_API_KEY_REGEX = re.compile(
    r"(?i)(?:api[_\-]?key|apikey|api_secret|access[_\-]?token|auth[_\-]?token|secret[_\-]?key)"
    r"['\"]?\s*[:=]\s*['\"]?([a-zA-Z0-9_\-]{20,})['\"]?"
)

# Password in code
PASSWORD_IN_CODE_REGEX = re.compile(
    r"(?i)(?:password|passwd|pwd|secret|contraseña)"
    r"['\"]?\s*[:=]\s*['\"]?([^\s'\",;]{8,})['\"]?"
)

# Private Key markers
PRIVATE_KEY_REGEX = re.compile(
    r"-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----"
)

# JWT Token
JWT_REGEX = re.compile(
    r"\beyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*\b"
)

SENSITIVE_PATTERNS = {
    "EMAIL": EMAIL_REGEX,
    "RFC": RFC_REGEX,
    "CURP": CURP_REGEX,
    "CREDIT_CARD": CREDIT_CARD_REGEX,
    "SSN": SSN_REGEX,
    "IBAN": IBAN_REGEX,
    "AWS_KEY": AWS_KEY_REGEX,
    "AWS_SECRET": AWS_SECRET_REGEX,
    "GITHUB_TOKEN": GITHUB_TOKEN_REGEX,
    "GOOGLE_API_KEY": GOOGLE_API_REGEX,
    "SLACK_TOKEN": SLACK_TOKEN_REGEX,
    "API_KEY": GENERIC_API_KEY_REGEX,
    "PASSWORD_IN_CODE": PASSWORD_IN_CODE_REGEX,
    "PRIVATE_KEY": PRIVATE_KEY_REGEX,
    "JWT_TOKEN": JWT_REGEX,
}

# Severidad de cada tipo de dato
PATTERN_SEVERITY = {
    "EMAIL": "MEDIUM",
    "RFC": "HIGH",
    "CURP": "HIGH",
    "CREDIT_CARD": "CRITICAL",
    "SSN": "CRITICAL",
    "IBAN": "CRITICAL",
    "AWS_KEY": "CRITICAL",
    "AWS_SECRET": "CRITICAL",
    "GITHUB_TOKEN": "CRITICAL",
    "GOOGLE_API_KEY": "HIGH",
    "SLACK_TOKEN": "HIGH",
    "API_KEY": "HIGH",
    "PASSWORD_IN_CODE": "CRITICAL",
    "PRIVATE_KEY": "CRITICAL",
    "JWT_TOKEN": "HIGH",
}


def luhn_checksum(card_number: str) -> bool:
    """
    Validar número de tarjeta usando algoritmo de Luhn.
    Retorna True si el número es válido.
    """
    def digits_of(n):
        return [int(d) for d in str(n)]
    
    digits = digits_of(card_number.replace(" ", "").replace("-", ""))
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(digits_of(d * 2))
    
    return checksum % 10 == 0


def _load_config_values():
    """Cargar valores desde configuración YAML"""
    try:
        config = get_scanner_config()
        max_size_mb = config.get("max_file_size_mb", 2)
        ignored_ext = tuple(config.get("ignored_extensions", []))
        return max_size_mb * 1024 * 1024, ignored_ext
    except Exception:
        # Valores por defecto si no se puede cargar config
        return 2 * 1024 * 1024, (
            ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".rar",
            ".exe", ".bin", ".iso", ".pyc", ".pyo"
        )


# Cargar configuración
MAX_FILE_SIZE, IGNORED_EXTENSIONS = _load_config_values()

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
    """
    Escanear un archivo en busca de datos sensibles.
    Retorna lista de tuplas (label, count, severity).
    """
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
                    # Validación especial para tarjetas de crédito
                    if label == "CREDIT_CARD":
                        valid_cards = [m for m in matches if luhn_checksum(m if isinstance(m, str) else m[0])]
                        if valid_cards:
                            severity = PATTERN_SEVERITY.get(label, "MEDIUM")
                            findings.append((label, len(valid_cards), severity))
                    else:
                        severity = PATTERN_SEVERITY.get(label, "MEDIUM")
                        findings.append((label, len(matches), severity))

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

                    for label, count, severity in results:
                        logger.debug(f"  [{severity}] {label}: {count}")

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

                    for label, count, severity in results:
                        logger.debug(f"  [{severity}] {label}: {count}")

        logger.info(f"Escaneo completado. Archivos analizados: {total_files}, Archivos sensibles: {len(sensitive_files)}")
    except Exception as e:
        logger.error(f"Error durante escaneo y recolección en {base_path}: {e}")

    return sensitive_files
