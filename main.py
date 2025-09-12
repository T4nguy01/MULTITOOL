import sys
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve

import pywinstyles
from config import APP_NAME, ICON_PATH

# Import des onglets
from tabs.accueil import AccueilTab
from tabs.reseaux_config import ReseauxTab
from tabs.reseaux_ping import ReseauxPingTab
from tabs.mikrotik import MikrotikTab
from tabs.parametres import ParametresTab
from tabs.rainbow import RainbowTab  # <-- Nouveau onglet Rainbow

class MainWindow(QMainWindow):
    def __init__(self, theme="light"):
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(ICON_PATH))
        self.resize(1000, 600)
        self.anim_duration = 250
        self.theme = theme  # light / dark

        # Layout principal
        central = QWidget()
        self.setCentralWidget(central)
        self.main_layout = QHBoxLayout()
        central.setLayout(self.main_layout)

        # Sidebar
        self.sidebar_container = QWidget()
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_container.setLayout(self.sidebar_layout)
        self.sidebar_container.setMaximumWidth(160)
        self.main_layout.addWidget(self.sidebar_container)

        # Boutons sidebar
        self.buttons_info = [
            ("Accueil", "resources/icons/home.svg"),
            ("Réseaux", "resources/icons/network.svg"),
            ("Ping", "resources/icons/ping.svg"),
            ("Mikrotik", "resources/icons/router.svg"),
            ("Rainbow", "resources/icons/rainbow.svg"),  # <-- Icône Rainbow
            ("Paramètres", "resources/icons/settings.svg")
        ]

        self.sidebar_buttons = []
        for text, icon_path in self.buttons_info:
            btn = QPushButton(text)
            btn.setFixedHeight(40)
            btn.setObjectName("sidebarButton")
            btn.setStyleSheet("text-align:left; padding-left:8px;")
            btn.setToolTip(text)  # Tooltip quand réduit
            self.sidebar_layout.addWidget(btn)
            self.sidebar_buttons.append(btn)

        self.sidebar_layout.addStretch()

        # Contenu onglets
        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack, 1)

        # Création onglets
        self.accueil_tab = AccueilTab()
        self.reseaux_tab = ReseauxTab()
        self.ping_tab = ReseauxPingTab()
        self.mikrotik_tab = MikrotikTab()
        self.rainbow_tab = RainbowTab()
        self.param_tab = ParametresTab(main_window=self)

        for widget in [self.accueil_tab, self.reseaux_tab, self.ping_tab, self.mikrotik_tab, self.rainbow_tab, self.param_tab]:
            self.stack.addWidget(widget)

        # Connexion boutons sidebar
        self.tab_map = {
            self.sidebar_buttons[0]: self.accueil_tab,
            self.sidebar_buttons[1]: self.reseaux_tab,
            self.sidebar_buttons[2]: self.ping_tab,
            self.sidebar_buttons[3]: self.mikrotik_tab,
            self.sidebar_buttons[4]: self.rainbow_tab,
            self.sidebar_buttons[5]: self.param_tab
        }
        for btn, tab in self.tab_map.items():
            btn.clicked.connect(lambda checked, t=tab: self.stack.setCurrentWidget(t))

        # Onglet par défaut
        self.stack.setCurrentWidget(self.accueil_tab)

        # Connexion interface sélectionnée (Reseaux → Ping)
        try:
            self.reseaux_tab.interface_changed.connect(self.ping_tab.set_default_host)
        except AttributeError:
            pass

        # Sidebar rétractable au hover
        self.sidebar_container.installEventFilter(self)

        # Appliquer les icônes selon le thème
        self.apply_sidebar_icons(self.theme)

    def apply_sidebar_icons(self, theme="light"):
        """Met les icônes adaptées au thème (light / dark)."""
        for btn, (text, icon_path) in zip(self.sidebar_buttons, self.buttons_info):
            base_name = os.path.splitext(os.path.basename(icon_path))[0]  # ex: home
            ext = os.path.splitext(icon_path)[1]  # .svg
            themed_icon_path = os.path.join("resources", "icons", f"{base_name}_{theme}{ext}")
            if os.path.exists(themed_icon_path):
                btn.setIcon(QIcon(themed_icon_path))
            else:
                btn.setIcon(QIcon(icon_path))  # fallback si pas de fichier

    def eventFilter(self, source, event):
        if source == self.sidebar_container:
            if event.type() == event.Type.Enter:
                self.animate_sidebar(160)
            elif event.type() == event.Type.Leave:
                self.animate_sidebar(50)
        return super().eventFilter(source, event)

    def animate_sidebar(self, width):
        self.anim = QPropertyAnimation(self.sidebar_container, b"maximumWidth")
        self.anim.setDuration(self.anim_duration)
        self.anim.setStartValue(self.sidebar_container.width())
        self.anim.setEndValue(width)
        self.anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.anim.start()

        for btn, (text, _) in zip(self.sidebar_buttons, self.buttons_info):
            if width > 60:
                btn.setText(text)
                btn.setStyleSheet("text-align:left; padding-left:8px;")
            else:
                btn.setText("")
                btn.setStyleSheet("text-align:center;")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    pywinstyles.apply_style(app, style="mica")

    # Charger QSS
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "styles", "style.qss")
    with open(qss_path, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    window = MainWindow(theme="light")  # ou "dark" si tu veux forcer
    window.show()
    sys.exit(app.exec())
