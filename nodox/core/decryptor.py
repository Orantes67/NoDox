import os
import stat
import json
import hashlib
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from nodox.core.logger import setup_logger
from nodox.core.config_loader import get_encryptor_config

logger = setup_logger()

# Cargar configuración
def _load_decryptor_config():
    try:
        config = get_encryptor_config()
        return {
            "extension": config.get("encrypted_extension", ".nodox"),
            "env_key_name": config.get("env_key_name", "NODOX_KEY"),
            "use_key_derivation": config.get("use_key_derivation", False),
        }
    except Exception:
        return {
            "extension": ".nodox",
            "env_key_name": "NODOX_KEY",
            "use_key_derivation": False,
        }


CONFIG = _load_decryptor_config()
ENCRYPTED_EXTENSION = CONFIG["extension"]
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB para archivos cifrados (incluyen metadata)

# Salt para derivación (debe coincidir con encryptor)
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
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
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
    """Cargar clave de descifrado"""
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
                        key = key.strip('"').strip("'")
                        break
        except Exception as e:
            logger.debug(f"No se pudo leer .env.local: {e}")

    if not key:
        error_msg = (
            f"No se encontró la variable de entorno {CONFIG['env_key_name']}.\n"
            "Usa la misma llave con la que se cifraron los archivos."
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

    logger.debug("Clave de descifrado cargada correctamente")
    return key.encode()


def is_encrypted_file(filename):
    return filename.endswith(ENCRYPTED_EXTENSION)


def decrypt_file(filepath, cipher, verify_integrity: bool = True):
    """
    Descifrar un archivo con verificación de integridad.
    
    Args:
        filepath: Ruta del archivo cifrado
        cipher: Objeto Fernet para descifrado
        verify_integrity: Si verificar checksum después de descifrar
    
    Returns:
        bool: True si el descifrado fue exitoso
    """
    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            logger.debug(f"Archivo excede tamaño máximo: {filepath}")
            return False

        with open(filepath, "rb") as f:
            file_data = f.read()

        # Intentar leer formato nuevo (con metadata)
        metadata = None
        encrypted_data = file_data
        
        try:
            # Leer longitud de metadata (primeros 4 bytes)
            metadata_length = int.from_bytes(file_data[:4], 'big')
            
            # Validar que la longitud sea razonable (< 10KB)
            if metadata_length < 10000:
                metadata_json = file_data[4:4 + metadata_length]
                metadata = json.loads(metadata_json.decode())
                encrypted_data = file_data[4 + metadata_length:]
                logger.debug(f"Metadata encontrada: versión {metadata.get('version', 'unknown')}")
        except (json.JSONDecodeError, ValueError, IndexError):
            # Formato antiguo sin metadata, usar todo el archivo
            logger.debug("Archivo en formato legacy (sin metadata)")
            encrypted_data = file_data

        try:
            decrypted_data = cipher.decrypt(encrypted_data)
        except InvalidToken:
            logger.error(f"Clave incorrecta o archivo corrupto: {filepath}")
            return False

        # Verificar integridad si hay metadata con checksum
        if verify_integrity and metadata and "original_checksum" in metadata:
            calculated_checksum = compute_checksum(decrypted_data)
            expected_checksum = metadata["original_checksum"]
            
            if not verify_checksum(decrypted_data, expected_checksum):
                logger.error(
                    f"❌ VERIFICACIÓN DE INTEGRIDAD FALLIDA: {filepath}\n"
                    f"   Esperado: {expected_checksum[:16]}...\n"
                    f"   Obtenido: {calculated_checksum[:16]}..."
                )
                return False
            
            logger.debug(f"✓ Integridad verificada: {filepath}")

        original_path = filepath[:-len(ENCRYPTED_EXTENSION)]

        if os.path.exists(original_path):
            logger.warning(f"Archivo ya existe, se omite: {original_path}")
            return False

        # Escribir a archivo temporal primero para evitar corrupción
        temp_path = original_path + ".tmp"
        try:
            with open(temp_path, "wb") as f:
                f.write(decrypted_data)
            
            # Renombrar es atómico en la mayoría de sistemas
            os.replace(temp_path, original_path)
            
            # Solo eliminar el cifrado después de confirmar el descifrado
            os.remove(filepath)
            logger.debug(f"Archivo descifrado exitosamente: {filepath}")
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
        logger.error(f"Error al descifrar archivo {filepath}: {e}")
        return False


def decrypt_files(base_path, verify_integrity: bool = True):
    """
    Descifrar todos los archivos .nodox en un directorio.
    
    Args:
        base_path: Directorio base para buscar archivos
        verify_integrity: Si verificar checksums
    """
    logger.info(f"Iniciando descifrado en: {base_path}")

    try:
        key = load_key()
        cipher = Fernet(key)

        decrypted_count = 0
        failed_count = 0

        for root, _, files in os.walk(base_path):
            for filename in files:
                if not is_encrypted_file(filename):
                    continue

                filepath = os.path.join(root, filename)
                success = decrypt_file(filepath, cipher, verify_integrity)

                if success:
                    decrypted_count += 1
                    logger.info(f"Archivo descifrado: {filepath}")
                else:
                    failed_count += 1

        logger.info(
            f"Descifrado completado. "
            f"Recuperados: {decrypted_count}, Fallidos: {failed_count}"
        )

    except Exception as e:
        logger.error(f"Error durante descifrado en {base_path}: {e}")
