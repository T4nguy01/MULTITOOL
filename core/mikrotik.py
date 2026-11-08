import ipaddress
import re

from core.appconfig import MIKROTIK_BASE_CONFIG

WAN_INTERFACE = "pppoe-out1"


def base_config():
    """
    Retourne la configuration de base d'un routeur Mikrotik
    (chargée depuis config.py pour ne pas l'exposer directement ici).
    """
    return MIKROTIK_BASE_CONFIG


# --- Validation / échappement : toute saisie utilisateur passe par ici ---

def _ip(value: str, label: str = "IP") -> str:
    try:
        return str(ipaddress.IPv4Address(value.strip()))
    except ValueError:
        raise ValueError(f"{label} invalide : {value!r}") from None


def _network(value: str, label: str = "Réseau") -> str:
    try:
        return str(ipaddress.IPv4Interface(value.strip()))
    except ValueError:
        raise ValueError(f"{label} invalide (attendu 192.168.1.1/24) : {value!r}") from None


def _prefix(mask: str) -> int:
    """Accepte '24', '/24' ou '255.255.255.0'."""
    mask = mask.strip().lstrip("/")
    try:
        if mask.isdigit():
            prefix = int(mask)
            if not 0 <= prefix <= 32:
                raise ValueError
            return prefix
        return ipaddress.IPv4Network(f"0.0.0.0/{mask}").prefixlen
    except ValueError:
        raise ValueError(f"Masque invalide : {mask!r}") from None


def _port(value, label: str = "Port") -> int:
    try:
        port = int(str(value).strip())
    except ValueError:
        raise ValueError(f"{label} invalide : {value!r}") from None
    if not 1 <= port <= 65535:
        raise ValueError(f"{label} hors plage (1-65535) : {port}")
    return port


def _ether(value: str) -> int:
    value = str(value).strip()
    if not value.isdigit() or int(value) < 1:
        raise ValueError(f"Port Ethernet invalide (numéro attendu) : {value!r}")
    return int(value)


def _proto(value: str) -> str:
    value = value.strip().lower()
    if value not in ("tcp", "udp"):
        raise ValueError(f"Protocole invalide (tcp ou udp) : {value!r}")
    return value


_NAME = re.compile(r"^[A-Za-z0-9._-]+$")


def _name(value: str, label: str = "Nom") -> str:
    value = value.strip()
    if not _NAME.match(value):
        raise ValueError(f"{label} invalide (lettres, chiffres, . _ - ) : {value!r}")
    return value


def _quote(value: str, label: str = "Texte") -> str:
    """Chaîne RouterOS entre guillemets, caractères spéciaux échappés."""
    if any(ord(c) < 32 for c in value):
        raise ValueError(f"{label} : caractères de contrôle interdits")
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("$", "\\$")
    return f'"{escaped}"'


# --- Blocs de configuration ---

def wifi_block(ssid: str, key: str, interface1="wlan1", interface2="wlan2"):
    """
    Génère un bloc de configuration Wi-Fi pour deux interfaces.
    """
    if len(key) < 8:
        raise ValueError("La clé Wi-Fi doit faire au moins 8 caractères")
    ssid_q, key_q = _quote(ssid, "SSID"), _quote(key, "Clé Wi-Fi")
    i1, i2 = _name(interface1, "Interface"), _name(interface2, "Interface")
    return (
        f'/interface wireless set {i1} ssid={ssid_q} hide-ssid=yes\n'
        f'/interface wireless security-profiles set [find default=yes] wpa2-pre-shared-key={key_q}\n'
        f'/interface wireless enable {i1}\n'
        f'/interface wireless set {i2} ssid={ssid_q} hide-ssid=yes\n'
        f'/interface wireless enable {i2}\n'
    )


def nat_block(to_ip: str, to_port: int, src_address: str, dst_port: int, protocol="tcp"):
    """
    Génère un bloc NAT simple.
    """
    return (
        f"/ip firewall nat add chain=dstnat action=dst-nat to-addresses={_ip(to_ip)} "
        f"to-ports={_port(to_port)} protocol={_proto(protocol)} "
        f"src-address={_ip(src_address, 'IP source')} dst-port={_port(dst_port)}\n"
    )


