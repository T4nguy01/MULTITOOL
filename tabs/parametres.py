from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QCheckBox, QComboBox, QPushButton, QMessageBox
from PyQt6.QtCore import pyqtSignal
from core.settings import SETTINGS
import subprocess

# Import pywinstyles uniquement si Mica est utilisé
try:
    import pywinstyles
except ImportError:
    pywinstyles = None

class ParametresTab(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window  # doit être le QMainWindow principal

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

        # Bouton pour mise à jour Git
        self.update_btn = QPushButton("Mettre à jour l'application")
        self.update_btn.clicked.connect(self.update_app)
        layout.addWidget(self.update_btn)

        layout.addStretch()
        self.setLayout(layout)

    def apply_theme(self):
        """Applique le thème selon le QSS et pywinstyles"""
        theme = SETTINGS.theme.lower()  # "mica", "clair", "sombre"

        if theme == "mica" and pywinstyles:
            # Supprime le QSS et applique le style natif Windows
            if self.main_window:
                self.main_window.setStyleSheet("")
                try:
                    pywinstyles.apply_style(self.main_window, style="mica")
                except Exception as e:
                    print("Erreur pywinstyles Mica:", e)
            return

        # Sinon on applique le QSS
        try:
            with open("style.qss", "r", encoding="utf-8") as f:
                qss = f.read()
        except Exception as e:
            print("Impossible de lire style.qss :", e)
            return

        if theme == "clair":
            # Ajoute le préfixe .light pour activer le thème clair
            if self.main_window:
                self.main_window.setStyleSheet(".light " + qss)
        else:  # sombre
            if self.main_window:
                self.main_window.setStyleSheet(qss)

    def save_settings(self):
        # Mise à jour des settings
        SETTINGS.update(
            theme=self.theme_combo.currentText(),
            auto_update=self.auto_update_cb.isChecked(),
            notifications=self.notifications_cb.isChecked()
        )

        # Appliquer le thème immédiatement
        self.apply_theme()

        # Émettre le signal pour le main_window
        self.settings_changed.emit()

        # Feedback utilisateur
        QMessageBox.information(self, "Paramètres", "Paramètres sauvegardés et appliqués.")

    def update_app(self):
        """Exécute un git pull pour mettre à jour l'application."""
        try:
            result = subprocess.run(
                ["git", "pull", "origin", "main"],
                capture_output=True, text=True, check=True
            )
            QMessageBox.information(self, "Mise à jour", f"Mise à jour effectuée :\n{result.stdout}")
        except subprocess.CalledProcessError as e:
            QMessageBox.warning(self, "Mise à jour", f"Erreur lors de la mise à jour :\n{e.stderr}")
