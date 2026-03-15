import os
import stat
from cryptography.fernet import Fernet, InvalidToken
from nodox.core.logger import setup_logger

logger = setup_logger()

ENCRYPTED_EXTENSION = ".nodox"
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
        # En Windows, verificar que no sea world-readable
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
            "No se encontró la variable de entorno NODOX_KEY.\n"
            "Usa la misma llave con la que se cifraron los archivos."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    # Validar que sea una clave Fernet válida
    if not _validate_fernet_key(key):
        error_msg = "La clave NODOX_KEY no es una clave Fernet válida."
        logger.error(error_msg)
        raise RuntimeError(error_msg)

    logger.debug("Clave de descifrado cargada correctamente")
    return key.encode()


def is_encrypted_file(filename):
    return filename.endswith(ENCRYPTED_EXTENSION)


def decrypt_file(filepath, cipher):
    try:
        if os.path.getsize(filepath) > MAX_FILE_SIZE:
            logger.debug(f"Archivo excede tamaño máximo: {filepath}")
            return False

        with open(filepath, "rb") as f:
            encrypted_data = f.read()

        try:
            decrypted_data = cipher.decrypt(encrypted_data)
        except InvalidToken:
            logger.error(f"Clave incorrecta o archivo corrupto: {filepath}")
            return False

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


def decrypt_files(base_path):
    logger.info(f"Iniciando descifrado en: {base_path}")

    try:
        key = load_key()
        cipher = Fernet(key)

        decrypted_count = 0

        for root, _, files in os.walk(base_path):
            for filename in files:
                if not is_encrypted_file(filename):
                    continue

                filepath = os.path.join(root, filename)
                success = decrypt_file(filepath, cipher)

                if success:
                    decrypted_count += 1
                    logger.info(f"Archivo descifrado: {filepath}")

        logger.info(f"Descifrado completado. Total de archivos recuperados: {decrypted_count}")

    except Exception as e:
        logger.error(f"Error durante descifrado en {base_path}: {e}")
