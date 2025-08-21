import os
import sys
import subprocess
import ipaddress
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTextEdit, QProgressBar, QListWidget, QListWidgetItem, QGroupBox, QGridLayout, QMessageBox, QTabWidget, QComboBox
)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt, QTimer

import psutil

from config_manager import ConfigManager
from network import get_network_interfaces, get_interface_info
from ping_worker import PingWorker
from network_worker import NetworkWorker
from extensions.extension_manager import ExtensionManager
from utils.helper import format_bytes, current_time
from stats_worker import StatsPage

def read_version():
    try:
        with open("version.txt") as f:
            return f.read().strip()
    except Exception:
        return "?"

VERSION_LOCALE = read_version()

def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0

class MainWindow(QMainWindow):
    """
    Fenêtre principale de l'application Multitool.
    Gère les onglets Ping, Réseau, Extensions et Stats.
    """
    def __init__(self, config: ConfigManager):
        super().__init__()
        self.config_manager = config
        self.extension_manager = ExtensionManager()
        self.setWindowTitle(f"Multitool v{VERSION_LOCALE}")
        self.resize(900, 700)

        # Restaurer la géométrie si disponible
        geometry = self.config_manager.get("window_geometry")
        if geometry:
            self.restoreGeometry(bytes.fromhex(geometry))

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Nouvel ordre : Ping, Réseau, Extensions, Stats
        self.tabs.addTab(self.create_ping_page(), "📡 Ping")
        self.tabs.addTab(self.create_network_page(), "🌐 Réseau")
        self.tabs.addTab(self.create_extensions_page(), "🧩 Extensions")
        self.tabs.addTab(StatsPage(), "📊 Stats")

    # -------------------- PAGE PING --------------------
    def create_ping_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("📡 Test de Ping")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color: white; margin-bottom: 20px;")
        layout.addWidget(title)

        # Input personnalisé
        input_group = QGroupBox("Test Personnalisé")
        input_group.setStyleSheet("QGroupBox {font-size: 16px; font-weight: bold; color: white; border: 2px solid #444; border-radius: 10px; margin-top: 10px; padding-top: 10px;}")
        input_layout = QHBoxLayout(input_group)
        self.custom_ip_input = QLineEdit()
        self.custom_ip_input.setPlaceholderText("Entrez une adresse IP ou un nom de domaine...")
        self.custom_ip_input.setStyleSheet("padding:8px; border-radius:6px; background-color:#2d2d2d; color:white;")
        input_layout.addWidget(self.custom_ip_input)

        btn_ping = QPushButton("🚀 Ping")
        btn_ping.setStyleSheet("background-color:#0078D7; color:white; border-radius:8px; padding:10px; font-weight:bold;")
        btn_ping.clicked.connect(self.ping_custom_ip)
        input_layout.addWidget(btn_ping)
        layout.addWidget(input_group)

        # Progress bar
        self.ping_progress = QProgressBar()
        self.ping_progress.setVisible(False)
        self.ping_progress.setStyleSheet("QProgressBar {border: 2px solid #444; border-radius: 8px; text-align:center; background-color:#2d2d2d; color:white;} QProgressBar::chunk {background-color:#0078D7; border-radius:6px;}")
        layout.addWidget(self.ping_progress)

        # Résultats
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setStyleSheet("background-color:#1e1e1e; color:white; border:2px solid #444; border-radius:10px; padding:15px; font-family:'Consolas'; font-size:13px;")
        layout.addWidget(self.result_box)

        # Tests rapides
        quick_group = QGroupBox("Tests Rapides")
        quick_group.setStyleSheet(input_group.styleSheet())
        quick_layout = QGridLayout(quick_group)
        recent_ips = self.config_manager.get("recent_ips", ["8.8.8.8","1.1.1.1","192.168.1.1","google.com"])
        for i, ip in enumerate(recent_ips):
            btn = QPushButton(f"📡 {ip}")
            btn.setStyleSheet("background-color:#3a3a3a; color:white; border:none; border-radius:8px; padding:12px; font-size:14px;")
            btn.clicked.connect(lambda _, ip=ip: self.start_ping(ip))
            quick_layout.addWidget(btn, i // 2, i % 2)
        layout.addWidget(quick_group)

        return page

    def ping_custom_ip(self):
        ip = self.custom_ip_input.text().strip()
        if ip:
            self.start_ping(ip)
            recent = self.config_manager.get("recent_ips", [])
            if ip in recent:
                recent.remove(ip)
            recent.insert(0, ip)
            self.config_manager.set("recent_ips", recent[:8])

    def start_ping(self, ip):
        self.result_box.append(f"🔄 <span style='color:#0078D7;'>Ping vers {ip}...</span>")
        self.ping_progress.setVisible(True)
        self.ping_progress.setValue(0)
        self.ping_thread = PingWorker(ip, count=4)
        self.ping_thread.finished.connect(self.on_ping_finished)
        self.ping_thread.progress.connect(self.ping_progress.setValue)
        self.ping_thread.start()

    def on_ping_finished(self, message, success):
        self.ping_progress.setVisible(False)
        icon = "✅" if success else "❌"
        color = "#28a745" if success else "#dc3545"
        self.result_box.append(f"{icon} <span style='color:{color};'>{message}</span>\n")
        self.result_box.verticalScrollBar().setValue(self.result_box.verticalScrollBar().maximum())

    # -------------------- PAGE EXTENSIONS --------------------
    def create_extensions_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("🧩 Extensions")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("color:white;margin-bottom:20px;")
        layout.addWidget(title)

        self.extensions_list_widget = QListWidget()
        layout.addWidget(self.extensions_list_widget)

        btn_layout = QHBoxLayout()
        btn_refresh = QPushButton("🔄 Rafraîchir")
        btn_refresh.clicked.connect(self.load_extensions)
        btn_layout.addWidget(btn_refresh)
        layout.addLayout(btn_layout)

        self.load_extensions()
        return page

    def load_extensions(self):
        self.extensions_list_widget.clear()
        scripts = self.extension_manager.list_extensions()
        if not scripts:
            self.extensions_list_widget.addItem("Aucune extension trouvée.")
            return
        for script in scripts:
            item = QListWidgetItem(f"📄 {script}")
            self.extensions_list_widget.addItem(item)

    # -------------------- PAGE STATS --------------------
    def create_stats_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("📊 Statistiques Système")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Valeurs CPU/RAM
        self.cpu_value = QLabel("")
        self.cpu_value.setStyleSheet("color:white; font-size:18px;")
        layout.addWidget(self.cpu_value)

        self.ram_value = QLabel("")
        self.ram_value.setStyleSheet("color:white; font-size:18px;")
        layout.addWidget(self.ram_value)

        # Barres de progression CPU/RAM
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setTextVisible(False)
        self.cpu_bar.setStyleSheet("QProgressBar {border: 2px solid #444; border-radius: 8px; background-color:#2d2d2d;} QProgressBar::chunk {background-color:#0078D7; border-radius:6px;}")
        layout.addWidget(self.cpu_bar)

        self.ram_bar = QProgressBar()
        self.ram_bar.setTextVisible(False)
        self.ram_bar.setStyleSheet("QProgressBar {border: 2px solid #444; border-radius: 8px; background-color:#2d2d2d;} QProgressBar::chunk {background-color:#0078D7; border-radius:6px;}")
        layout.addWidget(self.ram_bar)

        # Autres labels
        self.disk_label = QLabel("Disque :")
        self.disk_total_label = QLabel("Disque total :")
        self.net_label = QLabel("Réseau :")

        layout.addWidget(self.disk_label)
        layout.addWidget(self.disk_total_label)
        layout.addWidget(self.net_label)

        self.last_net = psutil.net_io_counters()
        self.last_net_time = psutil.time.time()

        self.stats_timer = QTimer(self)
        self.stats_timer.timeout.connect(self.refresh_system_stats)
        self.stats_timer.start(1000)
        self.refresh_system_stats()

        return page

    def refresh_system_stats(self):
        cpu = psutil.cpu_percent()
        cpu_cores = psutil.cpu_count(logical=True)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        self.cpu_value.setText(f"{cpu} %")
        self.cpu_bar.setValue(int(cpu))
        self.ram_value.setText(f"{ram.percent} %")
        self.ram_bar.setValue(int(ram.percent))
        self.disk_label.setText(f"Disque utilisé : {disk.percent} %")
        self.disk_total_label.setText(f"Disque total : {format_bytes(disk.total)}")

        # Réseau (débit entrant/sortant)
        net = psutil.net_io_counters()
        now = psutil.time.time()
        duration = now - getattr(self, 'last_net_time', now)
        if duration > 0:
            rx = (net.bytes_recv - getattr(self, 'last_net', net).bytes_recv) / duration
            tx = (net.bytes_sent - getattr(self, 'last_net', net).bytes_sent) / duration
            self.net_label.setText(f"Réseau : ↓ {format_bytes(rx)}/s  ↑ {format_bytes(tx)}/s")
        self.last_net = net
        self.last_net_time = now

    # -------------------- PAGE NETWORK --------------------
    def create_network_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)

        title = QLabel("🌐 Gestion Réseau")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        layout.addWidget(title)

        # Groupe interface
        iface_group = QGroupBox("Sélection de l'interface")
        iface_layout = QHBoxLayout(iface_group)
        self.iface_combo = QComboBox()
        self.iface_combo.addItems(get_network_interfaces())
        self.iface_combo.currentTextChanged.connect(self.load_iface_info)
        iface_layout.addWidget(self.iface_combo)
        layout.addWidget(iface_group)

        # Paramètres IP
        param_group = QGroupBox("Paramètres IP")
        param_layout = QGridLayout(param_group)
        param_layout.addWidget(QLabel("Adresse IP:"), 0, 0)
        self.ip_input = QLineEdit()
        param_layout.addWidget(self.ip_input, 0, 1)
        param_layout.addWidget(QLabel("Masque:"), 1, 0)
        self.subnet_input = QLineEdit()
        param_layout.addWidget(self.subnet_input, 1, 1)
        param_layout.addWidget(QLabel("Passerelle:"), 2, 0)
        self.gateway_input = QLineEdit()
        param_layout.addWidget(self.gateway_input, 2, 1)
        layout.addWidget(param_group)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_apply = QPushButton("💾 Appliquer")
        btn_apply.clicked.connect(self.apply_network_settings)
        btn_layout.addWidget(btn_apply)
        btn_dhcp = QPushButton("🌐 DHCP")
        btn_dhcp.clicked.connect(self.set_dhcp)
        btn_layout.addWidget(btn_dhcp)
        btn_refresh = QPushButton("🔄 Actualiser")
        btn_refresh.clicked.connect(self.refresh_iface_list)
        btn_layout.addWidget(btn_refresh)
        layout.addLayout(btn_layout)

        # Zone de résultat
        self.network_result = QTextEdit()
        self.network_result.setReadOnly(True)
        layout.addWidget(self.network_result)

        # Charger infos interface sélectionnée
        self.load_iface_info()
        return page

    def load_iface_info(self):
        iface = self.iface_combo.currentText()
        if not iface:
            self.ip_input.setText("")
            self.subnet_input.setText("")
            self.gateway_input.setText("")
            self.network_result.setPlainText("Aucune interface sélectionnée.")
            return
        info = get_interface_info(iface)
        self.ip_input.setText(info.get("ip", "") or "")
        self.subnet_input.setText(info.get("subnet", "") or "")
        self.gateway_input.setText(info.get("gateway", "") or "")
        # Affichage lisible même si aucune IP
        ip = info.get("ip", "") or "Aucune"
        subnet = info.get("subnet", "") or "Aucune"
        gateway = info.get("gateway", "") or "Aucune"
        self.network_result.setPlainText(
            f"Interface : {iface}\nIP : {ip}\nMasque : {subnet}\nPasserelle : {gateway}"
        )

    def apply_network_settings(self):
        iface = self.iface_combo.currentText()
        ip = self.ip_input.text().strip()
        subnet = self.subnet_input.text().strip()
        gateway = self.gateway_input.text().strip()
        if not (iface and ip and subnet):
            QMessageBox.warning(self, "Erreur", "Veuillez remplir tous les champs obligatoires (IP, masque).")
            return
        try:
            ipaddress.IPv4Address(ip)
            ipaddress.IPv4Address(subnet)
            if gateway:
                ipaddress.IPv4Address(gateway)
        except Exception:
            QMessageBox.critical(self, "Erreur", "Adresse IP, masque ou passerelle invalide.")
            return
        confirm = QMessageBox.question(self, "Confirmation", f"Appliquer la configuration suivante à {iface} ?\nIP: {ip}\nMasque: {subnet}\nPasserelle: {gateway or 'Aucune'}")
        if confirm != QMessageBox.StandardButton.Yes:
            return
        self.network_result.append("🔄 Application des paramètres réseau...")
        self.network_thread = NetworkWorker(iface, ip, subnet, gateway)
        self.network_thread.finished.connect(self.on_network_finished)
        self.network_thread.start()

    def set_dhcp(self):
        iface = self.iface_combo.currentText()
        if not iface:
            return
        self.network_result.append("🔄 Passage en DHCP...")
        self.network_thread = NetworkWorker(iface, "", "", "", dhcp=True)
        self.network_thread.finished.connect(self.on_network_finished)
        self.network_thread.start()

    def on_network_finished(self, message, success):
        self.network_result.append(message)
        self.load_iface_info()

    def refresh_iface_list(self):
        current = self.iface_combo.currentText()
        self.iface_combo.blockSignals(True)
        self.iface_combo.clear()
        self.iface_combo.addItems(get_network_interfaces())
        idx = self.iface_combo.findText(current)
        if idx >= 0:
            self.iface_combo.setCurrentIndex(idx)
        self.iface_combo.blockSignals(False)
        self.load_iface_info()

    # -------------------- CLOSE EVENT --------------------
    def closeEvent(self, event):
        self.config_manager.set("window_geometry", self.saveGeometry().toHex().data().decode())
        event.accept()

# -------------------- LANCEMENT --------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    if not is_admin():
        QMessageBox.critical(None, "Droits insuffisants", "L'application doit être lancée en tant qu'administrateur pour modifier les paramètres réseau.")
        sys.exit(1)
    config = ConfigManager()
    window = MainWindow(config)
    window.show()
    sys.exit(app.exec())
