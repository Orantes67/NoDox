import os
import stat
import hashlib
import base64
import json
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from nodox.core.logger import setup_logger
from nodox.core.config_loader import get_encryptor_config

logger = setup_logger()

# Cargar configuración
def _load_encryptor_config():
    try:
        config = get_encryptor_config()
        return {
            "extension": config.get("encrypted_extension", ".nodox"),
            "use_env_key": config.get("use_env_key", True),
            "env_key_name": config.get("env_key_name", "NODOX_KEY"),
            "create_backup": config.get("create_backup", True),
            "backup_dir": config.get("backup_dir", ".nodox_backups"),
            "use_key_derivation": config.get("use_key_derivation", False),
        }
    except Exception:
        return {
            "extension": ".nodox",
            "use_env_key": True,
            "env_key_name": "NODOX_KEY",
            "create_backup": True,
            "backup_dir": ".nodox_backups",
            "use_key_derivation": False,
        }


CONFIG = _load_encryptor_config()
ENCRYPTED_EXTENSION = CONFIG["extension"]
BACKUP_DIR = CONFIG["backup_dir"]

# Tamaño máximo (2MB)
MAX_FILE_SIZE = 2 * 1024 * 1024

# Salt fijo para derivación de claves (en producción usar salt único por archivo)
DEFAULT_SALT = b'NoDox_Salt_2024!'


def compute_checksum(data: bytes) -> str:
    """Calcular SHA-256 checksum de datos"""
    return hashlib.sha256(data).hexdigest()


def verify_checksum(data: bytes, expected_checksum: str) -> bool:
    """Verificar integridad de datos usando checksum"""
    return compute_checksum(data) == expected_checksum


