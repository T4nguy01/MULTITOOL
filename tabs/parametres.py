from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
                             QPushButton, QMessageBox, QGroupBox, QSpinBox,
                             QSlider, QProgressBar, QFrame, QSizePolicy)
from PyQt6.QtCore import pyqtSignal, QThread, Qt, QSettings
from PyQt6.QtGui import QFont
from core.settings import SETTINGS
import subprocess

# Import pywinstyles uniquement si Mica est utilisé
try:
    import pywinstyles
except ImportError:
    pywinstyles = None


class GitUpdateThread(QThread):
    """Thread pour les mises à jour Git en arrière-plan"""
    update_finished = pyqtSignal(bool, str)
    progress_updated = pyqtSignal(int)

    EXPECTED_REMOTE = "github.com/T4nguy01/MULTITOOL"

    def run(self):
        try:
            remote = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True, text=True, timeout=10
            ).stdout.strip()
            if self.EXPECTED_REMOTE.lower() not in remote.lower() or not remote.startswith("https://"):
                self.update_finished.emit(False, f"Dépôt distant non autorisé : {remote!r}")
                return
            self.progress_updated.emit(25)
            result_fetch = subprocess.run(
                ["git", "fetch"],
                capture_output=True, text=True, timeout=30
            )

            self.progress_updated.emit(50)
            result_status = subprocess.run(
                ["git", "status", "-uno"],
                capture_output=True, text=True, timeout=15
            )

            self.progress_updated.emit(75)
            if "Your branch is behind" in result_status.stdout:
                result_pull = subprocess.run(
                    ["git", "pull", "--ff-only", "origin", "main"],
                    capture_output=True, text=True, timeout=60
                )
                self.progress_updated.emit(100)
                if result_pull.returncode == 0:
                    self.update_finished.emit(True, f"Mise à jour réussie :\n{result_pull.stdout}")
                else:
                    self.update_finished.emit(False, f"Erreur lors de la mise à jour :\n{result_pull.stderr}")
            else:
                self.progress_updated.emit(100)
                self.update_finished.emit(True, "L'application est déjà à jour.")

        except subprocess.TimeoutExpired:
            self.update_finished.emit(False, "Timeout : La mise à jour a pris trop de temps.")
        except Exception as e:
            self.update_finished.emit(False, f"Erreur inattendue : {str(e)}")


