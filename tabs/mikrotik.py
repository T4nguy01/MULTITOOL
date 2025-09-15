# tabs/mikrotik.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit,
    QDialog, QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt
import os
from core import mikrotik as core_mikrotik


class MikrotikTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setObjectName("mikrotikTab")
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        self.setLayout(layout)

        # Terminal
        self.terminal = QPlainTextEdit()
        self.terminal.setObjectName("mikrotikTerminal")  # pour QSS spécifique
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 11))
        self.terminal.setPlainText(core_mikrotik.base_config())
        layout.addWidget(self.terminal, 2)

        # Boutons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        icon_path = lambda name: os.path.join("resources", "icons", f"{name}.svg")

        self.lan_btn = QPushButton("Ajout LAN")
        self.lan_btn.setIcon(QIcon(icon_path("lan")))
        self.port_btn = QPushButton("Redirection de Port")
        self.port_btn.setIcon(QIcon(icon_path("nat")))

        # Utiliser QSS global, retirer les styles inline
        for btn in [self.lan_btn, self.port_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_layout.addWidget(btn)

        # Connexions
        self.lan_btn.clicked.connect(self.add_lan)
        self.port_btn.clicked.connect(self.add_port_forward)

    def insert_config(self, config_text: str):
        """Insère un bloc dans le terminal."""
        self.terminal.appendPlainText(config_text)

    # --- Popups ---
    def add_lan(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter un LAN")
        layout = QFormLayout(dialog)

        iface_input = QLineEdit()
        ip_input = QLineEdit()
        mask_input = QLineEdit()
        dhcp_start_input = QLineEdit()
        dhcp_end_input = QLineEdit()

        layout.addRow("Port Ethernet:", iface_input)
        layout.addRow("Adresse IP LAN:", ip_input)
        layout.addRow("Masque:", mask_input)
        layout.addRow("DHCP Début:", dhcp_start_input)
        layout.addRow("DHCP Fin:", dhcp_end_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = core_mikrotik.lan_block(
                iface_input.text(),
                ip_input.text(),
                mask_input.text(),
                dhcp_start_input.text(),
                dhcp_end_input.text(),
            )
            self.insert_config(config)

    def add_port_forward(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter une redirection de port")
        layout = QFormLayout(dialog)

        to_ip_input = QLineEdit()
        lan_port_input = QLineEdit()
        proto_input = QLineEdit()
        wan_ip_input = QLineEdit()
        wan_port_input = QLineEdit()

        layout.addRow("Adresse LAN:", to_ip_input)
        layout.addRow("Port LAN:", lan_port_input)
        layout.addRow("Protocole:", proto_input)
        layout.addRow("IP WAN (optionnel):", wan_ip_input)
        layout.addRow("Port WAN:", wan_port_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            config = core_mikrotik.port_forward_block(
                to_ip_input.text(),
                lan_port_input.text(),
                proto_input.text(),
                wan_ip_input.text(),
                wan_port_input.text(),
            )
            self.insert_config(config)
