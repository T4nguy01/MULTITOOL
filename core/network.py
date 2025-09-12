import psutil
import subprocess
import sys
import ctypes

def is_admin() -> bool:
    """Retourne True si le script est lancé en admin (Windows)."""
    if sys.platform.startswith("win"):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
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
        if sys.platform.startswith("win"):
            # Construction de la commande netsh
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "static", ip, mask]
            if gateway:
                cmd.append(gateway)
        else:
            # Linux / Mac
            cmd = ["sudo", "ip", "addr", "add", f"{ip}/{mask}", "dev", interface]
            if gateway:
                subprocess.run(["sudo", "ip", "route", "add", "default", "via", gateway], check=True)

        subprocess.run(cmd, check=True)
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
