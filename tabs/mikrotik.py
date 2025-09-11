# tabs/mikrotik.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit,
    QDialog, QLineEdit, QLabel, QFormLayout, QDialogButtonBox
)
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette
from PyQt6.QtCore import Qt
from core import mikrotik as core_mikrotik
import os

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
        self.terminal.setReadOnly(True)
        self.terminal.setFont(QFont("Consolas", 11))
        self.terminal.setStyleSheet("""
            QPlainTextEdit {
                background-color: rgba(40, 40, 40, 220);
                color: #ffffff;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        self.terminal.setPlainText(core_mikrotik.base_config())
        layout.addWidget(self.terminal, 2)

        # Boutons pour ajouter des blocs
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)
        layout.addLayout(btn_layout)

        # Dossier ressources pour icônes
        icon_path = lambda name: os.path.join("resources", "icons", f"{name}.svg")

        self.wifi_btn = QPushButton("Wi-Fi")
        self.wifi_btn.setIcon(QIcon(icon_path("wifi")))
        self.vlan_btn = QPushButton("VLAN")
        self.vlan_btn.setIcon(QIcon(icon_path("vlan")))
        self.nat_btn = QPushButton("NAT")
        self.nat_btn.setIcon(QIcon(icon_path("nat")))

        for btn in [self.wifi_btn, self.vlan_btn, self.nat_btn]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border-radius: 6px;
                    padding: 6px 12px;
                }
                QPushButton:hover {
                    background-color: #5a5a5a;
                }
            """)
            btn_layout.addWidget(btn)

        # Connexions
        self.wifi_btn.clicked.connect(self.add_wifi)
        self.vlan_btn.clicked.connect(self.add_vlan)
        self.nat_btn.clicked.connect(self.add_nat)

    def insert_config(self, config_text):
        """Insère un bloc dans le terminal."""
        self.terminal.appendPlainText(config_text)

    # --- Popups pour config ---
    def add_wifi(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter Wi-Fi")
        layout = QFormLayout(dialog)

        ssid_input = QLineEdit()
        key_input = QLineEdit()
        layout.addRow("SSID:", ssid_input)
        layout.addRow("Clé WPA2:", key_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            ssid = ssid_input.text()
            key = key_input.text()
            self.insert_config(core_mikrotik.wifi_block(ssid, key))

    def add_nat(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter NAT")
        layout = QFormLayout(dialog)

        to_ip_input = QLineEdit()
        to_port_input = QLineEdit()
        src_input = QLineEdit()
        dst_port_input = QLineEdit()
        layout.addRow("To IP:", to_ip_input)
        layout.addRow("To Port:", to_port_input)
        layout.addRow("Src Address:", src_input)
        layout.addRow("Dst Port:", dst_port_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.insert_config(core_mikrotik.nat_block(
                to_ip_input.text(),
                int(to_port_input.text()),
                src_input.text(),
                int(dst_port_input.text())
            ))

    def add_vlan(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Ajouter VLAN")
        layout = QFormLayout(dialog)

        vlan_id_input = QLineEdit()
        iface_input = QLineEdit()
        ip_net_input = QLineEdit()
        layout.addRow("VLAN ID:", vlan_id_input)
        layout.addRow("Interface:", iface_input)
        layout.addRow("IP Network:", ip_net_input)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        layout.addWidget(buttons)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.insert_config(core_mikrotik.vlan_block(
                int(vlan_id_input.text()),
                iface_input.text(),
                ip_net_input.text()
            ))
