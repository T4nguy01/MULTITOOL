# core/ping.py
import ipaddress
import re
import subprocess
import sys

_HOSTNAME = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.-]{0,251}[A-Za-z0-9])?$")


def _valid_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return bool(_HOSTNAME.match(host))


def ping_host(host: str) -> str:
    if not _valid_host(host):
        return f"Hôte invalide : {host!r}"
    param = "-n" if sys.platform.startswith("win") else "-c"
    try:
        output = subprocess.run(
            ["ping", param, "4", host],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return output.stdout
    except subprocess.TimeoutExpired:
        return f"Timeout lors du ping {host}"
    except subprocess.CalledProcessError as e:
        return e.stdout or f"Erreur lors du ping {host}"
