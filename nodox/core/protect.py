import threading
import time

from nodox.core.logger import setup_logger
from nodox.core.config_loader import load_config
from nodox.core.scanner import scan_and_collect
from nodox.core.encryptor import encrypt_file_list
from nodox.core.canary import (
    setup_canary_files, 
    monitor_canary_files, 
    stop_monitors as stop_canary_monitors,
    reset_monitors as reset_canary_monitors
)
from nodox.core.exfil import (
    monitor_exfiltration, 
    stop_exfil_monitor,
    reset_exfil_monitor
)

logger = setup_logger()


def protect():
    try:
        logger.info("===== MODO PROTECT ACTIVADO =====")

        # Reiniciar estados de monitores
        reset_canary_monitors()
        reset_exfil_monitor()

        config = load_config()

        paths = config.get("paths", {})
        scan_path = paths.get("scan_path", ".")
        encrypt_path = paths.get("encrypt_path", ".")
        canary_path = paths.get("canary_path", ".")

        # 1. Scan
        logger.info("Escaneando datos sensibles...")
        sensitive_files = scan_and_collect(scan_path)

        # 2. Encrypt
        logger.info("Cifrando datos sensibles...")
        encrypt_file_list(sensitive_files)

        # 3. Canary setup
        logger.info("Configurando canary files...")
        canary_state = setup_canary_files(canary_path)

        if not canary_state:
            logger.warning("No hay canary files configurados")

        # 4. Start monitors
        logger.info("Iniciando monitoreo continuo...")

        # Solo crear threads si hay canary files
        threads = []
        
        if canary_state:
            canary_thread = threading.Thread(
                target=monitor_canary_files,
                args=(canary_state,),
                daemon=False,
                name="CanaryMonitor"
            )
            threads.append(canary_thread)
            canary_thread.start()

        exfil_thread = threading.Thread(
            target=monitor_exfiltration,
            daemon=False,
            name="ExfilMonitor"
        )
        threads.append(exfil_thread)
        exfil_thread.start()

        logger.info("🛡️  Protección activa - Monitoreo continuo en ejecución")
        logger.info("Presiona Ctrl+C para detener")

        try:
            # Mantener el programa corriendo
            while threads:
                # Verificar si algún thread ha terminado
                threads = [t for t in threads if t.is_alive()]
                if threads:
                    time.sleep(1)
                else:
                    break
        except KeyboardInterrupt:
            logger.info("⏹️  Deteniendo NoDox...")
            
            # Señalizar a todos los monitores que deben detenerse
            stop_canary_monitors()
            stop_exfil_monitor()
            
            logger.info("Esperando threads...")
            
            # Esperar a que los threads terminen (máximo 5 segundos cada uno)
            for thread in threads:
                thread.join(timeout=5)
                if thread.is_alive():
                    logger.warning(f"Thread {thread.name} no terminó a tiempo")
            
            logger.info("✅ NoDox finalizado.")

    except RuntimeError as e:
        logger.error(f"Error de configuración: {e}")
        logger.info("Para usar protect necesitas configurar NODOX_KEY")
    except Exception as e:
        logger.error(f"Error crítico en modo PROTECT: {e}")
        raise
