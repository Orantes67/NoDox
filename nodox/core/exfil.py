import time
import psutil
from nodox.core.logger import setup_logger

logger = setup_logger()

CHECK_INTERVAL = 5          # segundos
EXFIL_THRESHOLD_MB = 50     # MB enviados en el intervalo


def get_bytes_sent():
    counters = psutil.net_io_counters()
    return counters.bytes_sent


def monitor_exfiltration():
    logger.info("Iniciando monitoreo de exfiltración")

    try:
        last_bytes = get_bytes_sent()

        while True:
            time.sleep(CHECK_INTERVAL)

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
