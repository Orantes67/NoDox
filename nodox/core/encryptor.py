import os
from cryptography.fernet import Fernet
from nodox.core.logger import setup_logger

logger = setup_logger()

# Extensión para archivos cifrados
ENCRYPTED_EXTENSION = ".nodox"

# Tamaño máximo (2MB)
MAX_FILE_SIZE = 2 * 1024 * 1024


def load_key():
    """Cargar clave de cifrado desde variable de entorno o archivo"""
    key = os.getenv("NODOX_KEY")
    
    # Si no está en env, intentar cargar desde archivo .env.local
    if not key and os.path.exists(".env.local"):
        try:
            with open(".env.local", "r") as f:
                for line in f:
                    if line.startswith("NODOX_KEY="):
                        key = line.split("=", 1)[1].strip()
                        break
        except Exception as e:
            logger.debug(f"No se pudo leer .env.local: {e}")

    if not key:
        error_msg = (
            "⚠️  No se encontró la variable de entorno NODOX_KEY.\n\n"
            "Soluciones:\n"
            "1. Generar clave: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\"\n"
            "2. Establecer variable:\n"
            "   - Linux/Mac: export NODOX_KEY='tu_clave_aqui'\n"
            "   - Windows (CMD): set NODOX_KEY=tu_clave_aqui\n"
            "   - Windows (PowerShell): $env:NODOX_KEY='tu_clave_aqui'\n"
            "3. O crear archivo .env.local con: NODOX_KEY=tu_clave_aqui"
        )
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

        with open(encrypted_path, "wb") as f:
            f.write(encrypted_data)

        os.remove(filepath)
        logger.debug(f"Archivo cifrado exitosamente: {filepath}")

        return True

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

