# tabs/reseaux_config.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QCompleter
from typing import Optional
from core.network import get_interfaces, set_ip, set_dhcp
import psutil
from PyQt6.QtCore import Qt


def get_default_gateway(interface_name: str) -> Optional[str]:
    """Retourne la passerelle par défaut pour une interface spécifique (Windows/Linux)."""
    gateways = psutil.net_if_stats()  # On peut adapter selon ton OS pour récupérer la gateway
    # Pour simplifier, retourne None ici
    return None


class ReseauxTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("🌐 Configuration Réseau"))

        # Liste déroulante des interfaces
        self.interface_box = QComboBox()
        layout.addWidget(self.interface_box)

        # Champs pour IP / masque / passerelle (remplis automatiquement)
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Adresse IP actuelle")

        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("Masque actuel")

        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("Passerelle actuelle")

        layout.addWidget(self.ip_input)
        layout.addWidget(self.mask_input)
        layout.addWidget(self.gateway_input)

        # Boutons appliquer / DHCP
        self.apply_btn = QPushButton("Appliquer IP")
        self.dhcp_btn = QPushButton("Passer en DHCP")
        layout.addWidget(self.apply_btn)
        layout.addWidget(self.dhcp_btn)

        # Zone de résultat
        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.setLayout(layout)

        # Charger les interfaces réseau
        self.load_interfaces()

        # Connexion boutons
        self.apply_btn.clicked.connect(self.apply_config)
        self.dhcp_btn.clicked.connect(self.apply_dhcp)
        self.interface_box.currentIndexChanged.connect(self.update_current_ip)

    def load_interfaces(self):
        """Remplit la liste des interfaces disponibles"""
        self.interfaces = get_interfaces()
        self.interface_box.clear()
        for iface in self.interfaces.keys():
            self.interface_box.addItem(iface)

        self.update_current_ip()

    def update_current_ip(self):
        """Remplit les champs avec l’IP/mask/gateway actuelle"""
        iface = self.interface_box.currentText()
        if iface and iface in self.interfaces:
            ip, mask, gw = None, None, get_default_gateway(iface)
            for addr in self.interfaces[iface]:
                # IPv4 uniquement
                if addr.family.name == "AF_INET":
                    ip = addr.address
                    mask = addr.netmask
            self.ip_input.setText(ip or "")
            self.mask_input.setText(mask or "")
            self.gateway_input.setText(gw or "")
            self.update_ip_completer()
        else:
            self.ip_input.clear()
            self.mask_input.clear()
            self.gateway_input.clear()

    def update_ip_completer(self):
        """Ajoute un autocomplete pour l'IP"""
        completer = QCompleter([ip.address for addrs in self.interfaces.values() for ip in addrs if ip.family.name == "AF_INET"])
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.ip_input.setCompleter(completer)

    def apply_config(self):
        """Applique une nouvelle configuration réseau"""
        iface = self.interface_box.currentText()
        ip = self.ip_input.text().strip()
        mask = self.mask_input.text().strip()
        gw = self.gateway_input.text().strip() or None

        if not iface or not ip or not mask:
            self.result_area.setPlainText("⚠️ Veuillez remplir au minimum Interface + IP + Masque.")
            return

        result = set_ip(iface, ip, mask, gw)
        self.result_area.setPlainText(result)
        self.load_interfaces()

    def apply_dhcp(self):
        """Passe l'interface sélectionnée en DHCP"""
        iface = self.interface_box.currentText()
        if not iface:
            self.result_area.setPlainText("⚠️ Veuillez sélectionner une interface.")
            return

        result = set_dhcp(iface)
        self.result_area.setPlainText(result)
        self.load_interfaces()
