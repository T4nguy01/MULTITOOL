# core/network.py

import psutil
import subprocess
import sys
import ctypes
import socket
import platform

def is_admin() -> bool:
    if sys.platform.startswith("win"):
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except:
            return False
    return True

def get_default_gateway() -> dict:
    """Retourne la passerelle par défaut pour chaque interface"""
    gateways = {}
    system = platform.system().lower()

    try:
        if system == "windows":
            output = subprocess.check_output("route print", shell=True, encoding="utf-8")
            lines = output.splitlines()
            for i, line in enumerate(lines):
                if "IPv4 Route Table" in line:
                    for route_line in lines[i+2:]:
                        if route_line.strip().startswith("0.0.0.0"):
                            parts = route_line.split()
                            if len(parts) >= 4:
                                gw = parts[2]
                                iface = parts[-1]
                                gateways[iface] = gw
                            break
        else:
            output = subprocess.check_output("ip route", shell=True, encoding="utf-8")
            for line in output.strip().splitlines():
                if line.startswith("default via"):
                    parts = line.split()
                    gw = parts[2]
                    iface = parts[4]
                    gateways[iface] = gw
                    break
    except Exception as e:
        print("Erreur passerelle:", e)

    return gateways

def get_interfaces():
    """Retourne les interfaces réseau avec leur IP, masque, et passerelle"""
    result = {}
    all_addrs = psutil.net_if_addrs()
    gateways = get_default_gateway()

    for iface, addrs in all_addrs.items():
        iface_data = {"ip": "", "mask": "", "gateway": gateways.get(iface, "")}

        for addr in addrs:
            if addr.family == socket.AF_INET:
                iface_data["ip"] = addr.address
                iface_data["mask"] = addr.netmask
                break

        result[iface] = iface_data

    return result

def set_ip(interface: str, ip: str, mask: str, gateway: str = None) -> str:
    if sys.platform.startswith("win") and not is_admin():
        return "⚠️ Erreur : veuillez lancer l'application en mode Administrateur pour changer l'IP."

    try:
        if sys.platform.startswith("win"):
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "static", ip, mask]
            if gateway:
                cmd.append(gateway)
        else:
            cmd = ["sudo", "ip", "addr", "flush", "dev", interface]
            subprocess.run(cmd, check=True)
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
    if sys.platform.startswith("win") and not is_admin():
        return "⚠️ Erreur : veuillez lancer l'application en mode Administrateur pour changer l'IP."

    try:
        if sys.platform.startswith("win"):
            cmd = ["netsh", "interface", "ip", "set", "address",
                   f"name={interface}", "dhcp"]
        else:
            subprocess.run(["sudo", "dhclient", "-r", interface], check=True)
            cmd = ["sudo", "dhclient", interface]

        subprocess.run(cmd, check=True)
        return f"✅ Interface '{interface}' passée en DHCP avec succès."
    except subprocess.CalledProcessError as e:
        return f"❌ Erreur lors du passage en DHCP : {e}\nVérifiez le nom exact de l'interface et les droits administrateur."
    except Exception as e:
        return f"❌ Erreur inattendue : {e}"
