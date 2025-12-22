import os
from cryptography.fernet import Fernet
from nodox.core.logger import setup_logger

logger = setup_logger()

ENCRYPTED_EXTENSION = ".nodox"
MAX_FILE_SIZE = 2 * 1024 * 1024


def load_key():
    key = os.getenv("NODOX_KEY")

    if not key:
        error_msg = (
            "No se encontró la variable de entorno NODOX_KEY.\n"
            "Usa la misma llave con la que se cifraron los archivos."
        )
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

        decrypted_data = cipher.decrypt(encrypted_data)

        original_path = filepath[:-len(ENCRYPTED_EXTENSION)]

        if os.path.exists(original_path):
            logger.warning(f"Archivo ya existe, se omite: {original_path}")
            return False

        with open(original_path, "wb") as f:
            f.write(decrypted_data)

        os.remove(filepath)
        logger.debug(f"Archivo descifrado exitosamente: {filepath}")

        return True

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
