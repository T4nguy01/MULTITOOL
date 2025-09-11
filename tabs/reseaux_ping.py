# tabs/reseaux_ping.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import QThread, pyqtSignal
from core.settings import SETTINGS
import subprocess, sys

# Worker pour exécuter le ping dans un thread séparé
class PingWorker(QThread):
    finished = pyqtSignal(str)

    def __init__(self, host):
        super().__init__()
        self.host = host

    def run(self):
        result = self.ping_host(self.host)
        self.finished.emit(result)

    @staticmethod
    def ping_host(host: str) -> str:
        param = "-n" if sys.platform.startswith("win") else "-c"
        try:
            output = subprocess.run(
                ["ping", param, "4", host],
                capture_output=True,
                text=True,
                check=True
            )
            return output.stdout
        except subprocess.CalledProcessError as e:
            return e.output or f"Erreur lors du ping {host}"

class ReseauxPingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ping préconfigurés"))

        self.hosts = SETTINGS.ping_hosts

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        for host in self.hosts:
            btn = QPushButton(f"Ping {host}")
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