class ParametresTab(QWidget):
    settings_changed = pyqtSignal()

    def __init__(self, main_window=None):
        super().__init__()
        self.main_window = main_window
        self.update_thread = None
        self.init_ui()
        self.load_current_settings()

    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout()

        # Titre principal
        title = QLabel("⚙️ Paramètres")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Groupe Apparence
        self.create_appearance_group(layout)

        # ❌ Groupe Général supprimé

        # Groupe Actions
        self.create_actions_group(layout)

        layout.addStretch()
        self.setLayout(layout)

    def create_appearance_group(self, parent_layout):
        """Crée le groupe des paramètres d'apparence"""
        group = QGroupBox("🎨 Apparence")
        layout = QVBoxLayout()

        # Thème
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Thème :"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Mica", "Clair", "Sombre"])
        self.theme_combo.currentTextChanged.connect(self.on_theme_preview)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)

        # Taille de police
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Taille de police :"))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(9, 16)
        self.font_size_spin.setValue(10)
        self.font_size_spin.setSuffix(" pt")
        font_layout.addWidget(self.font_size_spin)
        font_layout.addStretch()
        layout.addLayout(font_layout)

        # Opacité (Mica uniquement)
        opacity_layout = QHBoxLayout()
        self.opacity_label = QLabel("Transparence :")
        opacity_layout.addWidget(self.opacity_label)
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(80, 100)
        self.opacity_slider.setValue(95)
        self.opacity_value_label = QLabel("95%")
        self.opacity_slider.valueChanged.connect(
            lambda v: self.opacity_value_label.setText(f"{v}%")
        )
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_value_label)
        layout.addLayout(opacity_layout)

        self.update_opacity_visibility()
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def create_actions_group(self, parent_layout):
        """Crée le groupe des actions"""
        group = QGroupBox("🎯 Actions")
        layout = QVBoxLayout()

        buttons_layout1 = QHBoxLayout()

        # Appliquer
        self.apply_btn = QPushButton("✨ Appliquer")
        self.apply_btn.clicked.connect(self.apply_settings)
        self.apply_btn.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; padding: 8px 16px; }")
        buttons_layout1.addWidget(self.apply_btn)

        # Sauvegarder
        self.save_btn = QPushButton("💾 Sauvegarder")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("QPushButton { background-color: #2196F3; color: white; font-weight: bold; padding: 8px 16px; }")
        buttons_layout1.addWidget(self.save_btn)

        # Réinitialiser
        self.reset_btn = QPushButton("🔄 Réinitialiser")
        self.reset_btn.clicked.connect(self.reset_settings)
        self.reset_btn.setStyleSheet("QPushButton { padding: 8px 16px; }")
        buttons_layout1.addWidget(self.reset_btn)

        layout.addLayout(buttons_layout1)

        # Séparateur
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Mise à jour
        update_layout = QVBoxLayout()
        update_buttons = QHBoxLayout()

        self.update_btn = QPushButton("🔄 Vérifier les mises à jour")
        self.update_btn.clicked.connect(self.update_app)
        self.update_btn.setStyleSheet("QPushButton { background-color: #FF9800; color: white; font-weight: bold; padding: 8px 16px; }")
        update_buttons.addWidget(self.update_btn)

        update_layout.addLayout(update_buttons)

        self.update_progress = QProgressBar()
        self.update_progress.setVisible(False)
        self.update_progress.setStyleSheet("QProgressBar { text-align: center; }")
        update_layout.addWidget(self.update_progress)

        layout.addLayout(update_layout)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def load_current_settings(self):
        """Charge les paramètres actuels"""
        try:
            self.theme_combo.setCurrentText(SETTINGS.theme)
            settings = QSettings()
            self.font_size_spin.setValue(settings.value("font_size", 10, int))
            self.opacity_slider.setValue(settings.value("opacity", 95, int))
            self.opacity_value_label.setText(f"{self.opacity_slider.value()}%")
        except Exception as e:
            print(f"Erreur lors du chargement des paramètres : {e}")

    def on_theme_preview(self):
        self.update_opacity_visibility()

    def update_opacity_visibility(self):
        is_mica = self.theme_combo.currentText() == "Mica"
        self.opacity_label.setVisible(is_mica)
        self.opacity_slider.setVisible(is_mica)
        self.opacity_value_label.setVisible(is_mica)

    def apply_theme(self):
        theme = self.theme_combo.currentText().lower()
        opacity = self.opacity_slider.value() / 100.0

        if theme == "mica" and pywinstyles and self.main_window:
            self.main_window.setStyleSheet("")
            try:
                pywinstyles.apply_style(self.main_window, style="mica")
                self.main_window.setWindowOpacity(opacity)
            except Exception as e:
                print("Erreur pywinstyles Mica:", e)
            return

        try:
            with open("style.qss", "r", encoding="utf-8") as f:
                qss = f.read()
        except Exception as e:
            print("Impossible de lire style.qss :", e)
            return

        if self.main_window:
            if theme == "clair":
                self.main_window.setStyleSheet(".light " + qss)
            else:
                self.main_window.setStyleSheet(qss)

            if theme == "mica":
                self.main_window.setWindowOpacity(opacity)
            else:
                self.main_window.setWindowOpacity(1.0)

    def apply_settings(self):
        try:
            self.apply_theme()
            self.settings_changed.emit()
            QMessageBox.information(self, "✅ Paramètres", "Paramètres appliqués avec succès !")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur lors de l'application :\n{str(e)}")

    def save_settings(self):
        try:
            SETTINGS.update(theme=self.theme_combo.currentText())
            settings = QSettings()
            settings.setValue("font_size", self.font_size_spin.value())
            settings.setValue("opacity", self.opacity_slider.value())
            self.apply_theme()
            self.settings_changed.emit()
            QMessageBox.information(self, "✅ Paramètres", "Paramètres sauvegardés et appliqués !")
        except Exception as e:
            QMessageBox.critical(self, "❌ Erreur", f"Erreur lors de la sauvegarde :\n{str(e)}")

    def reset_settings(self):
        reply = QMessageBox.question(self, "🔄 Réinitialiser",
                                   "Réinitialiser tous les paramètres aux valeurs par défaut ?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            self.theme_combo.setCurrentText("Mica")
            self.font_size_spin.setValue(10)
            self.opacity_slider.setValue(95)
            self.opacity_value_label.setText("95%")
            self.update_opacity_visibility()
            QMessageBox.information(self, "✅ Réinitialisation",
                                  "Paramètres réinitialisés ! Cliquez sur 'Appliquer' ou 'Sauvegarder'.")

    def update_app(self):
        if self.update_thread and self.update_thread.isRunning():
            QMessageBox.information(self, "ℹ️ Mise à jour", "Une vérification est déjà en cours...")
            return

        self.update_btn.setEnabled(False)
        self.update_btn.setText("🔄 Vérification en cours...")
        self.update_progress.setVisible(True)
        self.update_progress.setValue(0)

        self.update_thread = GitUpdateThread()
        self.update_thread.update_finished.connect(self.on_update_finished)
        self.update_thread.progress_updated.connect(self.update_progress.setValue)
        self.update_thread.start()

    def on_update_finished(self, success, message):
        self.update_btn.setEnabled(True)
        self.update_btn.setText("🔄 Vérifier les mises à jour")
        self.update_progress.setVisible(False)

        if success:
            if "déjà à jour" in message:
                QMessageBox.information(self, "ℹ️ Mise à jour", message)
            else:
                QMessageBox.information(self, "✅ Mise à jour",
                                      message + "\n\nRedémarrez l'application pour appliquer les changements.")
        else:
            QMessageBox.warning(self, "⚠️ Mise à jour", message)
