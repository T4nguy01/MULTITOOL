from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton
from core.settings import SETTINGS
import pywinstyles

class ParametresTab(QWidget):
    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # main_window doit avoir l'attribut app

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Paramètres de l'application"))

        # Choix du thème
        layout.addWidget(QLabel("Thème de l'application"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Mica", "Clair", "Sombre"])
        self.theme_combo.setCurrentText(SETTINGS.theme)
        layout.addWidget(self.theme_combo)

        # Mise à jour automatique
        self.auto_update_cb = QCheckBox("Activer les mises à jour automatiques")
        self.auto_update_cb.setChecked(SETTINGS.auto_update)
        layout.addWidget(self.auto_update_cb)

        # Notifications
        self.notifications_cb = QCheckBox("Activer les notifications")
        self.notifications_cb.setChecked(SETTINGS.notifications)
        layout.addWidget(self.notifications_cb)

        # Bouton pour sauvegarder et appliquer les paramètres
        self.save_btn = QPushButton("Sauvegarder et appliquer")
        self.save_btn.clicked.connect(self.save_settings)
        layout.addWidget(self.save_btn)

        layout.addStretch()
        self.setLayout(layout)

    def save_settings(self):
        # Mise à jour des settings
        SETTINGS.update(
            theme=self.theme_combo.currentText(),
            auto_update=self.auto_update_cb.isChecked(),
            notifications=self.notifications_cb.isChecked()
        )

        print(f"Paramètres mis à jour : {SETTINGS.theme}, {SETTINGS.auto_update}, {SETTINGS.notifications}")

        # Appliquer immédiatement le thème
        if self.main_window and hasattr(self.main_window, "app"):
            style_name = SETTINGS.theme.lower()  # "mica", "clair", "sombre"
            try:
                pywinstyles.apply_style(self.main_window.app, style=style_name)
            except Exception as e:
                print(f"Erreur lors de l'application du style : {e}")
