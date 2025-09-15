from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QFrame
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtCore import Qt
import requests
import os

class AccueilTab(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # Header logo / titre / version
        header = QVBoxLayout()
        logo_label = QLabel()
        logo_pixmap = QPixmap(os.path.join("resources", "icons", "icon.ico")).scaled(
            60, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("MultiTool")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Lire version depuis version.txt
        version = "v?.?.?"  # fallback si fichier manquant
        version_file = os.path.join(os.path.dirname(__file__), "..", "version.txt")
        try:
            with open(version_file, "r", encoding="utf-8") as f:
                version = f.read().strip()
        except FileNotFoundError:
            pass

        version_label = QLabel(version)
        version_label.setFont(QFont("Segoe UI", 10))
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        header.addWidget(logo_label)
        header.addWidget(title_label)
        header.addWidget(version_label)
        layout.addLayout(header)

        # Scroll area pour les nouveautés (commits)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setSpacing(15)
        scroll_content.setLayout(scroll_layout)

        # Récupérer les 4 derniers commits
        commits = self.get_latest_commits("T4nguy01", "MULTITOOL", count=4)

        for item in commits:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.05);
                    border-radius: 8px;
                    padding: 10px;
                }
            """)
            label = QLabel(item)
            label.setWordWrap(True)
            label.setFont(QFont("Segoe UI", 11))
            frame_layout = QVBoxLayout()
            frame_layout.addWidget(label)
            frame.setLayout(frame_layout)
            scroll_layout.addWidget(frame)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        self.setLayout(layout)

    def get_latest_commits(self, owner, repo, count=4):
        """Récupère les derniers commits d’un repo GitHub public."""
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            commits = []
            for commit in data[:count]:
                message = commit["commit"]["message"]
                author = commit["commit"]["author"]["name"]
                date = commit["commit"]["author"]["date"][:10]  # YYYY-MM-DD
                commits.append(f"{date} - {author}: {message}")
            return commits
        except requests.RequestException:
            return ["⚠️ Impossible de récupérer les commits GitHub. Vérifiez votre connexion internet."]
