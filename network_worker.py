from PyQt6.QtCore import QThread, pyqtSignal
import subprocess

class NetworkWorker(QThread):
    finished = pyqtSignal(str, bool)  # message, success

    def __init__(self, iface, ip, subnet, gateway, dhcp=False):
        super().__init__()
        self.iface = iface
        self.ip = ip
        self.subnet = subnet
        self.gateway = gateway
        self.dhcp = dhcp

    def run(self):
        try:
            if self.dhcp:
                # Commande pour passer en DHCP
                cmd = [
                    "netsh", "interface", "ip", "set", "address",
                    f'name={self.iface}', "dhcp"
                ]
                result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    self.finished.emit("✅ Interface passée en DHCP.", True)
                else:
                    self.finished.emit(f"❌ Erreur DHCP: {result.stderr}", False)
            else:
                cmd_ip = [
                    "netsh", "interface", "ip", "set", "address",
                    f'name={self.iface}', "static", self.ip, self.subnet, self.gateway if self.gateway else "none"
                ]
                result_ip = subprocess.run(cmd_ip, capture_output=True, text=True, shell=True)
                if result_ip.returncode == 0:
                    self.finished.emit("✅ Paramètres appliqués avec succès.", True)
                else:
                    self.finished.emit(f"❌ Erreur: {result_ip.stderr}", False)
        except Exception as e:
            self.finished.emit(f"❌ Exception: {e}", False)