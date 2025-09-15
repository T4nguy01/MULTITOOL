# tabs/reseaux_ping.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from core.settings import SETTINGS
from core import ping as core_ping
import sys

class PingWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, host):
        super().__init__()
        self.host = host

    def run(self):
        result = core_ping.ping_host(self.host)
        self.finished.emit(result)

class ReseauxPingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ping préconfigurés"))

        # Récupération des hôtes depuis SETTINGS
        # Format attendu : [{"name": "Google DNS", "host": "8.8.8.8"}, ...]
        self.hosts = getattr(SETTINGS, "ping_hosts", [])

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # Création des boutons pour chaque host
        for item in self.hosts:
            name = item.get("name", item.get("host", "Host"))
            host = item.get("host")
            if not host:
                continue
            btn = QPushButton(f"Ping {name}")
            btn.clicked.connect(lambda _, h=host: self.start_ping(h))
            layout.addWidget(btn)

        self.setLayout(layout)

    def start_ping(self, host):
        self.result_area.append(f"Ping en cours vers {host}...")
        self.thread = PingWorker(host)
        self.thread.finished.connect(self.show_result)
        self.thread.start()

    def show_result(self, result):
        self.result_area.append(result)

    def set_default_host(self, host):
        self.result_area.append(f"Host par défaut changé vers : {host}")
