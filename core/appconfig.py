"""Charge config.py (privé, non versionné) ou, à défaut, des valeurs par défaut."""
try:
    from config import APP_NAME, ICON_PATH, MIKROTIK_BASE_CONFIG
except ImportError:
    APP_NAME = "MultiTool"
    ICON_PATH = "resources/icons/icon.ico"
    MIKROTIK_BASE_CONFIG = "# config.py absent : copier config.exemple.py en config.py\n"

try:
    from config import PING_HOSTS
except ImportError:
    PING_HOSTS = [{"name": "Google", "host": "8.8.8.8"}]
