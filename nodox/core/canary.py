import os
import time
import hashlib
import threading
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

# Evento global para señalizar parada de threads
_stop_event = threading.Event()


def stop_monitors():
    """Señalizar a todos los monitores que deben detenerse"""
    _stop_event.set()


def reset_monitors():
    """Reiniciar el evento de parada para nuevas ejecuciones"""
    _stop_event.clear()


def is_stopping():
    """Verificar si se ha solicitado parada"""
    return _stop_event.is_set()


def hash_file(filepath):
    h = hashlib.sha256()

    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
    except IOError as e:
        logger.error(f"Error al calcular hash de {filepath}: {e}")
        return None

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

            file_hash = hash_file(filepath)
            if file_hash:
                canary_state[filepath] = file_hash
                logger.warning(f"Canary file creado: {filepath}")

        logger.info(f"Total de canary files configurados: {len(canary_state)}")
        return canary_state

    except Exception as e:
        logger.error(f"Error al crear canary files: {e}")
        return {}


def monitor_canary_files(canary_state):
    logger.info("Monitoreando canary files...")

    try:
        while not is_stopping():
            for filepath, original_hash in canary_state.items():
                if is_stopping():
                    break

                if not os.path.exists(filepath):
                    logger.critical(f"🚨 CANARY FILE ACTIVADO – ARCHIVO ELIMINADO: {filepath}")
                    return

                current_hash = hash_file(filepath)
                
                if current_hash is None:
                    logger.warning(f"No se pudo verificar canary file: {filepath}")
                    continue

                if current_hash != original_hash:
                    logger.critical(f"🚨 CANARY FILE ACTIVADO – ARCHIVO MODIFICADO: {filepath}")
                    return

            # Usar wait con timeout para responder rápido a señales de parada
            _stop_event.wait(timeout=CHECK_INTERVAL)

    except Exception as e:
        logger.error(f"Error durante monitoreo de canary files: {e}")
    finally:
        logger.debug("Monitor de canary files detenido")


def setup_canary(setup, base_path="."):
    reset_monitors()  # Asegurar estado limpio
    if setup:
        logger.info("Inicializando sistema de canary files")
        state = setup_canary_files(base_path)
        if state:
            monitor_canary_files(state)
    else:
        logger.warning("Canary files no activados. Usa --setup para habilitar")
