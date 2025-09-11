# core/settings.py

class SETTINGS:
    # Paramètres utilisateurs
    theme = "Mica"             # "Mica", "Clair", "Sombre"
    auto_update = True
    notifications = True

    # Paramètres réseau
    ping_hosts = ["8.8.8.8", "1.1.1.1", "192.168.1.1", "google.com"]

    @classmethod
    def update(cls, theme=None, auto_update=None, notifications=None):
        if theme is not None:
            cls.theme = theme
        if auto_update is not None:
            cls.auto_update = auto_update
        if notifications is not None:
            cls.notifications = notifications
