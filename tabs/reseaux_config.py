from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox
from core.network import get_interfaces, set_ip, set_dhcp

class ReseauxTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Configuration Réseau"))

        # Liste déroulante des interfaces
        self.interface_box = QComboBox()
        layout.addWidget(self.interface_box)

        # Champs pour IP / masque / passerelle
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Nouvelle adresse IP")

        self.mask_input = QLineEdit()
        self.mask_input.setPlaceholderText("Masque (ex: 255.255.255.0)")

        self.gateway_input = QLineEdit()
        self.gateway_input.setPlaceholderText("Passerelle (optionnelle)")

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

    def load_interfaces(self):
        """Remplit la liste des interfaces disponibles"""
        interfaces = get_interfaces()
        self.interface_box.clear()
        for iface in interfaces.keys():
            self.interface_box.addItem(iface)

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

    def apply_dhcp(self):
        """Passe l'interface sélectionnée en DHCP"""
        iface = self.interface_box.currentText()
        if not iface:
            self.result_area.setPlainText("⚠️ Veuillez sélectionner une interface.")
            return

        result = set_dhcp(iface)
        self.result_area.setPlainText(result)
