import pytest

from core import mikrotik as m


def test_wifi_escapes_quotes_and_dollar():
    out = m.wifi_block('Mon"SSID', 'pa$$word!1')
    assert 'ssid="Mon\\"SSID"' in out
    assert 'pa\\$\\$word!1' in out


def test_wifi_rejects_newline_and_short_key():
    with pytest.raises(ValueError):
        m.wifi_block("a\n/system reset-configuration", "longkey123")
    with pytest.raises(ValueError):
        m.wifi_block("ssid", "short")


@pytest.mark.parametrize("ip", ["1.2.3", "1.2.3.4.5", "a.b.c.d", "", "300.1.1.1", "1.2.3.4; /x"])
def test_router_ip_invalid(ip):
    with pytest.raises(ValueError):
        m.ajout_port_ip_router(ip, "10.0.0.1", "3")


def test_router_ip_ok_and_destructive_actions_opt_in():
    out = m.ajout_port_ip_router("203.0.113.10", "198.51.100.5", "3")
    assert "203.0.113.10/32 gateway=ether3" in out
    assert "203.0.113.254/24" in out
    assert "nat remove" not in out and "filter set" not in out
    out = m.ajout_port_ip_router("203.0.113.10", "198.51.100.5", "3",
                                 reset_srcnat=True, disable_filter_rule=6)
    assert "nat remove [find chain=srcnat]" in out
    assert "numbers=6 disabled=yes" in out


def test_router_ether_must_be_number():
    with pytest.raises(ValueError):
        m.ajout_port_ip_router("203.0.113.10", "198.51.100.5", "3 ; /x")


def test_lan_block():
    out = m.lan_block("2", "192.168.10.1", "255.255.255.0", "192.168.10.10", "192.168.10.99")
    assert "address=192.168.10.1/24 interface=ether2" in out
    assert "ranges=192.168.10.10-192.168.10.99" in out
    assert "network add address=192.168.10.0/24 gateway=192.168.10.1" in out


def test_lan_dhcp_outside_network():
    with pytest.raises(ValueError):
        m.lan_block("2", "192.168.10.1", "24", "192.168.11.10", "192.168.11.20")


def test_port_forward_optional_wan_ip():
    out = m.port_forward_block("192.168.1.5", "80", "TCP", "", "8080")
    assert "dst-address" not in out and "dst-port=8080" in out
    assert "dst-address=1.2.3.4" in m.port_forward_block("192.168.1.5", "80", "udp", "1.2.3.4", "8080")


def test_port_forward_invalid():
    for args in [("192.168.1.5", "0", "tcp", "", "80"), ("192.168.1.5", "80", "icmp", "", "80"),
                 ("x", "80", "tcp", "", "80"), ("192.168.1.5", "80", "tcp", "", "70000")]:
        with pytest.raises(ValueError):
            m.port_forward_block(*args)


def test_vlan_range():
    assert "vlan-id=10" in m.vlan_block(10, "ether1", "10.0.0.1/24")
    with pytest.raises(ValueError):
        m.vlan_block(5000, "ether1", "10.0.0.1/24")
