import yaml
import os


def load_config(config_path=None):
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

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    return config
