# core/mikrotik.py

from config import MIKROTIK_BASE_CONFIG


def base_config():
    """
    Retourne la configuration de base d'un routeur Mikrotik
    (chargée depuis config.py pour ne pas l'exposer directement ici).
    """
    return MIKROTIK_BASE_CONFIG


def wifi_block(ssid: str, key: str, interface1="wlan1", interface2="wlan2"):
    """
    Génère un bloc de configuration Wi-Fi pour deux interfaces.
    """
    return (
        f'/interface wireless set {interface1} ssid="{ssid}" hide-ssid=yes\n'
        f'/interface wireless security-profiles set [find default=yes] wpa2-pre-shared-key="{key}"\n'
        f'/interface wireless enable {interface1}\n'
        f'/interface wireless set {interface2} ssid="{ssid}" hide-ssid=yes\n'
        f'/interface wireless security-profiles set [find default=yes] wpa2-pre-shared-key="{key}"\n'
        f'/interface wireless enable {interface2}\n'
    )


def nat_block(to_ip: str, to_port: int, src_address: str, dst_port: int, protocol="tcp"):
    """
    Génère un bloc NAT simple.
    """
    return (
        f"/ip firewall nat add chain=dstnat action=dst-nat to-addresses={to_ip} "
        f"to-ports={to_port} protocol={protocol} src-address={src_address} dst-port={dst_port}\n"
    )


def vlan_block(vlan_id: int, interface: str, ip_network: str):
    """
    Génère un bloc VLAN simple.
    """
    return (
        f"/interface vlan add name=vlan{vlan_id} vlan-id={vlan_id} interface={interface}\n"
        f"/ip address add address={ip_network} interface=vlan{vlan_id}\n"
    )
