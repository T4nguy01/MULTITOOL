APP_NAME = "MultiTool"
APP_VERSION = "1.0.0"

# Ressources
ICON_PATH = "resources/icons/icon.ico"

# Options par défaut
DEFAULT_WINDOW_SIZE = (1000, 600)

# Exemple de configuration Mikrotik (⚠️ à remplacer par config.py local)
MIKROTIK_BASE_CONFIG = """
# Exemple : à remplacer par ta configuration réelle
/user add name=admin password=changeme group=full
/ip service set [find] address=192.168.0.0/24
"""
