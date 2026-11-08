import psutil
import subprocess
import sys
import ctypes
import ipaddress

def is_admin() -> bool:
    """Retourne True si le script est lancé en admin (Windows)."""
    if sys.platform.startswith("win"):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except (AttributeError, OSError):
            return False
    return True  # Linux/Mac supposé sudo géré à part

def get_interfaces():
    """Retourne les interfaces réseau disponibles avec leurs adresses IP"""
    return psutil.net_if_addrs()

def set_ip(interface: str, ip: str, mask: str, gateway: str = None) -> str:
    """Change l'IP d'une interface (Windows / Linux simplifié)"""
    if sys.platform.startswith("win") and not is_admin():
        return "⚠️ Erreur : veuillez lancer l'application en mode Administrateur pour changer l'IP."

    try:
        ipaddress.IPv4Address(ip)
        prefix = ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
        if gateway:
            ipaddress.IPv4Address(gateway)
    except ValueError as e:
        return f"❌ Paramètres invalides : {e}"

    try:
        if sys.platform.startswith("win"):
            # Construction de la commande netsh
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "static", ip, mask]
            if gateway:
                cmd.append(gateway)
            subprocess.run(cmd, check=True)
        else:
            # Linux / Mac : l'adresse d'abord, la route par défaut ensuite
            subprocess.run(["sudo", "ip", "addr", "add", f"{ip}/{prefix}", "dev", interface], check=True)
            if gateway:
                subprocess.run(["sudo", "ip", "route", "add", "default", "via", gateway], check=True)
        return f"✅ Nouvelle IP appliquée : {ip} (masque {mask}, passerelle {gateway or 'aucune'})"
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur lors de la configuration réseau : commande échouée\nDétails : {e}\nVérifiez le nom exact de l'interface et les droits administrateur."
    except Exception as e:
        return f"❌ Erreur inattendue : {e}"

def set_dhcp(interface: str) -> str:
    """Passe une interface en DHCP"""
    if sys.platform.startswith("win") and not is_admin():
        return "⚠️ Erreur : veuillez lancer l'application en mode Administrateur pour changer l'IP."

    try:
        if sys.platform.startswith("win"):
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "dhcp"]
        else:
            cmd = ["sudo", "dhclient", "-r", interface]
            subprocess.run(cmd, check=True)
            cmd = ["sudo", "dhclient", interface]

        subprocess.run(cmd, check=True)
        return f"✅ Interface '{interface}' passée en DHCP avec succès."
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur lors du passage en DHCP : {e}\nVérifiez le nom exact de l'interface et les droits administrateur."
    except Exception as e:
        return f"❌ Erreur inattendue : {e}"
