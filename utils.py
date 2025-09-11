import subprocess
import platform

def ping(host="8.8.8.8", count=4):
    """
    Lance un ping vers une destination donnée.
    Retourne la sortie brute.
    """
    param = "-n" if platform.system().lower() == "windows" else "-c"
    try:
        result = subprocess.run(
            ["ping", param, str(count), host],
            capture_output=True, text=True
        )
        return result.stdout
    except Exception as e:
        return f"Erreur lors du ping: {e}"

def set_ip_config(ip, mask, gateway, interface="Ethernet"):
    """
    Exemple (Windows uniquement) : change la config IP.
    """
    try:
        subprocess.run(["netsh", "interface", "ip", "set", "address",
                        interface, "static", ip, mask, gateway],
                        check=True)
        return "Configuration appliquée avec succès"
    except Exception as e:
        return f"Erreur configuration IP: {e}"
