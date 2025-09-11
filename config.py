# config.py

# Informations générales
APP_NAME = "MultiTool"
APP_VERSION = "BETA 1.2"

# Ressources
ICON_PATH = "resources/icons/icon.ico"

# Options par défaut
DEFAULT_WINDOW_SIZE = (1000, 600)

# ==========================
# ⚙️ Configuration Mikrotik
# ==========================

# Configuration de base du routeur (⚠️ infos sensibles → ajouter config.py au .gitignore)
MIKROTIK_BASE_CONFIG = (
    "/user add name=adminATE password=f6z87BeCkSFUPgBJQQSBMK7gjhUNJb6553qqTku7SxcEf98BvBeCbX5b2kc5v8uvur84SetRy3cTLmTFdrntpFhZrMqFyeDhhQbUuRgN6pnjbWrvfBueSu6QiLgSmeqb group=full\n"
    "/ip service set [find] address=91.211.65.5/32,91.211.65.106/32,91.211.64.0/24,100.127.0.0.0/16,91.211.65.102/32,192.168.0.0/16,10.0.0.0/8,172.16.0.0/12,192.168.1.0/24,45.93.147.172/32,212.234.112.17/32,91.211.64.150/32\n"
    "/ip firewall nat add action=dst-nat chain=dstnat dst-port=16853 protocol=tcp to-addresses=192.168.92.246 to-ports=50443 src-address-list=ATE comment=ATE\n"
    "/ip firewall address-list add address=45.93.147.172-212.234.112.17 list=ATE\n"
    "/ip firewall nat add chain=dstnat action=dst-nat to-addresses=192.168.92.246 to-ports=5060 protocol=udp src-address=91.211.64.225 dst-port=5060 log=no\n"
)
