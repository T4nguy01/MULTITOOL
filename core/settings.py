# core/settings.py

class SETTINGS:
    # Paramètres utilisateurs
    theme = "Mica"             # "Mica", "Clair", "Sombre"
    auto_update = True
    notifications = True

    # Paramètres réseau
    ping_hosts = [
        {"name": "Google", "host": "8.8.8.8"},
        {"name": "OXO", "host": "192.168.1.246"},
        {"name": "MYOPENIP", "host": "94.143.87.70"},
        {"name": "CONVERGENCE", "host": "91.211.64.225"}
    ]

    @classmethod
    def update(cls, theme=None, auto_update=None, notifications=None):
        if theme is not None:
            cls.theme = theme
        if auto_update is not None:
            cls.auto_update = auto_update
        if notifications is not None:
            cls.notifications = notifications
