import platform
import subprocess
import re

def get_network_interfaces():
    """Return a list of interface names."""
    result = subprocess.run(
        ['netsh', 'interface', 'show', 'interface'],
        capture_output=True, text=True, shell=True
    )
    interfaces = []
    for line in result.stdout.splitlines():
        # Ignore la ligne d'entête et les lignes vides
        if line.strip() and not line.lower().startswith("admin") and not line.lower().startswith("---"):
            parts = line.split()
            # Le nom de l'interface est à la fin de la ligne
            if len(parts) >= 4:
                iface_name = " ".join(parts[3:])
                interfaces.append(iface_name)
    return interfaces

def get_interface_info(interface):
    """Return dict with ip, subnet, gateway"""
    info = {"ip": "N/A", "subnet": "N/A", "gateway": "N/A"}
    try:
        if platform.system() == "Windows":
            result = subprocess.run(f"netsh interface ip show config name=\"{interface}\"", shell=True, capture_output=True, text=True)
            lines = result.stdout.splitlines()
            for line in lines:
                if "Adresse IP" in line: info["ip"] = line.split(":")[-1].strip()
                if "Masque de sous-réseau" in line: info["subnet"] = line.split(":")[-1].strip()
                if "Passerelle par défaut" in line: info["gateway"] = line.split(":")[-1].strip()
        else:
            # Linux/macOS
            result = subprocess.run(f"ip addr show {interface}", shell=True, capture_output=True, text=True)
            match = re.search(r"inet (\d+\.\d+\.\d+\.\d+)/(\d+)", result.stdout)
            if match:
                info["ip"] = match.group(1)
                info["subnet"] = match.group(2)
            result = subprocess.run("ip route | grep default", shell=True, capture_output=True, text=True)
            if result.stdout:
                info["gateway"] = result.stdout.strip().split()[2]
    except:
        pass
    return info
