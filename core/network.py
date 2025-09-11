import psutil
import subprocess
import sys

def get_interfaces():
    """Retourne les interfaces réseau disponibles avec leurs adresses IP"""
    return psutil.net_if_addrs()

def set_ip(interface: str, ip: str, mask: str, gateway: str = None) -> str:
    """Change l'IP d'une interface (Windows / Linux simplifié)"""
    try:
        if sys.platform.startswith("win"):
            # Exemple avec netsh (Windows)
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "static", ip, mask]
            if gateway:
                cmd.append(gateway)
        else:
            # Exemple avec ip (Linux/Mac)
            cmd = ["sudo", "ip", "addr", "add", f"{ip}/{mask}", "dev", interface]
            if gateway:
                subprocess.run(["sudo", "ip", "route", "add", "default", "via", gateway], check=True)

        subprocess.run(cmd, check=True)
        return f"✅ Nouvelle IP appliquée : {ip} (masque {mask}, passerelle {gateway or 'aucune'})"
    except Exception as e:
        return f"❌ Erreur lors de la configuration réseau : {e}"
