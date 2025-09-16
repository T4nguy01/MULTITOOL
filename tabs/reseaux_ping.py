# tabs/reseaux_ping.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from core.settings import SETTINGS
from core import ping as core_ping
import time

# Objet signal pour communiquer entre threads et UI
class WorkerSignals(QObject):
    finished = pyqtSignal(str)

# QRunnable pour exécuter un ping en arrière-plan
class PingRunnable(QRunnable):
    def __init__(self, host):
        super().__init__()
        self.host = host
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = core_ping.ping_host(self.host)
        except Exception as e:
            result = f"❌ Erreur inattendue pour {self.host} : {e}"
        self.signals.finished.emit(result)

class ReseauxPingTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Ping préconfigurés"))

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        # Récupération des hôtes depuis SETTINGS
        self.hosts = getattr(SETTINGS, "ping_hosts", [])

        # Thread pool pour limiter les threads simultanés
        self.thread_pool = QThreadPool.globalInstance()
        self.thread_pool.setMaxThreadCount(4)  # max 4 pings simultanés

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
        worker = PingRunnable(host)
        worker.signals.finished.connect(self.show_result)
        self.thread_pool.start(worker)

    def show_result(self, result):
        self.result_area.append(result)

    def set_default_host(self, host):
        self.result_area.append(f"Host par défaut changé vers : {host}")
