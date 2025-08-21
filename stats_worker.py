from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QProgressBar, QFrame, QPushButton
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
import psutil
from utils.helper import format_bytes

class StatsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
            QWidget {background-color: #181818; border-radius: 16px;}
            QLabel {font-family: 'Segoe UI', Arial, sans-serif;}
            QPushButton {font-size:16px;}
        """)
        layout = QVBoxLayout(self)
        title = QLabel("📊 Statistiques Système")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color:#0078D7; margin-bottom:20px;")
        layout.addWidget(title)

        grid = QGridLayout()
        label_style = "font-size:18px; color:#0078D7; font-weight:bold;"
        value_style = "font-size:18px; color:white;"

        # CPU
        self.cpu_label = QLabel("🖥️ CPU :")
        self.cpu_label.setStyleSheet(label_style)
        self.cpu_label.setToolTip("Pourcentage d'utilisation du processeur")
        self.cpu_value = QLabel("")
        self.cpu_value.setStyleSheet(value_style)
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setMaximum(100)
        self.cpu_bar.setStyleSheet("QProgressBar {height:18px; border-radius:8px;} QProgressBar::chunk {background-color:#0078D7;}")

        # Cœurs CPU
        self.cpu_cores_label = QLabel("Cœurs CPU :")
        self.cpu_cores_label.setStyleSheet(label_style)
        self.cpu_cores_label.setToolTip("Nombre total de cœurs logiques du CPU")
        self.cpu_cores_value = QLabel("")
        self.cpu_cores_value.setStyleSheet(value_style)

        # RAM
        self.ram_label = QLabel("💾 RAM :")
        self.ram_label.setStyleSheet(label_style)
        self.ram_label.setToolTip("Pourcentage et quantité de mémoire vive utilisée")
        self.ram_value = QLabel("")
        self.ram_value.setStyleSheet(value_style)
        self.ram_bar = QProgressBar()
        self.ram_bar.setMaximum(100)
        self.ram_bar.setStyleSheet("QProgressBar {height:18px; border-radius:8px;} QProgressBar::chunk {background-color:#28a745;}")

        # Disque
        self.disk_label = QLabel("🗄️ Disque :")
        self.disk_label.setStyleSheet(label_style)
        self.disk_label.setToolTip("Utilisation du disque principal")
        self.disk_value = QLabel("")
        self.disk_value.setStyleSheet(value_style)

        # Réseau
        self.net_label = QLabel("🌐 Réseau :")
        self.net_label.setStyleSheet(label_style)
        self.net_label.setToolTip("Débit réseau entrant et sortant")
        self.net_value = QLabel("")
        self.net_value.setStyleSheet(value_style)

        # Placement dans la grille
        grid.addWidget(self.cpu_label, 0, 0)
        grid.addWidget(self.cpu_value, 0, 1)
        grid.addWidget(self.cpu_bar, 0, 2)
        grid.addWidget(self.cpu_cores_label, 1, 0)
        grid.addWidget(self.cpu_cores_value, 1, 1)
        grid.addWidget(self.ram_label, 2, 0)
        grid.addWidget(self.ram_value, 2, 1)
        grid.addWidget(self.ram_bar, 2, 2)
        grid.addWidget(self.disk_label, 3, 0)
        grid.addWidget(self.disk_value, 3, 1)
        grid.addWidget(self.net_label, 4, 0)
        grid.addWidget(self.net_value, 4, 1)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color:#444; background:#444; min-height:2px; margin:12px 0;")
        layout.addWidget(sep)
        layout.addLayout(grid)

        btn_copy = QPushButton("📋 Copier les stats")
        btn_copy.setStyleSheet("background-color:#0078D7; color:white; border-radius:8px; padding:8px; font-weight:bold;")
        btn_copy.clicked.connect(self.copy_stats)
        layout.addWidget(btn_copy)

        self.last_net = psutil.net_io_counters()
        self.last_net_time = psutil.time.time()

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.refresh_system_stats)
        self.stats_timer.start(1000)
        self.refresh_system_stats()

    def refresh_system_stats(self):
        cpu = psutil.cpu_percent()
        cpu_cores = psutil.cpu_count(logical=True)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        self.cpu_value.setText(f"{cpu} %")
        self.cpu_bar.setValue(int(cpu))
        self.cpu_cores_value.setText(f"{cpu_cores}")
        self.ram_value.setText(f"{ram.percent} % ({format_bytes(ram.used)}/{format_bytes(ram.total)})")
        self.ram_bar.setValue(int(ram.percent))
        self.disk_value.setText(f"{disk.percent} % ({format_bytes(disk.used)}/{format_bytes(disk.total)})")

        # Réseau (débit entrant/sortant)
        net = psutil.net_io_counters()
        now = psutil.time.time()
        duration = now - getattr(self, 'last_net_time', now)
        if duration > 0:
            rx = (net.bytes_recv - getattr(self, 'last_net', net).bytes_recv) / duration
            tx = (net.bytes_sent - getattr(self, 'last_net', net).bytes_sent) / duration
            self.net_value.setText(f"↓ {format_bytes(rx)}/s  ↑ {format_bytes(tx)}/s")
        self.last_net = net
        self.last_net_time = now

    def copy_stats(self):
        stats = (
            f"{self.cpu_label.text()} {self.cpu_value.text()}\n"
            f"{self.cpu_cores_label.text()} {self.cpu_cores_value.text()}\n"
            f"{self.ram_label.text()} {self.ram_value.text()}\n"
            f"{self.disk_label.text()} {self.disk_value.text()}\n"
            f"{self.net_label.text()} {self.net_value.text()}"
        )
        QApplication.clipboard().setText(stats)