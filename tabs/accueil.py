import sys
import os
import requests
import psutil
import platform
from datetime import datetime
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QGroupBox, QFrame, QScrollArea
)

# Thread pour charger les commits GitHub
class CommitsThread(QThread):
    commits_loaded = pyqtSignal(list)

    def run(self):
        try:
            url = "https://api.github.com/repos/T4nguy01/Multitool/commits"
            response = requests.get(url)
            if response.status_code == 200:
                commits = response.json()[:3]  # 3 derniers commits
                self.commits_loaded.emit(commits)
            else:
                self.commits_loaded.emit([])
        except Exception:
            self.commits_loaded.emit([])


# Onglet d'accueil
class AccueilTab(QWidget):
    def __init__(self):
        super().__init__()
        self.version = self.load_version()
        self.init_ui()

    def load_version(self):
        """Lit la version depuis version.txt"""
        try:
            if os.path.exists("version.txt"):
                with open("version.txt", "r", encoding="utf-8") as f:
                    return f.read().strip()
        except Exception:
            pass
        return "?.?.?"  # Valeur par défaut si fichier absent

    def init_ui(self):
        # Scroll principal pour rendre la page responsive
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        container = QWidget()
        layout = QVBoxLayout(container)

        # Header
        header = self.create_header()
        layout.addWidget(header)

        # Contenu principal
        content_layout = QHBoxLayout()

        # Colonne gauche (vide mais garde la structure)
        left_column = QVBoxLayout()
        left_column.addStretch()
        content_layout.addLayout(left_column, 1)

        # Colonne centrale - Commits
        center_column = QVBoxLayout()
        commits_group = QGroupBox("🕒 Derniers commits GitHub")
        commits_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #333;
                border: 2px solid #0078D7;
                border-radius: 10px;
                margin-top: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.commits_layout = QVBoxLayout()
        commits_group.setLayout(self.commits_layout)
        center_column.addWidget(commits_group)
        content_layout.addLayout(center_column, 2)

        # Colonne droite - Infos système
        right_column = self.create_info_section()
        content_layout.addLayout(right_column, 1)

        layout.addLayout(content_layout)

        # Charger commits
        self.load_commits()

        scroll.setWidget(container)

        # Layout final
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll)

    def create_header(self):
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: #0078D7;
                padding: 10px;
            }
        """)
        header_layout = QHBoxLayout(frame)

        # Logo
        logo_label = QLabel()
        pixmap = QPixmap("logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio))
        header_layout.addWidget(logo_label)

        # Titre
        title = QLabel("MULTITOOL - Tableau de bord")
        title.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        header_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignLeft)

        # Version depuis version.txt
        version_label = QLabel(f"📦 v{self.version}")
        version_label.setFont(QFont("Arial", 12))
        version_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(version_label, alignment=Qt.AlignmentFlag.AlignRight)

        # Horloge
        self.clock_label = QLabel()
        self.clock_label.setFont(QFont("Arial", 12))
        self.clock_label.setStyleSheet("color: white;")
        header_layout.addWidget(self.clock_label, alignment=Qt.AlignmentFlag.AlignRight)

        timer = QTimer(self)
        timer.timeout.connect(self.update_clock)
        timer.start(1000)
        self.update_clock()

        # État système
        status_label = QLabel("✅ Système opérationnel")
        status_label.setStyleSheet("color: white; font-weight: bold;")
        header_layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignRight)

        return frame

    def create_info_section(self):
        layout = QVBoxLayout()

        # Infos système
        system_group = QGroupBox("💻 Infos système")
        system_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                color: #333;
                border: 2px solid #28A745;
                border-radius: 10px;
                margin-top: 10px;
                background-color: #f9f9f9;
            }
        """)

        sys_layout = QVBoxLayout()

        os_label = QLabel(f"OS : {platform.system()} {platform.release()}")
        sys_layout.addWidget(os_label)

        ram = psutil.virtual_memory()
        ram_label = QLabel(f"RAM : {ram.used // (1024 ** 3)} Go / {ram.total // (1024 ** 3)} Go")
        sys_layout.addWidget(ram_label)

        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_label = QLabel(f"CPU : {cpu_usage}%")
        sys_layout.addWidget(cpu_label)

        system_group.setLayout(sys_layout)
        layout.addWidget(system_group)

        return layout

    def load_commits(self):
        self.commits_thread = CommitsThread()
        self.commits_thread.commits_loaded.connect(self.display_commits)
        self.commits_thread.start()

    def display_commits(self, commits):
        for i in reversed(range(self.commits_layout.count())):
            item = self.commits_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        if not commits:
            self.commits_layout.addWidget(QLabel("⚠️ Impossible de charger les commits"))
            return

        for commit in commits:
            message = commit["commit"]["message"]
            author = commit["commit"]["author"]["name"]
            date_str = commit["commit"]["author"]["date"]
            date = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")

            commit_frame = QFrame()
            commit_layout = QVBoxLayout()

            commit_msg = QLabel(f"🔹 {message}")
            commit_msg.setStyleSheet("font-weight: bold; color: #0078D7;")
            commit_layout.addWidget(commit_msg)

            commit_info = QLabel(f"✍️ {author} - {date.strftime('%d/%m/%Y %H:%M')}")
            commit_info.setStyleSheet("color: #555;")
            commit_layout.addWidget(commit_info)

            commit_frame.setLayout(commit_layout)
            commit_frame.setStyleSheet("""
                QFrame {
                    background-color: #ffffff;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 5px;
                }
            """)

            self.commits_layout.addWidget(commit_frame)

    def update_clock(self):
        now = datetime.now().strftime("%H:%M:%S")
        self.clock_label.setText(f"🕒 {now}")


# Lancer l'application en test
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AccueilTab()
    window.setWindowTitle("MULTITOOL - Accueil")
    window.resize(1000, 600)
    window.show()
    sys.exit(app.exec())
