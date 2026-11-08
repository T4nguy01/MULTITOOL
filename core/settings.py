# core/settings.py
from core.appconfig import PING_HOSTS

class SETTINGS:
    # Paramètres utilisateurs
    theme = "Mica"             # "Mica", "Clair", "Sombre"
    auto_update = True
    notifications = True

    # Paramètres réseau
    ping_hosts = PING_HOSTS  # défini dans config.py (privé)

    @classmethod
    def update(cls, theme=None, auto_update=None, notifications=None):
        if theme is not None:
            cls.theme = theme
        if auto_update is not None:
            cls.auto_update = auto_update
        if notifications is not None:
            cls.notifications = notifications
