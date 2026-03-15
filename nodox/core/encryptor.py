import os
import stat
from cryptography.fernet import Fernet
from nodox.core.logger import setup_logger

logger = setup_logger()

# Extensión para archivos cifrados
ENCRYPTED_EXTENSION = ".nodox"

# Tamaño máximo (2MB)
MAX_FILE_SIZE = 2 * 1024 * 1024


def _validate_fernet_key(key: str) -> bool:
    """Validar que la clave sea una clave Fernet válida"""
    try:
        Fernet(key.encode())
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


def load_key():
    """Cargar clave de cifrado desde variable de entorno o archivo"""
    key = os.getenv("NODOX_KEY")
    
    # Si no está en env, intentar cargar desde archivo .env.local
    if not key and os.path.exists(".env.local"):
        _check_env_file_permissions(".env.local")
        try:
            with open(".env.local", "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("NODOX_KEY=") and not line.startswith("#"):
                        key = line.split("=", 1)[1].strip()
                        # Remover comillas si existen
                        key = key.strip('"').strip("'")
                        break
        except Exception as e:
            logger.debug(f"No se pudo leer .env.local: {e}")

    if not key:
        error_msg = (
            "No se encontró la clave de cifrado NODOX_KEY.\n\n"
            "Soluciones:\n"
            "1. Generar clave: python generate_key.py\n"
            "2. Establecer variable de entorno o crear .env.local\n"
            "   Ver: QUICKSTART.md para instrucciones detalladas"
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Validar que sea una clave Fernet válida
    if not _validate_fernet_key(key):
        error_msg = "La clave NODOX_KEY no es una clave Fernet válida."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.debug("Clave de cifrado cargada correctamente")
    return key.encode()


def should_encrypt(filename):
    return not filename.endswith(ENCRYPTED_EXTENSION)


def encrypt_file(filepath, cipher):
    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            logger.debug(f"Archivo excede tamaño máximo: {filepath}")
            return False

        with open(filepath, "rb") as f:
            data = f.read()

        encrypted_data = cipher.encrypt(data)

        encrypted_path = filepath + ENCRYPTED_EXTENSION
        temp_path = encrypted_path + ".tmp"

        try:
            # Escribir a archivo temporal primero
            with open(temp_path, "wb") as f:
                f.write(encrypted_data)
            
            # Renombrar es atómico en la mayoría de sistemas
            os.replace(temp_path, encrypted_path)
            
            # Limpiar datos sensibles de memoria
            del data
            del encrypted_data
            
            # Solo eliminar original después de confirmar el cifrado
            os.remove(filepath)
            logger.debug(f"Archivo cifrado exitosamente: {filepath}")
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


def encrypt_file_list(file_list):
    logger.info("Cifrado selectivo iniciado")

    try:
        key = load_key()
        cipher = Fernet(key)

        encrypted_count = 0

        for filepath in file_list:
            if not os.path.exists(filepath):
                logger.warning(f"Archivo no encontrado: {filepath}")
                continue

            success = encrypt_file(filepath, cipher)

            if success:
                encrypted_count += 1
                logger.info(f"Archivo cifrado: {filepath}")

        logger.info(f"Cifrado completado. Total de archivos cifrados: {encrypted_count}")

    except Exception as e:
        logger.error(f"Error durante cifrado selectivo: {e}")