def vlan_block(vlan_id: int, interface: str, ip_network: str):
    """
    Génère un bloc VLAN simple.
    """
    try:
        vid = int(vlan_id)
    except (TypeError, ValueError):
        raise ValueError(f"VLAN invalide : {vlan_id!r}") from None
    if not 1 <= vid <= 4094:
        raise ValueError(f"VLAN hors plage (1-4094) : {vid}")
    return (
        f"/interface vlan add name=vlan{vid} vlan-id={vid} interface={_name(interface, 'Interface')}\n"
        f"/ip address add address={_network(ip_network)} interface=vlan{vid}\n"
    )


def lan_block(port_ether: str, ip: str, mask: str, dhcp_start: str, dhcp_end: str):
    """
    Génère un LAN sur un port Ethernet avec serveur DHCP.
    """
    eth = _ether(port_ether)
    iface = ipaddress.IPv4Interface(f"{_ip(ip)}/{_prefix(mask)}")
    start, end = ipaddress.IPv4Address(_ip(dhcp_start, "DHCP début")), ipaddress.IPv4Address(_ip(dhcp_end, "DHCP fin"))
    if start > end:
        raise ValueError("DHCP début doit précéder DHCP fin")
    if start not in iface.network or end not in iface.network:
        raise ValueError(f"La plage DHCP doit être dans {iface.network}")
    return (
        f"/interface bridge port remove [find interface=ether{eth}]\n"
        f"/ip address add address={iface} interface=ether{eth}\n"
        f"/ip pool add name=pool_ether{eth} ranges={start}-{end}\n"
        f"/ip dhcp-server add name=dhcp_ether{eth} interface=ether{eth} address-pool=pool_ether{eth} disabled=no\n"
        f"/ip dhcp-server network add address={iface.network} gateway={iface.ip}\n"
    )


def port_forward_block(to_ip: str, lan_port, protocol: str, wan_ip: str, wan_port):
    """
    Génère une redirection de port (dst-nat). L'IP WAN est optionnelle.
    """
    dst = f" dst-address={_ip(wan_ip, 'IP WAN')}" if wan_ip.strip() else ""
    return (
        f"/ip firewall nat add chain=dstnat action=dst-nat to-addresses={_ip(to_ip, 'Adresse LAN')} "
        f"to-ports={_port(lan_port, 'Port LAN')} protocol={_proto(protocol)}{dst} "
        f"dst-port={_port(wan_port, 'Port WAN')}\n"
    )


def ajout_port_ip_router(ip_routee: str, ip_nat: str, portEther: str,
                         wan_interface: str = WAN_INTERFACE,
                         reset_srcnat: bool = False,
                         disable_filter_rule: int | None = None):
    """
    Génère un bloc de configuration pour ajouter un port IP Mikrotik
    avec IP routée, IP NAT et port Ethernet.

    Les actions destructrices sont désormais opt-in :
    - reset_srcnat : supprime TOUTES les règles srcnat existantes ;
    - disable_filter_rule : désactive la règle de filtrage portant ce numéro.
    """
    ip_r = ipaddress.IPv4Address(_ip(ip_routee, "IP routée"))
    ip_n = _ip(ip_nat, "IP NAT")
    eth = _ether(portEther)
    wan = _name(wan_interface, "Interface WAN")
    base = ".".join(str(ip_r).split(".")[:3])

    lines = [
        f"/interface bridge port remove [find interface=ether{eth}]",
        f"/interface ethernet set ether{eth} arp=proxy-arp",
        "/ip address",
        f"add address={base}.254/24 interface=ether{eth}",
        ':foreach i in=[/ip address find where interface=bridge] do={:local a [/ip address get $i address]; :global mask  [:pick $a ([:find $a "/"]) [:len $a]]}',
        ":global netaddr [/ip address get [find interface=bridge] network ]",
        '/ip service set [find] address=([get winbox address] , "$netaddr$mask")',
        "/ip route",
        f"add distance=1 dst-address={ip_r}/32 gateway=ether{eth}",
        f"add distance=1 dst-address={base}.0/25 gateway={wan}",
        f"add distance=1 dst-address={base}.128/25 gateway={wan}",
    ]
    if disable_filter_rule is not None:
        lines.append(f"/ip firewall filter set numbers={int(disable_filter_rule)} disabled=yes")
    if reset_srcnat:
        lines.append("/ip firewall nat remove [find chain=srcnat]")
    lines += [
        f'/ip firewall nat add action=src-nat chain=srcnat to-addresses={ip_n} out-interface={wan} src-address=!{ip_r} comment="masquerade"',
        f'/ip service set [find] address=([get winbox address] , "{ip_r}")',
    ]
    return "\n" + "\n".join(lines) + "\n"
