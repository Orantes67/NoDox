import yaml
import os

# Cache global de configuración
_config_cache = None


def load_config(config_path=None, force_reload=False):
    """
    Cargar configuración desde archivo YAML.
    Usa cache para evitar lecturas repetidas.
    """
    global _config_cache
    
    if _config_cache is not None and not force_reload and config_path is None:
        return _config_cache
    
    if config_path is None:
        # Buscar en varias ubicaciones posibles
        possible_paths = [
            "nodox/config/nodox.yaml",
            "config/nodox.yaml",
            os.path.join(os.path.dirname(__file__), "..", "config", "nodox.yaml"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                config_path = path
                break
        else:
            raise FileNotFoundError(
                "No se encontró el archivo de configuración: nodox.yaml\n"
                "Busqué en: " + ", ".join(possible_paths)
            )
    
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"No se encontró el archivo de configuración: {config_path}"
        )

    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    _config_cache = config
    return config


def get_scanner_config():
    """Obtener configuración del scanner"""
    config = load_config()
    return config.get("scanner", {})


def get_encryptor_config():
    """Obtener configuración del encryptor"""
    config = load_config()
    return config.get("encryptor", {})


def get_canary_config():
    """Obtener configuración de canary files"""
    config = load_config()
    return config.get("canary", {})


def get_exfil_config():
    """Obtener configuración de detección de exfiltración"""
    config = load_config()
    return config.get("exfiltration", {})


def get_paths_config():
    """Obtener configuración de paths"""
    config = load_config()
    return config.get("paths", {})


def get_logging_config():
    """Obtener configuración de logging"""
    config = load_config()
    return config.get("logging", {})
