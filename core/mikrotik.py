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


def ajout_port_ip_router(ip_routee: str, ip_nat: str, portEther: str):
    """
    Génère un bloc de configuration pour ajouter un port IP Mikrotik
    avec IP routée, IP NAT et port Ethernet.
    """
    # On découpe l’IP routée en 4 octets
    ip_parts = ip_routee.split(".")
    ip_1_1, ip_2_1, ip_3_1, ip_4_1 = ip_parts

    # On découpe l’IP NAT en 4 octets
    ip_nat_parts = ip_nat.split(".")
    ip_1_2, ip_2_2, ip_3_2, ip_4_2 = ip_nat_parts

    return f"""
/interface bridge port remove [find interface=ether{portEther}]
/interface ethernet set ether{portEther} arp=proxy-arp
/ip address
add address={ip_1_1}.{ip_2_1}.{ip_3_1}.254/24 interface=ether{portEther}
:foreach i in=[/ip address find where interface=bridge] do={{:local a [/ip address get $i address]; :global mask  [:pick $a ([:find $a "/"]) [:len $a]]}}
:global netaddr [/ip address get [find interface=bridge] network ]
/ip service set [find] address=([get winbox address] , "$netaddr$mask")
/ip route
add distance=1 dst-address={ip_1_1}.{ip_2_1}.{ip_3_1}.{ip_4_1}/32 gateway=ether{portEther}
add distance=1 dst-address={ip_1_1}.{ip_2_1}.{ip_3_1}.0/25 gateway=pppoe-out1
add distance=1 dst-address={ip_1_1}.{ip_2_1}.{ip_3_1}.128/25 gateway=pppoe-out1
/ip firewall filter set numbers=6 disabled=yes
/ip firewall nat remove [find chain=srcnat]
/ip firewall nat add action=src-nat chain=srcnat to-addresses={ip_1_2}.{ip_2_2}.{ip_3_2}.{ip_4_2} out-interface=pppoe-out1 src-address=!{ip_1_1}.{ip_2_1}.{ip_3_1}.{ip_4_1} comment="masquerade"
/ip service set [find] address=([get winbox address] , "{ip_1_1}.{ip_2_1}.{ip_3_1}.{ip_4_1}")
"""
