import os
import time
import hashlib
from nodox.core.logger import setup_logger

logger = setup_logger()

CANARY_DIR = ".nodox_canary"
CHECK_INTERVAL = 5  # segundos

CANARY_FILES = [
    "clientes_2025_CONFIDENCIAL.xlsx",
    "passwords_admin.txt",
    "contratos_privados.docx",
    "backup_db.sql",
]


def hash_file(filepath):
    h = hashlib.sha256()

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)

    return h.hexdigest()


def setup_canary_files(base_path):
    logger.info("Creando canary files")

    try:
        canary_path = os.path.join(base_path, CANARY_DIR)
        os.makedirs(canary_path, exist_ok=True)

        canary_state = {}

        for filename in CANARY_FILES:
            filepath = os.path.join(canary_path, filename)

            if not os.path.exists(filepath):
                with open(filepath, "w") as f:
                    f.write("CONFIDENTIAL\nDO NOT ACCESS\n")

            canary_state[filepath] = hash_file(filepath)
            logger.warning(f"Canary file creado: {filepath}")

        logger.info(f"Total de canary files configurados: {len(canary_state)}")
        return canary_state

    except Exception as e:
        logger.error(f"Error al crear canary files: {e}")
        return {}


def monitor_canary_files(canary_state):
    logger.info("Monitoreando canary files...")

    try:
        while True:
            for filepath, original_hash in canary_state.items():

                if not os.path.exists(filepath):
                    logger.critical(f"🚨 CANARY FILE ACTIVADO – ARCHIVO ELIMINADO: {filepath}")
                    return

                current_hash = hash_file(filepath)

                if current_hash != original_hash:
                    logger.critical(f"🚨 CANARY FILE ACTIVADO – ARCHIVO MODIFICADO: {filepath}")
                    return

            time.sleep(CHECK_INTERVAL)

    except Exception as e:
        logger.error(f"Error durante monitoreo de canary files: {e}")


def setup_canary(setup, base_path="."):
    if setup:
        logger.info("Inicializando sistema de canary files")
        state = setup_canary_files(base_path)
        if state:
            monitor_canary_files(state)
    else:
        logger.warning("Canary files no activados. Usa --setup para habilitar")
