# core/ping.py
import subprocess, sys

def ping_host(host: str) -> str:
    param = "-n" if sys.platform.startswith("win") else "-c"
    try:
        output = subprocess.run(
            ["ping", param, "4", host],
            capture_output=True,
            text=True,
            check=True
        )
        return output.stdout
    except subprocess.CalledProcessError as e:
        return e.output or f"Erreur lors du ping {host}"
