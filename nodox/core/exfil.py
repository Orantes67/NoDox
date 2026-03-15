import time
import threading
import psutil
from nodox.core.logger import setup_logger

logger = setup_logger()

CHECK_INTERVAL = 5          # segundos
EXFIL_THRESHOLD_MB = 50     # MB enviados en el intervalo

# Evento global para señalizar parada
_stop_event = threading.Event()


def stop_exfil_monitor():
    """Señalizar al monitor que debe detenerse"""
    _stop_event.set()


def reset_exfil_monitor():
    """Reiniciar el evento de parada para nuevas ejecuciones"""
    _stop_event.clear()


def is_stopping():
    """Verificar si se ha solicitado parada"""
    return _stop_event.is_set()


def get_bytes_sent():
    try:
        counters = psutil.net_io_counters()
        return counters.bytes_sent
    except Exception as e:
        logger.error(f"Error al obtener contadores de red: {e}")
        return 0


def monitor_exfiltration():
    logger.info("Iniciando monitoreo de exfiltración")

    try:
        last_bytes = get_bytes_sent()

        while not is_stopping():
            # Usar wait con timeout para responder rápido a señales de parada
            _stop_event.wait(timeout=CHECK_INTERVAL)
            
            if is_stopping():
                break

            current_bytes = get_bytes_sent()
            diff = current_bytes - last_bytes

            mb_sent = diff / (1024 * 1024)

            if mb_sent > EXFIL_THRESHOLD_MB:
                logger.critical(
                    f"🚨 ALERTA DE EXFILTRACIÓN – Datos enviados: {mb_sent:.2f} MB en {CHECK_INTERVAL}s"
                )
                return

            logger.debug(
                f"Tráfico normal: {mb_sent:.2f} MB / {CHECK_INTERVAL}s"
            )

            last_bytes = current_bytes

    except Exception as e:
        logger.error(f"Error durante monitoreo de exfiltración: {e}")
    finally:
        logger.debug("Monitor de exfiltración detenido")