def derive_key_from_password(password: str, salt: bytes = DEFAULT_SALT) -> bytes:
    """
    Derivar clave Fernet desde una contraseña usando PBKDF2.
    Más seguro que usar la contraseña directamente.
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP recomienda mínimo 310,000 para SHA-256
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def _validate_fernet_key(key: str) -> bool:
    """Validar que la clave sea una clave Fernet válida"""
    try:
        Fernet(key.encode() if isinstance(key, str) else key)
        return True
    except (ValueError, TypeError):
        return False


def _check_env_file_permissions(filepath: str) -> bool:
    """Verificar que el archivo .env.local tenga permisos seguros"""
    try:
        file_stat = os.stat(filepath)
        # En Unix, verificar modo 600 o 400
        if os.name != 'nt':  # Unix
            mode = file_stat.st_mode
            if mode & (stat.S_IRWXG | stat.S_IRWXO):
                logger.warning(
                    f"⚠️ Permisos inseguros en {filepath}. "
                    "Recomendado: chmod 600 .env.local"
                )
        return True
    except OSError:
        return False


def load_key(use_derivation: bool = None):
    """
    Cargar clave de cifrado desde variable de entorno o archivo.
    Si use_derivation es True, deriva la clave usando PBKDF2.
    """
    if use_derivation is None:
        use_derivation = CONFIG.get("use_key_derivation", False)
    
    key = os.getenv(CONFIG["env_key_name"])
    
    # Si no está en env, intentar cargar desde archivo .env.local
    if not key and os.path.exists(".env.local"):
        _check_env_file_permissions(".env.local")
        try:
            with open(".env.local", "r") as f:
                for line in f:
                    line = line.strip()
                    key_name = CONFIG["env_key_name"]
                    if line.startswith(f"{key_name}=") and not line.startswith("#"):
                        key = line.split("=", 1)[1].strip()
                        # Remover comillas si existen
                        key = key.strip('"').strip("'")
                        break
        except Exception as e:
            logger.debug(f"No se pudo leer .env.local: {e}")

    if not key:
        error_msg = (
            f"No se encontró la clave de cifrado {CONFIG['env_key_name']}.\n\n"
            "Soluciones:\n"
            "1. Generar clave: python generate_key.py\n"
            "2. Establecer variable de entorno o crear .env.local\n"
            "   Ver: QUICKSTART.md para instrucciones detalladas"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Derivar clave si está habilitado
    if use_derivation:
        logger.debug("Usando derivación de clave (PBKDF2)")
        return derive_key_from_password(key)
    
    # Validar que sea una clave Fernet válida
    if not _validate_fernet_key(key):
        error_msg = f"La clave {CONFIG['env_key_name']} no es una clave Fernet válida."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.debug("Clave de cifrado cargada correctamente")
    return key.encode()


def should_encrypt(filename):
    return not filename.endswith(ENCRYPTED_EXTENSION)


def create_backup(filepath: str) -> str:
    """
    Crear backup del archivo antes de cifrarlo.
    Retorna la ruta del backup o None si falla.
    """
    try:
        # Crear directorio de backups si no existe
        os.makedirs(BACKUP_DIR, exist_ok=True)
        
        # Nombre del backup con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.basename(filepath)
        backup_filename = f"{timestamp}_{filename}.bak"
        backup_path = os.path.join(BACKUP_DIR, backup_filename)
        
        # Copiar archivo
        with open(filepath, "rb") as src:
            data = src.read()
        with open(backup_path, "wb") as dst:
            dst.write(data)
        
        logger.debug(f"Backup creado: {backup_path}")
        return backup_path
        
    except Exception as e:
        logger.warning(f"No se pudo crear backup de {filepath}: {e}")
        return None


def encrypt_file(filepath, cipher, create_bak: bool = None):
    """
    Cifrar un archivo con verificación de integridad.
    
    Args:
        filepath: Ruta del archivo a cifrar
        cipher: Objeto Fernet para cifrado
        create_bak: Si crear backup (None usa configuración)
    
    Returns:
        bool: True si el cifrado fue exitoso
    """
    if create_bak is None:
        create_bak = CONFIG.get("create_backup", True)
    
    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            logger.debug(f"Archivo excede tamaño máximo: {filepath}")
            return False

        # Leer datos originales
        with open(filepath, "rb") as f:
            data = f.read()

        # Calcular checksum original para verificación
        original_checksum = compute_checksum(data)
        
        # Crear backup si está habilitado
        backup_path = None
        if create_bak:
            backup_path = create_backup(filepath)

        # Cifrar datos
        encrypted_data = cipher.encrypt(data)
        
        # Crear metadata con checksum para verificación posterior
        metadata = {
            "original_checksum": original_checksum,
            "original_size": len(data),
            "encrypted_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # Combinar metadata + datos cifrados
        metadata_json = json.dumps(metadata).encode()
        metadata_length = len(metadata_json)
        
        # Formato: [4 bytes longitud metadata][metadata JSON][datos cifrados]
        final_data = (
            metadata_length.to_bytes(4, 'big') +
            metadata_json +
            encrypted_data
        )

        encrypted_path = filepath + ENCRYPTED_EXTENSION
        temp_path = encrypted_path + ".tmp"

        try:
            # Escribir a archivo temporal primero
            with open(temp_path, "wb") as f:
                f.write(final_data)
            
            # Renombrar es atómico en la mayoría de sistemas
            os.replace(temp_path, encrypted_path)
            
            # Limpiar datos sensibles de memoria
            del data
            del encrypted_data
            del final_data
            
            # Solo eliminar original después de confirmar el cifrado
            os.remove(filepath)
            logger.debug(f"Archivo cifrado exitosamente: {filepath}")
            logger.debug(f"  Checksum original: {original_checksum[:16]}...")
            return True
            
        except Exception as write_error:
            # Limpiar archivo temporal si existe
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise write_error

    except Exception as e:
        logger.error(f"Error al cifrar archivo {filepath}: {e}")
        return False


def encrypt_file_list(file_list, interactive: bool = False, create_backup: bool = None):
    """
    Cifrar lista de archivos.
    
    Args:
        file_list: Lista de rutas de archivos a cifrar
        interactive: Si True, pide confirmación antes de cada archivo
        create_backup: Si crear backups (None usa configuración)
    """
    logger.info("Cifrado selectivo iniciado")

    try:
        key = load_key()
        cipher = Fernet(key)

        encrypted_count = 0
        skipped_count = 0

        for filepath in file_list:
            if not os.path.exists(filepath):
                logger.warning(f"Archivo no encontrado: {filepath}")
                continue

            # Modo interactivo
            if interactive:
                response = input(f"\n¿Cifrar '{filepath}'? [s/N]: ").strip().lower()
                if response not in ('s', 'si', 'sí', 'y', 'yes'):
                    logger.info(f"Omitido por usuario: {filepath}")
                    skipped_count += 1
                    continue

            success = encrypt_file(filepath, cipher, create_bak=create_backup)

            if success:
                encrypted_count += 1
                logger.info(f"Archivo cifrado: {filepath}")

        logger.info(f"Cifrado completado. Cifrados: {encrypted_count}, Omitidos: {skipped_count}")

    except Exception as e:
        logger.error(f"Error durante cifrado selectivo: {e}")

